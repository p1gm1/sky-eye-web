# Rasterio
import rasterio

# Data
import numpy as np
import pandas as pd

# Torch
import torch
import torchvision.transforms as transforms

# pytorch-lighting
import pytorch_lightning as pl

# omegaconf
from omegaconf import OmegaConf, DictConfig

# Local
from pathlib import Path
import collections
import importlib
from typing import Any
import random


class LitImg(pl.LightningModule):

    def __init__(self, 
                 hparams: DictConfig = None, 
                 cfg: DictConfig = None, 
                 model = None):
        super(LitImg, self).__init__()
        self.cfg = cfg
        self.hparams = hparams
        self.model = model

    def forward(self, x, *args, **kwargs):
        return self.model(x)

    def configure_optimizers(self):
        if 'decoder_lr' in self.cfg.optimizer.params.keys():
            params = [
                {'params': self.model.decoder.parameters(), 'lr': self.cfg.optimizer.params.lr},
                {'params': self.model.encoder.parameters(), 'lr': self.cfg.optimizer.params.decoder_lr},
            ]
            optimizer = load_obj(self.cfg.optimizer.class_name)(params)

        else:
            optimizer = load_obj(self.cfg.optimizer.class_name)(self.model.parameters(), **self.cfg.optimizer.params)
        scheduler = load_obj(self.cfg.scheduler.class_name)(optimizer, **self.cfg.scheduler.params)

        return [optimizer], [{"scheduler": scheduler,
                              "interval": self.cfg.scheduler.step,
                              'monitor': self.cfg.scheduler.monitor}]


def load_obj(obj_path: str, default_obj_path: str = "") -> Any:
    """Extract an object from a given path.
        Args:
            obj_path: Path to an object to be extracted, 
            including the object name.
            default_obj_path: Default object path.
        Returns:
            Extracted object.
        Raises:
            AttributeError: When the object does not have 
            the given named attribute.
    """

    obj_path_list = obj_path.rsplit(".", 1)
    obj_path = obj_path_list.pop(0) if len(obj_path_list) > 1 else default_obj_path  
    obj_name = obj_path_list[0]
    module_obj = importlib.import_module(obj_path)
    
    if not hasattr(module_obj, obj_name):
        raise AttributeError(
            f"Object `{obj_name}` cannot be loaded from `{obj_path}`."
        )
    
    return getattr(module_obj, obj_name)


def make_ndvi(band_NIR, band_red, im):
    ndvi_lower = band_NIR.astype(float) - band_red.astype(float)
    ndvi_upper = band_NIR.astype(float) + band_red.astype(float)

    ndvi = ndvi_upper / ndvi_lower

    kwargs = im.meta
    kwargs.update(
        dtype=rasterio.uint8,
        count=1,
        compress='lzw'
    )

    nds = rasterio.open('ndvi.tif', 'w', **kwargs).write_band(1, ndvi.astype(rasterio.uint8))

    return nds


def get_cfg():
    """Get cfg object, with the preloaded
    configs.
    """

    cfg =  {'logging': {'log': True},
                        'data': { 'num_workers': 0, 
                        'batch_size': 12}}

    return OmegaConf.create(cfg)


def flatten_omegaconf(d, sep="_"):
    """Unroll the omegaconf."""
    d = OmegaConf.to_container(d)

    obj = collections.OrderedDict()

    def recurse(t, parent_key=""):

        if isinstance(t, list):
            for i in range(len(t)):
                for i in range(len(t)):
                    recurse(t[i], parent_key+sep+str(i) if parent_key else str(i))
        elif isinstance(t, dict):
            for k, v in t.items():
                recurse(v, parent_key + sep + k if parent_key else k)
        else:
            obj[parent_key] = t 
    
    recurse(d)

    obj = {k: v for k, v in obj.items() if type(v) in [int, float]}

    return obj


def eval_model(image,
               detection_threshold,
               device,
               lit_model,
               results=[]):
    """Evaluates an image on
    the model.
    """
    transform = transforms.ToTensor() 
    image = transform(image)

    images = [image,]
    outputs = lit_model(images)

    for i, image in enumerate(images):

        boxes=outputs[i]['boxes'].data.cpu().numpy()
        scores=outputs[i]['scores'].data.cpu().numpy()

        boxes=boxes[scores >= detection_threshold].astype(np.int32)
        scores=scores[scores >= detection_threshold]

        for s, b in zip(scores, boxes.astype(int)):
            result = {
               'x': b[0] + (b[2] - b[0])/2,
               'y': b[1] + (b[3] - b[1])/2
            }

            results.append(result)

    return results


def count_crops(image_url):

    WIDTH=3648
    HEIGHT=4864

    cfg = get_cfg()
    
    crops=[]

    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    model=torch.load(str(Path(__file__).resolve(strict=True).parent.parent)+'/static/model.pth',
                     map_location=device)

    detection_threshold=0.0

    hparams = flatten_omegaconf(cfg)

    with rasterio.open(str(Path(__file__).resolve(strict=True).parent.parent)+image_url) as src:
        for col in range(0, src.width, WIDTH):
            for row in range(0, src.height, HEIGHT):
                window=rasterio.windows.Window(col_off=col,
                                               row_off=row,
                                               width=WIDTH,
                                               height=HEIGHT)
                
                r,g,b,_ = src.read(window=window)

                total = [band for band in [r,g,b]]

                image = np.array(total).T.astype(np.float32)

                image /= 255.0

                model.eval()

                lit_model = LitImg(hparams=hparams,
                                   cfg=cfg,
                                   model=model)

                res = eval_model(image,
                                  detection_threshold,
                                  device,
                                  lit_model)

                for i in range(len(res)):
                    res[i]['x'] += row
                    res[i]['y'] += col

                crops += res
    
    crops_url = str(Path(__file__).resolve(strict=True).parent.parent)+f"/media/ortophoto/reports/csv_{random.randint(0, 100)}.csv"

    crops_pd = pd.DataFrame(crops, columns=["x", "y"])
    crops_pd.to_csv(crops_url, index=False)            

    return crops_url, len(crops)     
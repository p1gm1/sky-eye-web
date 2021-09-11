# pytest
import pytest
import unittest

# reasterio
import rasterio

# Data
import numpy as np

pytestmark = pytest.mark.django_db

def test_ndvi():
    band_NIR = np.empty([300, 300], dtype=rasterio.uint16)
    band_red = np.empty([300, 300], dtype=rasterio.uint16)
    ndvi_lower = band_NIR.astype(float) - band_red.astype(float)
    ndvi_upper = band_NIR.astype(float) + band_red.astype(float)

    assertions = unittest.TestCase('__init__')

    ndvi = ndvi_upper / ndvi_lower

    assertions.assertIsNotNone(ndvi)
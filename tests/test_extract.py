import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from line_scan import extract, sample

class ExtractionTests(unittest.TestCase):
    def test_large_intensities_preserve_centroid(self):
        image=np.zeros((10,2));image[5,:]=1
        center,valid=extract(image*1e307)
        np.testing.assert_allclose(center,[5,5])
        self.assertTrue(valid.all())
    def test_blank_and_synthetic(self):
        center,valid=extract(np.zeros((4,4)))
        self.assertFalse(valid.any())
        self.assertTrue(np.isnan(center).all())
        image,truth=sample();center,valid=extract(image)
        self.assertLess(np.sqrt(np.mean((center[valid]-truth[valid])**2)),.2)

import ast
import contextlib
import io
import json
import os
from pathlib import Path
import sys
import unittest

os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '2')

import numpy as np
from scipy import ndimage as ndi
from astropy.time import Time

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / 'scripts'))
from synthetic_smoke import sources, execute, run


def function(name, source, namespace):
    tree = ast.parse(source)
    nodes = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    if len(nodes) != 1:
        raise ValueError(f'Cannot isolate {name}')
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<actual-notebook-function>', 'exec'), namespace)
    return namespace[name]


class ProcessingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cell = sources()

    def test_notebook_has_valid_python_and_no_outputs_or_local_paths(self):
        raw = (REPO / 'notebooks/gdl_radiography.ipynb').read_text()
        notebook = json.loads(raw)
        for cell in notebook['cells']:
            if cell['cell_type'] == 'code':
                ast.parse(''.join(cell['source']))
                self.assertEqual(cell['outputs'], [])
                self.assertIsNone(cell['execution_count'])
        self.assertNotIn('000000000_Yong_Fuel_Cell', raw)

    def test_bright_and_dark_outliers_only_are_replaced(self):
        ns = dict(np=np, ndi=ndi, SPIKE_WINDOW=3, SPIKE_SIGMA=2,
                  SPIKE_MAX_AREA=1, SPIKE_ABSOLUTE_FLOOR=0., ENABLE_DESPIKE=True)
        clean = function('despike', self.cell[9], ns)
        a = np.full((15, 15), 20., np.float32)
        a[4, 4] = 100
        a[10, 10] = 0
        a[0, 0] = np.nan
        b, mask = clean(a)
        self.assertEqual(int(mask.sum()), 2)
        self.assertEqual(b[4, 4], 20)
        self.assertEqual(b[10, 10], 20)
        self.assertTrue(np.isnan(b[0, 0]))
        np.testing.assert_array_equal(a[~mask], b[~mask])

    def test_large_components_are_not_spot_replaced(self):
        ns = dict(np=np, ndi=ndi, SPIKE_WINDOW=7, SPIKE_SIGMA=2,
                  SPIKE_MAX_AREA=1, SPIKE_ABSOLUTE_FLOOR=0., ENABLE_DESPIKE=True)
        clean = function('despike', self.cell[9], ns)
        a = np.full((20, 20), 20., np.float32)
        a[8:10, 8:10] = 100
        b, mask = clean(a)
        self.assertFalse(mask.any())
        np.testing.assert_array_equal(a, b)

    def test_exact_fast_median_and_despike_match_reference(self):
        ns = dict(np=np, ndi=ndi, SPIKE_WINDOW=7, SPIKE_SIGMA=2,
                  SPIKE_MAX_AREA=300, SPIKE_ABSOLUTE_FLOOR=0., ENABLE_DESPIKE=True)
        reference = function('despike', self.cell[9], ns)
        reference_fn = reference
        # Execute only the setup, before any file calibration, from the actual cell.
        prefix = self.cell[12].split('# REPLACEMENT CELL 1')[0]
        with contextlib.redirect_stdout(io.StringIO()):
            execute(prefix, ns, {'CPU_THREADS': 1})
        rng = np.random.default_rng(1729)
        for array in [rng.integers(0, 65536, (17, 23)).astype(np.float32),
                      rng.normal(20, 0.7, (17, 23)).astype(np.float32)]:
            np.testing.assert_array_equal(ns['fast_median_exact'](array, 7), ndi.median_filter(array, size=7, mode='reflect'))
            expected, expected_mask = reference_fn(array)
            actual, actual_mask = ns['despike'](array)
            np.testing.assert_array_equal(actual_mask, expected_mask)
            np.testing.assert_array_equal(actual, expected)

    def test_timestamp_uses_date_proxy_without_midpoint_shift(self):
        ns = dict(np=np, Time=Time, TIME_KEY='DATE', TIME_FORMAT='isot',
                  TIME_SCALE_DEFAULT='utc', EXPOSURE_KEY='EXPTIME')
        f = function('timestamp_record', self.cell[5], ns)
        r = f({'DATE': '2026-07-20T12:00:00', 'EXPTIME': 5., 'TIMESYS': 'UTC'})
        self.assertEqual(r['time_position'], 'file_creation')
        self.assertIsNone(r['start_utc'])
        self.assertEqual(r['timestamp_utc'], '2026-07-20T12:00:00.000000000')
        missing = f({'DATE': '2026-07-20T12:00:00'})
        self.assertTrue(missing['exposure_missing'])
        self.assertTrue(missing['time_scale_assumed'])
        with self.assertRaises(ValueError):
            f({'EXPTIME': 5})

    def test_rotation_masks_padding_and_preserves_zero_angle(self):
        ns = dict(np=np, ndi=ndi)
        rotate = function('rotate_image', self.cell[19], ns)
        a = np.ones((32, 32), np.float32)
        a[15, 15] = np.nan
        np.testing.assert_array_equal(rotate(a, 0), a)
        result = rotate(a, 7)
        self.assertTrue(np.isnan(result).any())
        np.testing.assert_allclose(result[np.isfinite(result)], 1)

    def test_actual_bm3d_restores_invalid_mask(self):
        ns = dict(np=np, ndi=ndi, ENABLE_BM3D=True, BM3D_SIGMA=0.3)
        denoise = function('denoise', self.cell[16], ns)
        a = np.full((48, 48), .6, np.float32)
        a[0, :3] = np.nan
        result = denoise(a)
        self.assertEqual(result.dtype, np.float32)
        np.testing.assert_array_equal(np.isnan(result), np.isnan(a))
        self.assertTrue(np.isfinite(result[1:]).all())

    def test_fits_to_saturation_exports_and_arithmetic(self):
        report = run()
        self.assertTrue(report['negative_values_retained'])
        self.assertTrue(report['above_100_values_retained'])
        self.assertTrue(report['float32_tiff_metadata_and_csv_checked'])


if __name__ == '__main__':
    unittest.main()

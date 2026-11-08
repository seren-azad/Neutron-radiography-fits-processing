"""Exercise the packaged notebook on small synthetic FITS images, not beamtime data."""
import ast
import contextlib
import io
import json
import os
from pathlib import Path
import tempfile

os.environ.setdefault('MPLBACKEND', 'Agg')
os.environ.setdefault('OMP_NUM_THREADS', '1')
os.environ.setdefault('OPENBLAS_NUM_THREADS', '1')
os.environ.setdefault('NUMBA_NUM_THREADS', '2')

import numpy as np
from astropy.io import fits
from astropy.time import Time, TimeDelta

REPO = Path(__file__).resolve().parents[1]
NOTEBOOK = REPO / 'notebooks/gdl_radiography.ipynb'


def sources():
    notebook = json.loads(NOTEBOOK.read_text())
    return {int(c['id'].rsplit('-', 1)[1]): ''.join(c['source'])
            for c in notebook['cells'] if c['cell_type'] == 'code'}


def execute(source, namespace, overrides=None):
    """Override only top-level configuration assignments in the synthetic test."""
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name) and target.id in (overrides or {}):
                node.value = ast.parse(repr(overrides[target.id]), mode='eval').body
    exec(compile(ast.fix_missing_locations(tree), '<synthetic-notebook-cell>', 'exec'), namespace)


def run():
    import matplotlib.pyplot as plt
    import pandas as pd
    import tifffile
    cell = sources()
    with tempfile.TemporaryDirectory(prefix='gdl_synthetic_') as directory:
        base = Path(directory)
        raw_dir = base / 'raw'
        raw_dir.mkdir()
        shape = (64, 64)
        # Small but nonzero fixed-pattern detector variations.
        yy, xx = np.indices(shape)
        dc = np.full(shape, 100.0, np.float32)
        effective = (1000 + xx * 0.25 + yy * 0.1).astype(np.float32)
        header = fits.Header({'EXPTIME': 5.0, 'TIMESYS': 'UTC'})
        fits.writeto(raw_dir / 'reference_dc_0001.fits', dc, header)
        fits.writeto(raw_dir / 'reference_ob_0001.fits', dc + effective, header)
        expected = []
        for i, value in enumerate([0.0, 0.05, 0.15, -0.02]):
            attenuation = np.zeros(shape, np.float64)
            attenuation[8:56, 8:56] = 0.2 + value
            if i == 2:
                attenuation[30, 30] += 0.3
            expected.append(attenuation[16:48, 16:48] - 0.2)
            counts = dc + effective * np.exp(-attenuation)
            h = header.copy()
            h['DATE'] = (Time('2026-07-20T12:00:00', scale='utc') + TimeDelta(7*i, format='sec')).isot
            fits.writeto(raw_dir / f'sample_Proj_{i+1:04d}.fits', counts.astype(np.float32), h)
        env = {'GDL_INPUT_DIR': str(raw_dir), 'GDL_OUTPUT_DIR': str(base / 'outputs')}
        previous = {key: os.environ.get(key) for key in env}
        os.environ.update(env)
        ns = {'__name__': '__gdl_synthetic__'}
        log = io.StringIO()
        try:
            with contextlib.redirect_stdout(log):
                execute(cell[2], ns)
                ns['display'] = lambda *args, **kwargs: None
                for index in [4, 5, 7]:
                    execute(cell[index], ns)
                # TIFF/CSV exports run normally. Expensive publication figures are
                # closed instead of rendered during the small arithmetic check.
                ns['savefig'] = lambda fig, name: plt.close(fig)
                execute(cell[9], ns, {'ENABLE_DESPIKE': False})
                execute(cell[11], ns, {'DOSE_ROI': (0, 8, 0, 64), 'CROP_BOX': (8, 56, 8, 56)})
                execute(cell[12], ns, {'APPROVE_NORMALIZATION': True, 'CPU_THREADS': 1})
                execute(cell[13], ns, {'PRINT_EVERY': 10, 'TIFF_WRITERS': 1})
                execute(cell[16], ns, {'ENABLE_BM3D': False})
                execute(cell[17], ns, {'APPROVE_BM3D': True})
                execute(cell[19], ns, {'ROTATION_DEG': 0.0})
                execute(cell[20], ns, {'APPROVE_ROTATION': True})
                execute(cell[22], ns, {'GDL_ROI': (8, 40, 8, 40)})
                execute(cell[23], ns, {'APPROVE_GDL_ROI': True})
                execute(cell[25], ns)
                execute(cell[27], ns)
                execute(cell[29], ns)
                execute(cell[30], ns, {'APPROVE_SATURATION_REFERENCE': True, 'IMAGE_INDEX': 1})
            delta = np.array(ns['delta'])
            saturation = np.array(ns['saturation'])
            expected = np.array(expected)
            np.testing.assert_allclose(delta, expected, atol=8e-7)
            np.testing.assert_allclose(ns['manifest']['elapsed_s'], [0, 7, 14, 21], atol=1e-6)
            # The peak is one 0.45 pixel and eight 0.15 pixels: neighbourhood mean 0.18333...
            expected_peak = (0.45 + 8*0.15) / 9
            np.testing.assert_allclose(ns['OBSERVED_MAX'], expected_peak, atol=8e-7)
            np.testing.assert_allclose(saturation, 100 * expected / expected_peak, atol=0.001)
            assert np.min(saturation) < 0 and np.max(saturation) > 100
            path = ns['RUN'] / '10_relative_saturation' / 'proj_000003.tif'
            with tifffile.TiffFile(path) as f:
                assert f.asarray().dtype == np.float32
                meta = json.loads(f.pages[0].description)
                assert meta['details']['clipped'] is False
            history = pd.read_csv(ns['RUN'] / 'saturation_time_history.csv')
            assert len(history) == 4  # Reference remains exported.
            np.testing.assert_allclose(history['sd'], np.std(saturation, axis=(1, 2)), atol=1e-5)
            assert (ns['RUN'] / 'common_valid_ROI_mask.tif').exists()
            assert len(list((ns['RUN'] / 'original_headers' / 'projections').glob('*.txt'))) == 4
            report = {'synthetic_frames': 4, 'frame_shape': list(shape), 'roi_shape': [32, 32],
                      'elapsed_s': [0, 7, 14, 21], 'observed_reference': float(ns['OBSERVED_MAX']),
                      'negative_values_retained': True, 'above_100_values_retained': True,
                      'float32_tiff_metadata_and_csv_checked': True,
                      'filtering_in_arithmetic_smoke': 'disabled; filtering tested separately',
                      'experimental_validation': False}
            return report
        finally:
            plt.close('all')
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value


if __name__ == '__main__':
    print(json.dumps(run(), indent=2))

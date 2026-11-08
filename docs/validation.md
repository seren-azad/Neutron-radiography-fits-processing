# Validation of this publication package

All eight automated checks passed in the packaging environment. These checks exercise actual functions extracted from the packaged notebook, rather than a separately rewritten processing implementation.

1. Every code cell parses as Python; stored outputs/execution counts and the original workstation path are absent.
2. Isolated bright and dark outliers are replaced; other values and invalid pixels are preserved.
3. Connected candidate components larger than the configured maximum area are retained.
4. Accelerated integer/floating-point median results and accelerated despiking match the reference SciPy implementation on synthetic arrays.
5. FITS DATE timestamps remain file-creation proxies without a half-exposure shift; missing fields and metadata flags are checked.
6. Rotation preserves a zero-angle image and excludes invalid interpolation/padding regions.
7. The actual BM3D package runs with the retained sigma of 0.3 on a small image and restores invalid pixels.
8. Four synthetic 64 x 64 FITS frames run through the notebook's normalization, crop, reference subtraction, peak search and relative-saturation export. Expected attenuation differences, elapsed times, neighbourhood maximum, signed values, values above 100%, float32 TIFF metadata, CSV SDs, common mask and archived FITS headers are checked.

The arithmetic workflow check disables despiking, BM3D and rotation so that the expected analytic attenuation field is preserved; those operations are checked separately. Publication figures are closed without rendering in that test. Experimental FITS data were not available, so this is not an end-to-end validation on beamtime images or a confirmation of calibration, ROIs, timing semantics, filter suitability, sample alignment or physical saturation.

The synthetic input has 7 s frame spacing and a maximum 3 x 3 neighbourhood attenuation difference of approximately 0.18333338. That value is a synthetic test expectation, not an experimental result.

Run the checks with `python -m unittest discover -s tests -v`. Run the standalone synthetic arithmetic/export smoke check with `python scripts/synthetic_smoke.py`.

The accompanying Word document was rendered and its page images inspected for readable native Word equations, complete references and clean pagination. It is separate from this code repository.

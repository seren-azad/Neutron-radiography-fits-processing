# Time-resolved GDL neutron radiography

Notebook workflow for FITS radiographs acquired at ICON/SINQ: detector correction, dose normalization, image denoising, dry-reference subtraction, observed-maximum relative-saturation mapping, and spatial profiles.

The supplied scientific calculations are retained. This publication package removes stored notebook outputs and workstation paths, documents the parameters and interpretation, and adds synthetic checks. Experimental FITS images are not included.

## What relative saturation means

The exported quantity is `S_rel = 100 * delta_A / reference_delta_A`, with `delta_A = -ln(T_t) + ln(T_dry)`. By default, the reference is the greatest fully valid 3 by 3 pixel neighbourhood mean observed anywhere in one image series. It is an observed water-signal scale, **not a measured 100% pore-saturation state**. The optional independent scalar reference must be documented if used.

Values below zero and above 100 are retained in TIFF and CSV outputs. The map colour limits do not clip the data. Separate series normalized by separate observed maxima do not share an absolute water-content scale. The S3-only forced-flooding sequence may influence that series' reference; do not assume identical calibration across specimens.

## Contents

- `notebooks/gdl_radiography.ipynb`: cleaned, portable analysis notebook and independent saved-TIFF viewer.
- `docs/parameters.md`: exact source settings and coordinate conventions.
- `docs/methods.md`: manuscript Methods text and equations.
- `docs/references.bib`: scientific references.
- `docs/author_checks.md`: experimental details and publication checks.
- `docs/source_provenance.json`: source SHA-256, notebook cell mapping and packaging changes.
- `scripts/synthetic_smoke.py`, `tests/test_processing.py`: synthetic FITS workflow and regression checks.
- `requirements.txt`: direct dependency versions used for package validation, not a reconstruction of the original experiment's software environment.
- `requirements-notebook.txt`: notebook interface and analysis dependencies.

## Install

Python 3.12 is the validation environment. Create an isolated environment:

```bash
python -m venv .venv
# Linux/macOS:
source .venv/bin/activate
# Windows PowerShell alternative:
# .venv\Scripts\Activate.ps1
python -m pip install -r requirements-notebook.txt
jupyter lab notebooks/gdl_radiography.ipynb
```

Do not run the entire notebook unattended before reviewing the dataset-specific settings. The preview approval flags start at `False` and must be set to `True` after inspecting each corresponding preview.

## Input data

Place one experiment's images in `data/raw/`, or set `GDL_INPUT_DIR`. Set `GDL_OUTPUT_DIR` to choose an output location. The defaults are relative to the repository root, whether Jupyter opens in the root or in `notebooks/`.

| Input | Default glob | Example |
|---|---|---|
| Sample radiographs | `*Proj*.fits` | `sample_Proj_0001.fits` |
| Open beam | `*ob*.fits` | `reference_ob_0001.fits` |
| Dark current | `*dc*.fits` | `reference_dc_0001.fits` |

Glob patterns are case-sensitive on Linux. Groups must be nonempty and disjoint. Images must be 2D and share a shape. The configured FITS HDU is 0. Use matching exposure times for sample, open-beam and dark frames; the code does not convert unmatched exposures into compatible count rates.

Inspect the first FITS header before loading. The retained default is `TIME_KEY='DATE'`, parsed as ISO time, with `TIMESYS` used when present and UTC assumed otherwise. **FITS DATE is file creation time; this implementation treats it as an acquisition-time proxy.** It does not compute exposure start or midpoint. Missing `EXPTIME` is explicitly flagged; the stored zero placeholder is not a measured exposure. If the detector uses local clock time, convert it explicitly before treating it as UTC. No filesystem modification time is substituted.

## Run the analysis

1. Set input/output paths, file patterns, header settings and memory mode. Inspect names and timestamps.
2. Inspect the bright/dark outlier preview. Set the open-beam dose window and initial crop in original detector coordinates.
3. Approve normalization. The same outlier correction is applied to projections and calibration frames before calibration averaging.
4. Preview and approve BM3D. The source value is **0.3 transmission units**, not 0.3 percent and not 0.3/255. Inspect residual images before using it on experimental data.
5. Preview/approve a common rotation angle, then a fixed GDL ROI in rotated-crop coordinates. A common rotation is not time-dependent registration.
6. Calculate attenuation and dry-reference differences on the shared valid mask. Verify that projection 1 is an appropriate dry baseline.
7. Inspect the peak-neighbourhood diagnostics, approve the relative scale, then export relative saturation.
8. Use the independent final cell for maps, spatial mean/SD profiles and selected line profiles. After a full run it defaults to that run's saturation directory. In a fresh kernel, set `GDL_SATURATION_DIR` or replace `YOUR_RUN` explicitly; do not silently select an experiment.

Processing projection IDs and viewer `VIEW_PROJECTION` are one-based. The selected map `IMAGE_INDEX` is a zero-based array index (1 selects projection 2). The first reference frame is exported but omitted from the displayed relative-saturation time curve. All original rows remain in quantitative CSVs.

ROI tuples are `(x0, x1, y0, y1)` with exclusive upper bounds. Source ROIs are S3 examples, not universal bounds. Re-run all downstream stages after changing upstream settings. The peak temporal window is 1, so temporal median persistence filtering is disabled.

## Outputs and provenance

Each run is written under a new `run_YYYYMMDD_HHMMSS_microseconds` directory. Stages 01-10 contain float32 TIFFs, timestamp manifests and pixel statistics. The run also contains calibration averages, a common-mask TIFF, normalization QC, processing metadata, selected-patch diagnostics and software versions. `saturation_time_history.csv` contains the spatial mean and population SD plus fractions below zero and above 100. Original FITS headers are archived; source FITS files are not overwritten.

Mean +/- SD bands represent spatial variability, not independent replicates or uncertainty of the mean. The dry frame contributes shared noise across subsequent differences. Water-related attenuation is beam-path integrated: the pipeline does not reconstruct 3D water distribution, correct scattering/beam hardening, or automatically compensate sample drift/deformation or path-length changes.

The viewer uses lower-origin displays, while early processing previews use upper-origin displays. Exported array coordinates do not change. Physical axes require a verified sample-plane pixel size; the source has `PIXEL_SIZE_UM=None`. Do not reuse the pixel size from a different tomography setup.

## Memory

One float32 stack requires `4 * N * H * W` bytes. Several full and cropped stacks are retained. Select `STORAGE='memmap'` for disk-backed arrays when needed and allow space for both caches and TIFFs. Close the notebook and release memmaps before deleting caches.

## Validation

```bash
python -m unittest discover -s tests -v
python scripts/synthetic_smoke.py
```

Checks cover the actual notebook functions and a small synthetic FITS-to-TIFF workflow. They are not an experimental validation or calibration. See `docs/validation.md` for the completed checks and limitations.

## Upload to GitHub

Upload the contents of this directory as the repository root, retaining the `.github/` directory and `.gitignore`. Alternatively, initialize a local Git repository, add these files, commit and push to a repository you create. No remote repository has been created by this package.

Before a public release, review `docs/author_checks.md`, choose a code license with the rights holders, complete citation/release information, and add the actual repository URL or archived-release DOI to the manuscript. `CITATION.cff` supplies provisional software citation metadata without inventing a remote URL. Scientific references are listed in `docs/references.bib`.

## Rights and third-party software

No new redistribution license is assigned to the author's code by this packaging step; the rights holders should select one before licensing reuse. The notebook calls installed third-party packages but does not redistribute their source or binaries. In particular, BM3D has its own terms: consult the [official software page](https://webpages.tuni.fi/foi/GCF-BM3D/) for the intended use. See `LICENSE_NOTICE.md`.

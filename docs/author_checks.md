# Checks before manuscript submission and code release

## Acquisition details

- Confirm the sample-plane pixel size and actual field of view from this micro-setup's calibration. Neither is specified in the supplied notebook; do not import 32.3 micrometres from the separate wood-tomography experiment.
- Add camera model, collimation/aperture and sample-to-scintillator distance if required by the journal and supported by the experiment log. The Methods uses only the supplied CCD, 20 micrometre Gadox screen and 5 s exposure / approximately 2 s readout.
- Confirm projection, open-beam and dark-current integration times match, including cases where EXPTIME metadata are absent.

## Processing and interpretation

- Check actual run metadata against the retained S3 settings: 7 x 7 outlier window, threshold factor 2, maximum 300 pixels, BM3D sigma 0.3 transmission units, 1 degree rotation, 3 x 3 peak window and temporal window 1. ROI coordinates are specimen-specific.
- BM3D sigma 0.3 is the literal supplied value, equivalent to 30 percentage points of transmission. The package preserves it. Confirm it was the intended and executed noise parameter using before/after/residual images; no experimental validation of that value is claimed.
- DATE is used as a file-creation proxy. Confirm its relationship to exposure timing and the detector clock/time zone. TIME_IS and PLOT_TIME_AT in the original notebook were unused: packaging removes them but does not change timing arithmetic. A different TIME_KEY still receives the proxy labels in timestamp_record; revise labels and any midpoint arithmetic explicitly if changing timestamp semantics.
- Confirm the first chronological image is a dry baseline. A dry frame is an experimental state, not established by its ordering alone.
- Inspect the fraction of common valid pixels and any drift. A single fixed rotation does not register motion across frames.
- Relative saturation uses a per-series observed neighbourhood maximum. It is not a measured pore-volume saturation. Independent normalizations and S3-only forced flooding can affect comparisons among specimens. The definition must stay explicit in figures and conclusions.
- This notebook exports ROI histories and spatial profiles. It does not implement stage-boundary assignment, steady-state plateau selection, drainage event detection, t50/t90, RMS fluctuations, normalized through-plane coordinates, or water-side/gas-side fifths. Methods for those downstream results require the corresponding analysis code or a separate documented definition. The provided Methods does not invent these algorithms.
- Scattering, beam hardening, thickness variation and motion can affect quantitative attenuation differences; no automatic corrections for these effects appear in the notebook.

## Publication

- Add the actual public repository URL and, preferably, a tagged/archived release DOI to the code-availability statement once created. Nothing in this package claims that a public repository already exists.
- Review the provisional author list in CITATION.cff and add collaborators if appropriate.
- Select a source-code license with the rights holders. Review third-party package terms, including BM3D, separately. No third-party implementation is bundled.
- Preserve each run's processing metadata, timestamps, QC and software versions with its data. The package's validation dependencies describe the packaging test environment, not the original beamtime environment.

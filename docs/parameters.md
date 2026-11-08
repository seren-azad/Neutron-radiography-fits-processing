# Processing parameters

These values are retained from the supplied notebook. They document its configured S3 run; use the saved `processing.json` and TIFF metadata as the authority for other runs.

| Parameter | Retained value | Meaning |
|---|---|---|
| HDU | 0 | FITS primary image |
| Timestamp | DATE, isot | File-creation timestamp used as acquisition proxy |
| Default time scale | UTC | Used only when TIMESYS is absent; flagged in manifest |
| Exposure key | EXPTIME | Seconds; missing values flagged |
| Sort by timestamp | True | Stable chronological ordering |
| Dry reference | Projection 1 | First chronological projection |
| Effective pixel size | None | Unknown in the source; axes remain in pixels |
| Storage | ram | Optional memmap mode available |
| Outlier window | 7 x 7 pixels | Reflect boundary handling |
| Outlier threshold factor | 2 | Applied to maximum of local/global robust residual scales |
| Outlier component size | <=300 pixels | 8-connected components, bright and dark handled separately |
| Absolute residual floor | 0 detector counts | No additional absolute threshold |
| Dose ROI | (800,1000,1930,2000) | Original detector coordinates, stable open beam |
| Initial crop | (950,1170,300,2000) | Original detector coordinates |
| Denominator epsilon | 1e-6 x median positive OB-DC | Denominator <= epsilon becomes invalid |
| Minimum valid dose-window fraction | 0.9 | Reject frame below this threshold |
| Dose estimator | Median | Taken after flat-field correction |
| BM3D | Enabled, all stages | Independent filtering of each cropped transmission frame |
| BM3D sigma | 0.3 | Absolute transmission units; verify experimentally |
| Rotation | 1 degree | Common angle, bilinear, reshape=False |
| Rotated valid-weight cutoff | 0.99999 | Interpolation/padding values below threshold become NaN |
| GDL ROI | (103,120,465,1190) | Coordinates within the rotated initial crop |
| Minimum transmission | 0 | Require strictly positive T for the log |
| Common mask | Intersection over all frames | Same valid pixels used for time histories |
| Peak neighbourhood | 3 x 3 pixels | Whole patch must lie in valid search region |
| Peak temporal window | 1 frame | No temporal median persistence criterion |
| Peak search ROI | None | Full common-valid GDL ROI |
| Candidate support diagnostic | >=0.8 x patch mean | Reported, not an acceptance threshold |
| Stored top candidates | 20 | Diagnostic ranking |
| Saturation reference | None | Uses observed global neighbourhood maximum |
| Negative / >100% values | Retained | Display colour limits only |
| SD definition | ddof=0 | Spatial population SD |
| Profile band half-width | 0 pixels | Single row or column; may be increased |

The local robust scale is `1.4826 * median_filter(abs(I - median_filter(I)))`. The global floor is `1.4826 * median(abs(r - median(r)))` over finite residuals. Candidate components are kept only when their area is at most 300 pixels; only their pixels are replaced by the local median. This is not a full-image median replacement and is not a temporal filter.

The peak support fraction is diagnostic only. The code does not discard a candidate for low support. The scalar reference is searched independently for each run. A temporal window above 1 changes the peak score to a centred temporal median of local means and excludes incomplete edge windows; it does not smooth the exported image sequence.

ROI bounds use zero-based arrays and exclusive upper bounds: `(x0,x1,y0,y1)`. A dose ROI can lie outside the initial crop because dose normalization is applied first. Processing previews use upper origin; final map/profile figures use lower origin. These plotting choices do not flip the saved arrays.

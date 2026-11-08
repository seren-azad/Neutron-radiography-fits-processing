# Neutron radiography and image analysis

## 1 Neutron radiography acquisition

Time-resolved neutron radiography was performed at the ICON cold-neutron imaging beamline of the Swiss Spallation Neutron Source (SINQ), Paul Scherrer Institut, Villigen, Switzerland [1]. The micro imaging setup [2] used a CCD camera optically coupled to a 20 µm-thick Gadox scintillation screen. Each radiograph was acquired with a 5 s exposure followed by approximately 2 s of camera readout, giving a nominal frame interval of approximately 7 s. Each image therefore integrates the transmitted signal over 5 s; the readout interval is not an additional measurement of the evolving sample.

The GDL specimens were mounted in a two-phase transport cell and imaged during controlled water delivery and gas flow. The common protocol comprised prefill at 0.1 mL min⁻¹, primary invasion at water flow rates of 0.001, 0.01 and 0.1 mL min⁻¹ without gas flow, the same sequence of water flow rates under a 0.05 L min⁻¹ gas sweep, and a final dry-down under 0.5 L min⁻¹ air. The commercial carbon-paper specimen S3 additionally underwent forced flooding at water flow rates up to 5 mL min⁻¹. This additional sequence was distinguished from the common protocol when comparing specimens.

## 2 Image handling and temporal coordinates

Radiographs, open-beam images and dark-current images were read from FITS files as two-dimensional floating-point arrays. File groups were checked for overlap and consistent image dimensions, and projection images were ordered chronologically. The elapsed time of each radiograph was calculated relative to the first projection from the FITS DATE header. In this implementation, DATE was treated as a file-creation timestamp and used as an acquisition-time proxy, rather than an independently determined exposure-start or exposure-midpoint time [5]. The declared TIMESYS was respected where available; otherwise UTC was assumed and the assumption recorded. Exposure metadata, original filenames and original FITS headers were retained with the processed data. Actual timestamp differences, rather than frame number multiplied by the nominal interval, were used for the time histories.

## 3 Detector correction and dose normalization

Isolated bright and dark intensity outliers were removed before transmission normalization. A 7 × 7-pixel median filter with reflected boundaries supplied a local background estimate. Deviations from this background were compared with twice the larger of a local robust residual scale and a global residual-noise floor. The local scale was calculated as 1.4826 times the local median of the absolute residuals, and the global scale as 1.4826 times the median absolute deviation of the residuals about their global median. Positive and negative candidate pixels were grouped separately using eight-connectivity. Only connected components containing at most 300 pixels were replaced by their local median values; other finite pixels were retained. The same treatment was applied to the open-beam and dark-current images before computing their pixelwise finite-value means.

Let Pᶜₜ(p) denote the corrected sample counts at detector pixel p and time t, and let Ō(p) and D̄(p) denote the mean corrected open-beam and dark-current counts. The flat-field-corrected signal was calculated as

$$
F_t(p)=\frac{P_t^c(p)-\overline D(p)}{\overline O(p)-\overline D(p)+\epsilon}\tag{1}
$$

where ε was 10⁻⁶ times the median positive value of Ō − D̄. Pixels with nonfinite or insufficient open-beam signal (Ō − D̄ ≤ ε) were marked invalid. Sample and calibration images were required to have matching integration times; no count-rate rescaling for mismatched exposures was applied.

Frame-to-frame changes in incident intensity were corrected using a fixed dose-reference window D located in stable open beam outside the specimen and the wetting region:

$$
T_t(p)=\frac{F_t(p)}{\operatorname{median}_{q\in D}F_t(q)}\tag{2}
$$

The dose factor was the median finite flat-field signal in this window. A frame was rejected if fewer than 90% of the dose-window pixels were finite or if its dose factor was nonpositive or nonfinite. Dose normalization preceded cropping, allowing the reference window to lie outside the final analysis region. Dose factors and replaced-pixel fractions were retained for quality control.

## 4 Denoising and selection of a consistent analysis region

The normalized sequence was cropped to the region surrounding the GDL. Each cropped transmission image was then denoised independently using both stages of block-matching and three-dimensional collaborative filtering (BM3D) [3,4]. The noise standard-deviation parameter was 0.3 in absolute transmission units. No per-frame intensity rescaling was applied. Invalid pixels were temporarily filled from their nearest valid neighbours for denoising and subsequently restored to invalid values. Before-and-after images and removed-signal residuals were inspected to assess the denoising.

A common 1° rotation was applied to the image sequence using bilinear interpolation on a fixed-size canvas, after which a fixed rectangular GDL region of interest (ROI) was selected. Pixels affected by invalid interpolation support or padding were excluded. The same ROI geometry was used throughout each sequence. A common valid-pixel mask M was defined as the intersection of pixels having finite, strictly positive transmission in every frame. Subsequent quantitative time histories therefore compared the same pixels at all times. The common rotation aligned the image orientation but did not perform time-dependent registration or correct specimen drift.

## 5 Dry-reference subtraction and relative saturation

The first chronological radiograph was used as the dry reference. On the common valid mask, transmission was converted to dimensionless line-integrated attenuation, Aₜ(p) = −ln Tₜ(p). Water-related changes were isolated by subtracting the reference attenuation:

$$
\Delta A_t(p)=A_t(p)-A_0(p)=\ln\!\left[\frac{T_0(p)}{T_t(p)}\right]\tag{3}
$$

Positive ΔA indicates increased attenuation relative to the reference state. Nonpositive or invalid transmission values were excluded from the logarithm; transmissions greater than one and signed attenuation differences were retained. Because the measurements are radiographs, ΔA is integrated along the neutron beam path and is not a reconstructed local attenuation coefficient or three-dimensional water distribution.

A relative water-signal scale was established from the largest spatial-neighbourhood mean observed within each image series. The mean ΔA was evaluated in every fully valid 3 × 3-pixel neighbourhood contained in the GDL analysis region, and the maximum over neighbourhood centres and times was selected:

$$
\Delta A_{\mathrm{ref}}=\max_{t,p}\left[\frac{1}{9}\sum_{q\in N_{3\times3}(p)}\Delta A_t(q)\right]\tag{4}
$$

where N₃×₃(p) is the nine-pixel neighbourhood centred at p. No temporal median was applied to the neighbourhood scores (temporal window = 1 frame). Candidate locations, timestamps, patch variability and fixed-patch time histories were recorded and inspected before approving the scalar reference. Relative saturation was then defined as

$$
S_{\mathrm{rel}}(p,t)=100\frac{\Delta A_t(p)}{\Delta A_{\mathrm{ref}}}\quad(\%)\tag{5}
$$

The term relative saturation denotes this observed-maximum-normalized water signal, not an independently calibrated pore-volume saturation. In particular, the selected neighbourhood is not established to be fully water saturated. The scalar reference was kept fixed throughout each series, with no per-frame min–max normalization. Negative values and values above 100% were retained in quantitative outputs; only the map display range was limited to 0–100%. Individual pixels can exceed the selected neighbourhood mean and hence yield values above 100%. Comparisons between series with separately selected maxima describe relative dynamics and spatial patterns rather than a common absolute water-content scale. The additional S3 flooding sequence may influence that specimen’s observed maximum.

## 6 Spatial statistics and profiles

At each time point, the arithmetic mean relative saturation and its population standard deviation (normalization by N, not N − 1) were calculated over the N pixels of the common mask.

Mean ± SD bands describe spatial heterogeneity within the imaged ROI, rather than uncertainty of the mean or variability among independent specimens. The dry-reference frame was retained in the exported data but omitted from the displayed relative-saturation time-history curve. Selected saturation images were additionally summarized by row-wise and column-wise means and spatial SDs. Horizontal and vertical line profiles were extracted at specified pixel locations; the configured profile half-width was zero, corresponding to individual rows or columns. Profile values remained unclipped. Coordinates were retained in pixels unless a verified sample-plane pixel size was supplied.

## 7 Data preservation and scope of the analysis

Intermediate images and final maps were exported as 32-bit floating-point TIFF files, preserving fractional transmission, signed differences and invalid pixels as NaN. CSV files recorded timestamps, ROI statistics, normalization quality-control measures, reference-neighbourhood diagnostics and spatial profiles. Processing parameters were saved in JSON and TIFF metadata together with software-version information. The complete notebook, parameter documentation and environment specification accompany the analysis for release in the study’s code repository.

The analysis quantifies projected changes relative to the initial reference. Automatic corrections for time-dependent image registration, neutron scattering, beam hardening and changing beam-path thickness were not included. Accordingly, the reported quantity is interpreted as a relative water-related attenuation signal. A common dry reference also introduces correlated noise into subsequent differences. Absolute pore saturation would require an independently verified saturated calibration or an appropriate water-attenuation, path-length and porosity calibration.

## References

- [1] Kaestner, A. P., Hartmann, S., Kühne, G., Frei, G., Grünzweig, C., Josic, L., Schmid, F. and Lehmann, E. H. The ICON beamline – A facility for cold neutron imaging at SINQ. Nuclear Instruments and Methods in Physics Research Section A 659, 387–393 (2011). https://doi.org/10.1016/j.nima.2011.08.022
- [2] Lehmann, E. H., Frei, G., Kühne, G. and Boillat, P. The micro-setup for neutron imaging: A major step forward to improve the spatial resolution. Nuclear Instruments and Methods in Physics Research Section A 576, 389–396 (2007). https://doi.org/10.1016/j.nima.2007.03.017
- [3] Dabov, K., Foi, A., Katkovnik, V. and Egiazarian, K. Image denoising by sparse 3-D transform-domain collaborative filtering. IEEE Transactions on Image Processing 16, 2080–2095 (2007). https://doi.org/10.1109/TIP.2007.901238
- [4] Mäkinen, Y., Azzari, L. and Foi, A. Collaborative filtering of correlated noise: Exact transform-domain variance for improved shrinkage and patch matching. IEEE Transactions on Image Processing 29, 8339–8354 (2020). https://doi.org/10.1109/TIP.2020.3014721
- [5] IAU FITS Working Group. Definition of the Flexible Image Transport System (FITS), Version 4.0 (2016; language-edited edition 2018). https://fits.gsfc.nasa.gov/standard40/fits_standard40aa-le.pdf

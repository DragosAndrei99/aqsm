# Watermarked Carrier Attacks Reviewed From The AQSM Paper

This note reviews the attacks evaluated in `adaptive quantum scaling model.pdf` and cross-checks them against external image-processing and watermarking references. Online paper record: https://arxiv.org/abs/2502.18006.

## Scope

The paper evaluates two attacks on the watermarked carrier image:

1. Salt-and-pepper noise.
2. Cropping attack.

I did not find paper experiments for JPEG compression, Gaussian noise, filtering, resizing, rotation, translation, shearing, blur, histogram equalization, or collusion attacks. Those may be useful future tests, but they are not part of the paper's reported robustness section.

The paper reports robustness using the extracted watermark quality, mainly `PSNR` and `NCC`. This matches common watermarking practice: PSNR is widely used for image distortion/quality, and NC/NCC or BER are common similarity metrics between original and extracted watermark data. See the scikit-image metrics API and the watermarking robustness overview in the sources.

## Attack 1: Salt-And-Pepper Noise

### How It Works

Salt-and-pepper noise is impulse noise. A random subset of pixels is replaced by extreme values:

- "Salt": white/high pixels, usually `255` for an 8-bit grayscale image.
- "Pepper": black/low pixels, usually `0`.

In MATLAB, `imnoise(I, "salt & pepper", d)` applies salt-and-pepper noise to approximately `d * numel(I)` pixels. In scikit-image, `random_noise(..., mode="s&p", amount=d)` similarly replaces a proportion of pixels with high or low values, with `salt_vs_pepper=0.5` meaning equal salt and pepper by default. See MATLAB `imnoise` and scikit-image `random_noise` in the sources.

For this AQSM/HDWM algorithm, this attack is especially relevant because the watermark is embedded into low carrier bit planes. Setting a pixel to `0` or `255` overwrites not just the LSBs but also the carrier MSBs used to recompute `V_eta`, so the attack can damage both the embedded AQSM bits and the parity/XOR side of extraction.

### Paper Protocol

The paper applies salt-and-pepper noise to the watermarked carrier images and then extracts the watermark from the corrupted carrier.

Reported density sweep:

- `r = 1`, capacity `1/4`: densities `0.05`, `0.1`, `0.15`, `0.2`.
- `r = 2`, capacity `1/16`: densities `0.05`, `0.1`, `0.15`, `0.2`.
- `r = 3`, capacity `1/64`: densities `0.1`, `0.2`, `0.3`, `0.4`.

The paper states that only extracted-watermark results with `PSNR > 20 dB` are shown.

Reported average endpoint results:

| Scale | Lower Attack Level | Lower Result | Higher Attack Level | Higher Result |
|---|---:|---|---:|---|
| `r = 1` | density `0.05` | `PSNR = 32.06 dB`, `NCC = 0.9926` | density `0.2` | `PSNR = 22.44 dB`, `NCC = 0.9343` |
| `r = 2` | density `0.05` | `PSNR = 35.45 dB`, `NCC = 0.9963` | density `0.2` | `PSNR = 23.74 dB`, `NCC = 0.9481` |
| `r = 3` | density `0.1` | `PSNR = 61.20 dB`, `NCC = 0.9999` | density `0.4` | `PSNR = 21.72 dB`, `NCC = 0.9014` |

The paper also compares HDWM against direct LSB substitution under salt-and-pepper noise. It reports average extracted-watermark PSNR improvements from HDWM of `23.14%`, `14.42%`, and `1.25%` for `r = 1`, `r = 2`, and `r = 3`.

### Why The Paper Expects Resistance

The paper attributes resistance mainly to:

- AQSM spreading/scrambling watermark information across the carrier.
- Repetition in the AQSM construction.
- Quantum refining / majority voting during extraction.
- HDWM selecting an embedding/extraction rule based on watermark brightness distribution.

In practical terms, a single corrupted area or a random set of corrupted pixels may damage some AQSM copies, but repeated copies can still allow recovery if enough redundant copies remain correct.

### Pros As A Test Attack

- Simple to reproduce.
- Easy to parameterize by density.
- Directly stresses LSB watermarking because endpoint pixels overwrite the embedded low bits.
- Available in standard tools such as MATLAB and scikit-image.
- Good for testing randomized local corruption.

### Cons / Limitations

- Random results depend on seed and number of trials; the paper does not provide seeds.
- It is only one noise model. It does not test JPEG compression, Gaussian noise, blur, resizing, or filtering.
- It does not test synchronization problems like true crop-resize, rotation, translation, or scaling.
- High densities visibly degrade the image and may be less representative of normal sharing pipelines.
- For this implementation, if an attacked pixel damages a non-redundant extracted bit plane, majority voting may not correct it.

### Usability Notes For Our Repo

Use this as the first robustness notebook attack because it is easy and matches the paper directly.

Implementation choices to make explicit:

- Use 8-bit grayscale.
- Use a fixed random seed for reproducibility.
- Use equal salt/pepper probability unless deliberately testing an asymmetric case.
- Run multiple random trials per density and report mean/std, not just one run.
- Compare original watermark vs extracted watermark with pixel-difference rate, PSNR, and NCC.

## Attack 2: Cropping Attack

### How It Works

In watermarking literature, cropping is a geometric/desynchronization attack because it removes or occludes part of the image and can break the alignment between embedded watermark coordinates and the detector. Geometric attacks are generally hard for watermarking systems because the watermark may still exist but no longer be sampled at the expected positions. See the geometric attack overview and the cropping/synchronization discussion in the sources.

The AQSM paper's specific crop attack is narrower than general cropping. It starts at the top-left vertex and expands a square along the diagonal. I rendered the source figure `paper_analysis/arxiv_src/crop_demo.pdf`; the figure shows the attacked carrier remaining the same size, with a black square masking the top-left area. So, in the paper's visualized protocol, "cropping" behaves like deterministic top-left square occlusion/blackout rather than a normal crop that reduces image size.

This distinction matters: a same-size black-square mask is easier to feed into the extractor than a true crop that changes dimensions and must be padded, resized, or otherwise resynchronized.

### Paper Protocol

The paper applies the top-left square crop/mask to watermarked carrier images and then extracts the watermark.

Reported crop sweep:

- `r = 1`, capacity `1/4`: `5%`, `10%`, `15%`, `20%`, `25%`, `30%`.
- `r = 2`, capacity `1/16`: paper text says from `5%` to `60%` in `5%` increments; the visualization highlights `10%` to `60%`.
- `r = 3`, capacity `1/64`: paper text says from `5%` to `60%` in `5%` increments; the visualization highlights `10%` to `60%`, and notes that `5%` gives nearly infinite extracted-watermark PSNR.

The paper again keeps only reported results with extracted-watermark `PSNR > 20 dB`.

Reported endpoint results:

| Scale | Lower Attack Level | Lower Result | Higher Attack Level | Higher Result |
|---|---:|---|---:|---|
| `r = 1` | crop `5%` | `PSNR = 27.94 dB`, `NCC = 0.9821` | crop `30%` | `PSNR = 22.02 dB`, `NCC = 0.9529` |
| `r = 2` | crop `5%` | `PSNR = 54.00 dB`, `NCC = 1.0` | crop `60%` | `PSNR = 23.03 dB`, `NCC = 0.9565` |
| `r = 3` | crop `10%` | `PSNR = 57.90 dB`, `NCC = 1.0` | crop `60%` | `PSNR = 21.61/21.62 dB`, `NCC = 0.9125` |

The source figure also shows intermediate values for the visualized examples. For `r = 1`, the sequence from `5%` to `30%` is:

- `5%`: `PSNR = 27.94`, `NCC = 0.9821`
- `10%`: `PSNR = 25.34`, `NCC = 0.9699`
- `15%`: `PSNR = 23.51`, `NCC = 0.9593`
- `20%`: `PSNR = 22.60`, `NCC = 0.9560`
- `25%`: `PSNR = 22.07`, `NCC = 0.9533`
- `30%`: `PSNR = 22.02`, `NCC = 0.9529`

### Why The Paper Expects Resistance

The paper argues that AQSM distributes the watermark throughout the carrier. Therefore, localized damage to one region should leave enough watermark information in other regions to reconstruct a recognizable watermark.

The reported results improve as `r` increases, but this comes with lower embedding capacity:

- `r = 1`: capacity `1/4`, less robust than larger `r`.
- `r = 2`: capacity `1/16`, more robust.
- `r = 3`: capacity `1/64`, strongest reported crop/noise robustness among the three.

This is the usual capacity/robustness trade-off: lower payload can be repeated or spread more heavily.

### Pros As A Test Attack

- Important for spatial watermarking because it tests localized data loss.
- Deterministic if the location and square size are fixed.
- Easy to sweep by crop/mask size.
- Directly tests whether AQSM distribution and majority voting survive missing carrier regions.
- More meaningful than only testing random noise because it damages contiguous blocks.

### Cons / Limitations

- The paper's crop is only top-left. It does not test random crop locations, center crops, object crops, or multiple occlusions.
- The visualized attack appears to be black-square masking, not true dimension-changing crop. That is less general than real-world cropping.
- Exact definition of crop percentage is not formalized enough. The figure suggests square side length percentage, but the paper does not give an implementation formula.
- It does not test crop followed by resize, which is common in real sharing pipelines.
- It does not test rotation, scaling, translation, row/column deletion, or other desynchronization attacks.
- Because the extractor expects fixed carrier dimensions, true cropping would require an extra resynchronization/padding policy not specified by the paper.

### Usability Notes For Our Repo

To match the paper most closely, implement the attack as same-size top-left square masking:

1. Keep the watermarked carrier dimensions unchanged.
2. Compute a square mask size from the chosen crop percentage.
3. Replace that top-left square with `0` pixels.
4. Extract the watermark from the masked carrier.

For a more realistic second experiment, add true crop-resize/pad variants, but label them clearly as beyond-paper attacks.

## Key Cross-Attack Takeaways

- The paper's robustness evidence is limited to salt-and-pepper noise and top-left square crop/mask attacks.
- Both attacks preserve the carrier array shape in the paper's visual workflows, which makes extraction straightforward.
- The paper's strongest robustness claims are for larger `r`, especially `r = 3`, but our current implementation is intentionally limited to the fully specified `r = 1` path.
- The paper does not give random seeds, exact carrier list, Elsevier watermark file, or complete implementation details for every robustness curve.
- For our current `r = 1` implementation, the faithful next step is to test:
  - Salt-and-pepper density sweep: `0.05`, `0.1`, `0.15`, `0.2`.
  - Top-left square mask sweep: `5%`, `10%`, `15%`, `20%`, `25%`, `30%`.
  - Multiple random seeds for salt-and-pepper.
  - Per-trial and average metrics.

## Sources Consulted

- AQSM paper online record: https://arxiv.org/abs/2502.18006
- Local paper PDF: `paper_analysis/adaptive quantum scaling model.pdf`
- Local extracted paper source: `paper_analysis/arxiv_src/A3_Manuscript.tex`
- Local crop visualization: `paper_analysis/arxiv_src/crop_demo.pdf`
- MATLAB `imnoise` documentation: https://www.mathworks.com/help/images/ref/imnoise.html
- scikit-image `random_noise` documentation: https://scikit-image.org/docs/stable/api/skimage.util.html
- MATLAB `imcrop` documentation: https://www.mathworks.com/help/images/ref/imcrop.html
- scikit-image image metrics documentation: https://scikit-image.org/docs/stable/api/skimage.metrics.html
- Watermarking robustness overview: https://www.sciencedirect.com/science/article/abs/pii/S0923596521002551
- Geometric attack overview: https://www.sciencedirect.com/topics/computer-science/geometric-attack
- Cropping robustness and synchronization discussion: https://www.mdpi.com/1424-8220/18/7/2096

## Self-Review

- Checked that the paper evaluates only salt-and-pepper noise and cropping in its robustness section.
- Verified the crop figure locally; the shown attack is same-size top-left black-square masking.
- Marked crop-percentage details as ambiguous where the paper does not provide an exact formula.
- Avoided adding unsupported results for attacks not evaluated by the paper.
- Tied implementation-level attack definitions to MATLAB/scikit-image documentation instead of inventing parameters.
- Separated paper-faithful tests from possible future beyond-paper tests.

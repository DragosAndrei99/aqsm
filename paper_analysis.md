# Adaptive Quantum Scaling Model Paper Analysis

## Sources used

- Local paper: `adaptive quantum scaling model.pdf`
- Extracted arXiv source: `arxiv_src/A3_Manuscript.tex`

This note separates:

- confirmed details that are explicit in the paper/source
- derived implementation logic that follows directly from the HDWM tables
- reproducibility gaps where the paper is underspecified or internally inconsistent

## What the paper is trying to do

The paper proposes a quantum watermarking scheme for grayscale NEQR images with three main pieces:

1. `AQSM` converts a grayscale watermark into one or more larger binary images so the watermark can be embedded into a larger carrier.
2. `HDWM` chooses how to write/extract watermark bits based on the watermark histogram and a parity-like value from the carrier MSBs.
3. `Quantum refining` performs majority voting on repeated bit-plane information during extraction.

The paper's experiments are not on real quantum hardware. They are MATLAB simulations on classical matrices, so a faithful Python reproduction should also be a classical array-level simulation of the image operations, not a full statevector simulation.

## Core notation

- Watermark size: `2^m x 2^m`
- Carrier size: `2^n x 2^n`
- Scale factor: `r = n - m`
- All images are 8-bit grayscale
- NEQR is used as the conceptual representation, but in the simulation the image data is effectively handled as matrices/bit planes

## AQSM, step by step

### 1. Preparation

The watermark is bit-plane decomposed into 8 binary planes:

- low half: `w_1l, w_2l, w_3l, w_4l`
- high half: `w_5h, w_6h, w_7h, w_8h`

The paper defines:

- `beta = 2` if `r = 1`
- `beta = r` if `r > 1`

Then:

- `alpha = 2^(2*beta - 3) - 1`

Useful values for the paper's experiments:

- `r = 1 -> beta = 2, alpha = 1`
- `r = 2 -> beta = 2, alpha = 1`
- `r = 3 -> beta = 3, alpha = 7`

The paper says bit decomposition must be repeated `alpha + 2` times because an unknown quantum state cannot be copied. In Python we do not need repeated decomposition; we only need to duplicate bit-plane arrays as required by the AQSM schedule.

### 2. Customization

This is the least explicit part of the paper.

The source states:

- low-half block sets count: `alpha`
- high-half block sets count: `alpha + 2`

Total block-set count:

- `2*alpha + 2 = 4^(r-1)`

Each block set contains 4 binary blocks, so total QBA input blocks are:

- `4 * (2*alpha + 2) = 4^r`

The paper explicitly gives only the three `r = 1` AQSM watermarks that are actually embedded:

1. `{w_1l, w_2l, w_3l, w_4l}`
2. `{w_5h, w_7h, w_7h, w_7h}`
3. `{w_6h, w_8h, w_8h, w_8h}`

This confirms the intended idea:

- lower-significance planes are kept with less redundancy
- more-significant planes are repeated more often
- the redundancy is intentionally odd-count so majority voting can recover the logical bit plane later

What is not explicit:

- the full AQSM block-set schedule for `r = 3`
- the omitted 4th `r = 1` AQSM output
- the exact general rule that maps `alpha` to all low/high block sets

### 3. Aggregation with QBA

QBA recursively combines 4 equally sized binary blocks into 1 larger binary block using block splicing:

- top-left block goes to coordinates `00`
- top-right block goes to `01`
- bottom-left block goes to `10`
- bottom-right block goes to `11`

After QBA at level `d`, output image size becomes:

- `2^(m+d) x 2^(m+d)`

The paper defines the number of outputs after level `d` as:

- `q = 4` if `r = 1`
- `q = 4^(r-d)` if `r > 1`

For watermark embedding the paper sets:

- `d = 1` if `r = 1`
- `d = r` if `r > 1`

Therefore:

- `r = 1`: AQSM produces four `2^n x 2^n` binary outputs, but only three are embedded
- `r = 2`: AQSM produces one final `2^n x 2^n` binary output
- `r = 3`: AQSM produces one final `2^n x 2^n` binary output

## HDWM, step by step

### 1. Histogram statistics

The paper defines:

- `h(g)`: count of watermark pixels with grayscale value `g`
- `H(g) = sum_{x=0..g} h(x)`

It splits grayscale values into:

- dark interval: `0..127`
- bright interval: `128..255`

Then:

- `T_dark = H(127) / (...)`
- `T_bright = 1 - H(127) / (...)`

Important reproducibility issue:

- The source writes the denominator as `2^m x 2^n`
- For a watermark of size `2^m x 2^m`, the mathematically consistent denominator should be `2^(2m)`
- This looks like a paper typo and must be clarified before implementation

### 2. Histogram-based parameters

The paper defines threshold `lambda` in `[0, 1]`, and later fixes:

- `lambda = 0.5`

Then:

- `tau_1 = 0` if `|T_bright - T_dark| < lambda`
- `tau_1 = 1` otherwise

If `tau_1 = 1`, then:

- `tau_2 = 0` if `T_dark >= (1 + lambda)/2`
- `tau_2 = 1` if `T_bright >= (1 + lambda)/2`

With `lambda = 0.5`, the second threshold is:

- `(1 + lambda)/2 = 0.75`

So in practice:

- if histogram is not strongly biased: `tau_1 = 0`
- if strongly dark-biased: `tau_1 = 1, tau_2 = 0`
- if strongly bright-biased: `tau_1 = 1, tau_2 = 1`

### 3. XOR index

The paper defines:

- `eta = 0` if `r = 1`
- `eta = r mod 2` if `r > 1`

and says:

- if `eta = 0`, use XOR of 3 MSBs
- if `eta = 1`, use XOR of 4 MSBs

The paper does not write the explicit formula for `V_eta`, but the intended interpretation is almost certainly:

- `V_0 = XOR` of the top 3 most significant carrier bits
- `V_1 = XOR` of the top 4 most significant carrier bits

This still needs confirmation because the exact bit indices are never formalized in the text.

## HDWM embedding and extraction logic derived from the tables

Let:

- `w` be the AQSM watermark bit to embed
- `b` be the selected carrier LSB before embedding
- `b'` be the selected carrier LSB after embedding
- `V` be `V_eta`

From Table I and Table II, the logic reduces cleanly to:

### Embedding

- if `tau_1 = 0`: set `b' = w`
- if `tau_1 = 1` and `tau_2 = 0`: set `b' = w XOR V`
- if `tau_1 = 1` and `tau_2 = 1`: set `b' = w XOR (1 - V)`

### Extraction

- if `tau_1 = 0`: recover `w_hat = b'`
- if `tau_1 = 1` and `tau_2 = 0`: recover `w_hat = b' XOR V`
- if `tau_1 = 1` and `tau_2 = 1`: recover `w_hat = b' XOR (1 - V)`

This is the most implementation-useful interpretation of the HDWM tables.

## End-to-end embedding pipeline

1. Read classical watermark and carrier grayscale images.
2. Compute `m`, `n`, and `r = n - m`.
3. Compute histogram of the watermark image.
4. Compute `T_dark`, `T_bright`, `tau_1`, `tau_2`.
5. Run AQSM on the watermark to produce one or more binary `2^n x 2^n` watermark images.
6. Compute `eta`.
7. For each carrier pixel, compute `V_eta` from the carrier MSBs.
8. Embed the AQSM watermark bits into carrier LSB locations using the HDWM rule above.
9. Convert back to an 8-bit watermarked image.

Important ambiguity:

- The paper says embedding starts from the first LSB "in turn"
- For `r = 1` this is consistent with embedding three AQSM watermarks into the first three LSB planes
- For `r > 1`, the paper later says only one AQSM watermark is extracted/prepared, so the intended LSB usage for `r = 2, 3` should be treated carefully during implementation

## End-to-end extraction pipeline

1. Convert the watermarked grayscale image into bit planes.
2. Using the same `tau_1`, `tau_2`, and `eta`, extract AQSM watermark bit images from the LSB plane(s).
3. Apply inverse QBA to recover the extracted low/high block sets.
4. Apply quantum refining as majority voting over repeated copies of each logical bit plane.
5. Reconstruct the 8 watermark bit planes.
6. Reassemble the grayscale watermark image.

## Quantum refining, practical interpretation

The paper's "quantum refining" is effectively majority voting over repeated copies of the same bit-plane information after inverse QBA.

In a Python matrix implementation, this should be modeled as:

- group all copies that correspond to the same original bit plane
- take pixel-wise majority vote over each group
- keep the voted result as the refined bit plane

The paper explicitly says the scheme relies on odd-length sequences so minority errors can be ignored.

## Experiment protocol in the paper

### Environment

- MATLAB 2020b
- Intel Core i7 2.30 GHz
- 16 GB RAM

### Data

- 83 grayscale carrier images
- size: `512 x 512`
- source: USC-SIPI
- watermark image: grayscale `Elsevier` logo
- watermark sizes:
  - `256 x 256` for `r = 1`
  - `128 x 128` for `r = 2`
  - `64 x 64` for `r = 3`

### Metrics

- `PSNR`
- `SSIM`
- `NCC`

### Capacities

The paper defines:

- `C = Q_w / Q_c = 1 / 4^r`

So:

- `r = 1 -> capacity 1/4`
- `r = 2 -> capacity 1/16`
- `r = 3 -> capacity 1/64`

### Visual quality results reported in the paper

Mean values over the 83 test images:

- `r = 1`: mean `PSNR = 36.78 dB`, mean `SSIM = 0.9693`
- `r = 2`: mean `PSNR = 51.25 dB`, mean `SSIM = 0.9982`
- `r = 3`: mean `PSNR = 51.15 dB`, mean `SSIM = 0.9981`

### Salt-and-pepper noise protocol

For `r = 1` and `r = 2`:

- densities: `0.05, 0.1, 0.15, 0.2`

For `r = 3`:

- densities: `0.1, 0.2, 0.3, 0.4`

Only results with extracted-watermark `PSNR > 20 dB` are shown.

Reported average values:

- `r = 1`, density `0.05`: `PSNR = 32.06 dB`, `NCC = 0.9926`
- `r = 1`, density `0.2`: `PSNR = 22.44 dB`, `NCC = 0.9343`
- `r = 2`, density `0.05`: `PSNR = 35.45 dB`, `NCC = 0.9963`
- `r = 2`, density `0.2`: `PSNR = 23.74 dB`, `NCC = 0.9481`
- `r = 3`, density `0.1`: `PSNR = 61.20 dB`, `NCC = 0.9999`
- `r = 3`, density `0.4`: `PSNR = 21.72 dB`, `NCC = 0.9014`

### Cropping protocol

Cropping starts at the top-left corner and expands as a square along the diagonal.

For `r = 1`:

- `5%, 10%, 15%, 20%, 25%, 30%`

For `r = 2` and `r = 3`:

- `5%, 10%, 15%, ... , 60%`

Only results with extracted-watermark `PSNR > 20 dB` are shown.

Reported average values:

- `r = 1`, `5%`: `PSNR = 27.94 dB`, `NCC = 0.9821`
- `r = 1`, `30%`: `PSNR = 22.02 dB`, `NCC = 0.9529`
- `r = 2`, `5%`: `PSNR = 54.00 dB`, `NCC = 1.0`
- `r = 2`, `60%`: `PSNR = 23.03 dB`, `NCC = 0.9565`
- `r = 3`, `10%`: `PSNR = 57.90 dB`, `NCC = 1.0`
- `r = 3`, `60%`: `PSNR = 21.61 dB`, `NCC = 0.9125`

### HDWM ablation

The paper compares:

- proposed method with HDWM
- direct LSB substitution without HDWM

Reported mean PSNR improvement from HDWM:

- `r = 1`: `23.14%`
- `r = 2`: `14.42%`
- `r = 3`: `1.25%`

## Reproducibility blockers and ambiguities

These are the main reasons we cannot guarantee the exact paper curves/tables from the paper alone:

1. The exact list of the 83 USC-SIPI carrier images is not given.
2. The exact `Elsevier` watermark image file is not included in the source bundle.
3. The complete AQSM customization schedule is not written out, especially for `r = 3`.
4. The omitted 4th `r = 1` AQSM watermark is not explicitly stated.
5. `T_dark` and `T_bright` use a denominator that appears inconsistent with watermark size.
6. The source swaps "low half" and "high half" when naming `S_kl` and `S_kh`.
7. The exact bit indices used in `V_eta` are described informally, not formally.
8. The embedding text uses `j in {1,2,3}` even though for `r > 1` the AQSM output count is `q = 1`.

## Recommended Python implementation strategy

### Phase 1: paper-faithful classical simulation

Use:

- `numpy` for bit-plane and block operations
- `opencv-python` or `Pillow` for image I/O
- `scikit-image` for `SSIM`

Suggested modules:

- `io_utils.py`: load/save grayscale images
- `metrics.py`: PSNR, SSIM, NCC
- `attacks.py`: salt-and-pepper, top-left square crop
- `aqsm.py`: bit-plane decomposition, block-set scheduling, QBA, inverse QBA
- `hdwm.py`: histogram stats, `tau_1`, `tau_2`, `eta`, `V_eta`, embed/extract
- `refine.py`: majority-vote reconstruction
- `pipeline.py`: end-to-end embed/extract/evaluate

### Phase 2: experiment runner

- fixed run for `r = 1, 2, 3`
- per-image metric collection
- aggregate means matching the paper's reporting style

### Phase 3: optional circuit mapping

Only after the matrix simulation is stable:

- map QBA/QBS/QIB/HDWM logic to Qiskit-style circuit sketches
- do not try to simulate full 512x512 NEQR states directly

## Minimal clarification needed before coding

To implement this without inventing missing behavior, we still need answers to:

1. Do we have the exact `Elsevier` watermark image used by the authors?
2. Do we have the exact list of the 83 USC-SIPI carrier images?
3. For `r = 3`, what AQSM block-set schedule should we use, since the paper does not state it explicitly?
4. Should `T_dark` and `T_bright` use denominator `2^(2m)` instead of the printed `2^m * 2^n`?
5. Do you want the Python work to target the practical MATLAB-style matrix simulation first, or do you also want Qiskit circuit construction in the same implementation?

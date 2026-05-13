# Adaptive Quantum Scaling Model Demo

This repository contains a compact Python implementation of the paper walkthroughs for **Adaptive Quantum Scaling Model for Histogram Distribution-based Quantum Watermarking**.

The current code is intentionally conservative: it implements the paper's fully specified `r = 1` embedding case, where a watermark image has half the side length of the carrier image, for example:

```text
256x256 watermark -> 512x512 carrier
2x2 watermark     -> 4x4 carrier
```

It can run the tiny worked example from the markdown notes or download small real-image samples from the USC-SIPI Miscellaneous image database.

## What You Can Run

- `python main.py`: downloads a USC-SIPI-style sample pair, embeds the watermark, and writes a visual HTML report.
- `python main.py --toy`: runs the tiny `2x2 -> 4x4` walkthrough example.
- `python -m unittest -v`: runs the regression tests.
- `jupyter notebook aqsm_real_image_walkthrough.ipynb`: opens the central notebook with step-by-step calls and visual outputs.

Generated reports, downloaded sample images, and PNG previews are written under `example_outputs/`.

## Setup

Use Python `3.8` or newer. The dependency pins in `requirements.txt` include compatibility markers: Python `3.8` uses the classic Notebook 6 stack, while newer Python versions use the modern Notebook 7 stack.

### Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name aqsm-demo --display-name "AQSM Demo"
```

If PowerShell blocks virtualenv activation, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m ipykernel install --user --name aqsm-demo --display-name "AQSM Demo"
```

## Quick Verification

After setup, run:

```bash
python -m unittest -v
python main.py --no-open
```

The first command should pass all tests. The second command should create:

```text
example_outputs/aqsm_report.html
```

Open that file in a browser to inspect the input images, bit planes, AQSM watermarks, intermediate carrier states, final watermarked carrier, and computed parameters.

## Running The Notebook

Start Jupyter from the repository root:

```bash
jupyter notebook aqsm_real_image_walkthrough.ipynb
```

Then select the `AQSM Demo` kernel if prompted.

If `jupyter` is not on your `PATH`, use:

```bash
python -m notebook aqsm_real_image_walkthrough.ipynb
```

You can also execute the notebook headlessly:

```bash
jupyter nbconvert --to notebook --execute --inplace aqsm_real_image_walkthrough.ipynb
```

The notebook walks through the pipeline manually:

1. Download USC-SIPI sample images.
2. Load them as 8-bit grayscale matrices.
3. Build conceptual NEQR descriptions.
4. Compute scale parameters and HDWM histogram parameters.
5. Decompose watermark bit planes.
6. Build AQSM watermarks.
7. Compute carrier `V_eta`.
8. Embed into carrier LSB planes.
9. Display the output and a scaled difference image.

## Running With Your Own Images

Use square grayscale or color images. Color files are converted to grayscale automatically. For the currently implemented `r = 1` path, the watermark side must be half the carrier side.

```bash
python main.py --watermark path/to/watermark.png --carrier path/to/carrier.png
```

If the files are not already the right size, resize them while loading:

```bash
python main.py \
  --watermark path/to/watermark.png \
  --carrier path/to/carrier.png \
  --watermark-side 256 \
  --carrier-side 512
```

On Windows PowerShell, use backticks for line continuation:

```powershell
python main.py `
  --watermark path\to\watermark.png `
  --carrier path\to\carrier.png `
  --watermark-side 256 `
  --carrier-side 512
```

Useful flags:

```text
--no-open                      Write the report without opening the browser.
--toy                          Use the tiny built-in walkthrough example.
--force-download               Redownload the USC-SIPI sample TIFFs.
--output-dir example_outputs   Choose where reports and preview images are written.
--histogram-denominator-mode   Use "natural" or the paper's printed "paper" denominator.
```

## Dataset Notes

The default real-image demo uses the USC-SIPI Miscellaneous volume:

- Database: https://sipi.usc.edu/database/
- Miscellaneous volume: https://sipi.usc.edu/database/?volume=misc

The code downloads:

- `5.1.09`: Moon surface, `256x256`, grayscale, used as the watermark.
- `5.2.08`: Couple, `512x512`, grayscale, used as the default carrier.
- `5.2.10`: Stream and bridge, `512x512`, grayscale, cached for experiments.
- `boat.512`: Fishing boat, `512x512`, grayscale, cached for experiments.

USC-SIPI images are intended for research use. Check the database copyright notes before using them in publications.

## Project Map

```text
aqsm_embedding_core/
  embedding_pipeline.py          End-to-end embedding pipeline.
  image_file_loader.py           Real image loading and PNG export.
  usc_sipi_dataset.py            Small USC-SIPI sample downloader.
  embedding_report_writer.py     HTML visual report writer.
  aqsm_watermark_builder.py      r = 1 AQSM watermark construction.
  hdwm_embedder.py               HDWM LSB embedding logic.
  histogram_analyzer.py          Histogram branch parameters.
  bit_plane_decomposer.py        w1..w8 bit-plane decomposition.
  quantum_block_aggregator.py    QBA/QBS quadrant aggregation.
  neqr_encoder.py                Conceptual NEQR state summaries.

paper_analysis/
  adaptive quantum scaling model.pdf       Local paper copy.
  paper_analysis.md                        Paper notes and reproducibility gaps.
  aqsm_2x2_step_by_step.md                 Classical worked walkthrough.
  aqsm_2x2_quantum_step_by_step.md         Quantum-notation worked walkthrough.
  arxiv_src/                               Extracted arXiv source bundle.

aqsm_real_image_walkthrough.ipynb  Central visual notebook.
main.py                            Command-line demo/report runner.
test_aqsm_embedding.py             Regression tests for the worked example.
requirements.txt                   Python dependencies.
```

## Current Limitations

- Only the embedding side is implemented.
- Only the paper's explicit `r = 1` AQSM schedule is implemented.
- Extraction and quantum refining are described in the markdown walkthroughs but not yet implemented as code.
- This is a classical matrix simulation of the paper's operations, matching the paper's MATLAB simulation style; it is not a quantum hardware/statevector simulator.

## Troubleshooting

If imports fail in the notebook, make sure Jupyter was launched from the repository root and the `AQSM Demo` kernel is selected.

If `main.py` raises an `AQSM watermark construction is intentionally limited to r=1` error, use a watermark whose side length is exactly half the carrier side length.

If image loading fails, check that dependencies were installed in the active virtual environment:

```bash
python -m pip install -r requirements.txt
```

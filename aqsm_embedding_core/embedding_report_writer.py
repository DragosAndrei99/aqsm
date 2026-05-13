"""HTML report generation for AQSM embedding runs."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Mapping, Sequence

from .embedding_context import EmbeddingContext
from .image_file_loader import ImageFileLoader
from .types import ImageMatrix


class EmbeddingReportWriter:
    """Write a visual HTML report for one embedding pipeline run.

    Inputs:
        Input matrices, an `EmbeddingContext`, and optional run metadata.

    Outputs:
        A self-contained HTML page plus PNG images in a sibling assets directory.
    """

    def __init__(self, image_loader: ImageFileLoader | None = None) -> None:
        self.image_loader = image_loader or ImageFileLoader()

    @staticmethod
    def _absolute_difference(first: Sequence[Sequence[int]], second: Sequence[Sequence[int]]) -> ImageMatrix:
        return [
            [abs(left - right) for left, right in zip(first_row, second_row)]
            for first_row, second_row in zip(first, second)
        ]

    @staticmethod
    def _visible_difference(diff: Sequence[Sequence[int]]) -> ImageMatrix:
        max_value = max(max(row) for row in diff)
        if max_value == 0:
            return [[0 for _ in row] for row in diff]
        return [[round((value / max_value) * 255) for value in row] for row in diff]

    @staticmethod
    def _table(items: Mapping[str, object]) -> str:
        rows = "\n".join(
            f"<tr><th>{escape(str(key))}</th><td>{escape(str(value))}</td></tr>"
            for key, value in items.items()
        )
        return f"<table>{rows}</table>"

    @staticmethod
    def _image_card(title: str, relative_path: str, note: str = "") -> str:
        note_html = f"<p>{escape(note)}</p>" if note else ""
        return (
            "<figure>"
            f"<img src=\"{escape(relative_path)}\" alt=\"{escape(title)}\">"
            f"<figcaption>{escape(title)}</figcaption>"
            f"{note_html}"
            "</figure>"
        )

    def write(
        self,
        output_directory: str | Path,
        watermark_image: Sequence[Sequence[int]],
        carrier_image: Sequence[Sequence[int]],
        context: EmbeddingContext,
        metadata: Mapping[str, object] | None = None,
        report_name: str = "aqsm_report.html",
    ) -> str:
        """Write the report and return the HTML path."""

        output_path = Path(output_directory)
        assets_path = output_path / "aqsm_report_assets"
        output_path.mkdir(parents=True, exist_ok=True)
        assets_path.mkdir(parents=True, exist_ok=True)

        saved_images: dict[str, str] = {}

        def save(name: str, image: Sequence[Sequence[int]], binary: bool = False) -> None:
            filename = f"{name}.png"
            self.image_loader.save_png(
                image,
                assets_path / filename,
                scale_binary_to_255=binary,
            )
            saved_images[name] = f"aqsm_report_assets/{filename}"

        save("input_watermark", watermark_image)
        save("input_carrier", carrier_image)
        for name, bit_plane in context.bit_planes.items():
            save(name, bit_plane, binary=True)
        for index, aqsm_image in enumerate(context.aqsm_result.embedded_watermarks, start=1):
            save(f"aqsm_watermark_{index}", aqsm_image, binary=True)
        save("carrier_xor_v_eta", context.embedding_result.xor_matrix, binary=True)
        for stage_name, image in context.embedding_result.intermediate_images.items():
            save(stage_name, image)
        save("final_watermarked_carrier", context.embedding_result.final_image)

        raw_diff = self._absolute_difference(carrier_image, context.embedding_result.final_image)
        visible_diff = self._visible_difference(raw_diff)
        save("carrier_absolute_difference_scaled", visible_diff)

        scale = context.scale_parameters
        histogram = context.histogram_parameters
        scale_table = self._table(
            {
                "watermark exponent m": scale.watermark_side_exponent,
                "carrier exponent n": scale.carrier_side_exponent,
                "scale factor r": scale.scale_factor,
                "beta": scale.beta,
                "alpha": scale.alpha,
                "QBA aggregation level d": scale.aggregation_level,
                "declared AQSM output count q": scale.q_outputs,
                "embedded AQSM images": len(context.aqsm_result.embedded_watermarks),
            }
        )
        histogram_table = self._table(
            {
                "dark pixels [0, 127]": histogram.dark_count,
                "bright pixels [128, 255]": histogram.bright_count,
                "denominator": histogram.denominator,
                "lambda": histogram.threshold_lambda,
                "T_dark": f"{histogram.t_dark:.6f}",
                "T_bright": f"{histogram.t_bright:.6f}",
                "tau1": histogram.tau1,
                "tau2": histogram.tau2,
            }
        )
        neqr_table = self._table(
            {
                "watermark NEQR terms": len(context.watermark_neqr.terms),
                "watermark amplitude": context.watermark_neqr.amplitude,
                "carrier NEQR terms": len(context.carrier_neqr.terms),
                "carrier amplitude": context.carrier_neqr.amplitude,
                "first watermark term": context.watermark_neqr.terms[0],
                "first carrier term": context.carrier_neqr.terms[0],
            }
        )
        metadata_table = self._table(metadata or {})

        input_cards = "\n".join(
            [
                self._image_card("Input watermark", saved_images["input_watermark"]),
                self._image_card("Input carrier", saved_images["input_carrier"]),
                self._image_card(
                    "Final watermarked carrier",
                    saved_images["final_watermarked_carrier"],
                ),
                self._image_card(
                    "Carrier absolute difference, scaled",
                    saved_images["carrier_absolute_difference_scaled"],
                    "Scaled for visibility; actual LSB changes are much smaller.",
                ),
            ]
        )
        bit_plane_cards = "\n".join(
            self._image_card(name, saved_images[name])
            for name in sorted(context.bit_planes.keys(), key=lambda item: int(item[1:]))
        )
        aqsm_cards = "\n".join(
            self._image_card(f"AQSM watermark {index}", saved_images[f"aqsm_watermark_{index}"])
            for index in range(1, len(context.aqsm_result.embedded_watermarks) + 1)
        )
        embedding_cards = "\n".join(
            [self._image_card("Carrier xor matrix V_eta", saved_images["carrier_xor_v_eta"])]
            + [
                self._image_card(stage_name, saved_images[stage_name])
                for stage_name in context.embedding_result.intermediate_images
            ]
        )

        html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AQSM Embedding Report</title>
  <style>
    body {{
      color: #17202a;
      font-family: Arial, sans-serif;
      line-height: 1.45;
      margin: 28px;
      background: #f6f7f9;
    }}
    h1, h2 {{ margin-bottom: 8px; }}
    section {{ margin: 28px 0; }}
    .grid {{
      display: grid;
      gap: 18px;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }}
    figure {{
      background: #ffffff;
      border: 1px solid #d7dce2;
      border-radius: 8px;
      margin: 0;
      padding: 12px;
    }}
    img {{
      display: block;
      image-rendering: auto;
      max-width: 100%;
      width: 100%;
      border: 1px solid #e3e7ec;
      background: #fff;
    }}
    figcaption {{
      font-weight: 700;
      margin-top: 10px;
    }}
    table {{
      background: #ffffff;
      border-collapse: collapse;
      margin: 10px 0 20px;
      min-width: 340px;
    }}
    th, td {{
      border: 1px solid #d7dce2;
      padding: 8px 10px;
      text-align: left;
      vertical-align: top;
    }}
    th {{ background: #edf1f5; }}
  </style>
</head>
<body>
  <h1>AQSM Embedding Report</h1>
  <section>
    <h2>Run Metadata</h2>
    {metadata_table}
  </section>
  <section>
    <h2>Computed Parameters</h2>
    <h3>Scale</h3>
    {scale_table}
    <h3>Histogram / HDWM</h3>
    {histogram_table}
    <h3>NEQR Summary</h3>
    {neqr_table}
  </section>
  <section>
    <h2>Inputs And Output</h2>
    <div class="grid">{input_cards}</div>
  </section>
  <section>
    <h2>Watermark Bit Planes</h2>
    <div class="grid">{bit_plane_cards}</div>
  </section>
  <section>
    <h2>AQSM Watermarks</h2>
    <div class="grid">{aqsm_cards}</div>
  </section>
  <section>
    <h2>Embedding Stages</h2>
    <div class="grid">{embedding_cards}</div>
  </section>
</body>
</html>
"""

        report_path = output_path / report_name
        report_path.write_text(html, encoding="utf-8")
        return str(report_path)

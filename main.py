"""Run AQSM/HDWM embedding and produce a visual report."""

from __future__ import annotations

import argparse
import os
import webbrowser
from pathlib import Path

from aqsm_embedding import (
    EmbeddingPipeline,
    EmbeddingReportWriter,
    ExampleImageRepository,
    ImageDisplay,
    ImageFileLoader,
    USCSIPISampleDataset,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser for the demo runner."""

    parser = argparse.ArgumentParser(
        description=(
            "Run the AQSM/HDWM embedding pipeline. By default this downloads a "
            "small USC-SIPI-like real-image pair: a 256x256 grayscale watermark "
            "and a 512x512 grayscale carrier."
        )
    )
    parser.add_argument("--carrier", type=Path, help="Path to a custom carrier image.")
    parser.add_argument("--watermark", type=Path, help="Path to a custom watermark image.")
    parser.add_argument(
        "--carrier-side",
        type=int,
        help="Optional square power-of-two side to resize the carrier to.",
    )
    parser.add_argument(
        "--watermark-side",
        type=int,
        help="Optional square power-of-two side to resize the watermark to.",
    )
    parser.add_argument(
        "--histogram-denominator-mode",
        choices=("natural", "paper"),
        default="natural",
        help="Histogram denominator convention.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("example_outputs"),
        help="Directory for PNG previews and the HTML report.",
    )
    parser.add_argument(
        "--toy",
        action="store_true",
        help="Use the tiny 2x2 into 4x4 markdown walkthrough instead of real images.",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="Redownload the USC-SIPI sample files even if cached copies exist.",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the generated HTML report in the default browser.",
    )
    return parser


def load_images(args: argparse.Namespace) -> tuple[list[list[int]], list[list[int]], dict[str, object]]:
    """Load either toy, custom, or default USC-SIPI sample images."""

    if args.toy:
        watermark_image, carrier_image = ExampleImageRepository.worked_example_inputs()
        return watermark_image, carrier_image, {"source": "Built-in 2x2 -> 4x4 walkthrough"}

    loader = ImageFileLoader()
    if args.carrier or args.watermark:
        if not args.carrier or not args.watermark:
            raise ValueError("Provide both --carrier and --watermark, or neither.")

        watermark_image = loader.load_grayscale(args.watermark, target_side=args.watermark_side)
        carrier_image = loader.load_grayscale(args.carrier, target_side=args.carrier_side)
        return (
            watermark_image,
            carrier_image,
            {
                "source": "Custom image files",
                "watermark path": str(args.watermark),
                "carrier path": str(args.carrier),
            },
        )

    dataset = USCSIPISampleDataset(args.output_dir / "usc_sipi_samples")
    watermark_path, carrier_path = dataset.default_pair(force=args.force_download)
    watermark_image = loader.load_grayscale(watermark_path)
    carrier_image = loader.load_grayscale(carrier_path)
    return (
        watermark_image,
        carrier_image,
        {
            "source": "USC-SIPI Miscellaneous sample",
            "dataset page": dataset.DATASET_PAGE_URL,
            "watermark": str(watermark_path),
            "carrier": str(carrier_path),
        },
    )


def main() -> None:
    """Run the embedding pipeline and write a visual HTML report."""

    args = build_parser().parse_args()
    watermark_image, carrier_image, metadata = load_images(args)

    pipeline = EmbeddingPipeline()
    context = pipeline.run(
        watermark_image=watermark_image,
        carrier_image=carrier_image,
        histogram_denominator_mode=args.histogram_denominator_mode,
    )

    display = ImageDisplay()
    print("Scale parameters:", context.scale_parameters)
    print(
        "Histogram summary:",
        {
            "dark_count": context.histogram_parameters.dark_count,
            "bright_count": context.histogram_parameters.bright_count,
            "denominator": context.histogram_parameters.denominator,
            "t_dark": context.histogram_parameters.t_dark,
            "t_bright": context.histogram_parameters.t_bright,
            "tau1": context.histogram_parameters.tau1,
            "tau2": context.histogram_parameters.tau2,
        },
    )
    print("AQSM watermarks embedded:", len(context.aqsm_result.embedded_watermarks))

    if len(carrier_image) <= 8:
        print()
        display.print_image("Watermark image", watermark_image)
        print()
        display.print_image("Carrier image", carrier_image)
        print()
        display.print_image("Final watermarked carrier", context.embedding_result.final_image)

    report_writer = EmbeddingReportWriter()
    report_path = report_writer.write(
        output_directory=args.output_dir,
        watermark_image=watermark_image,
        carrier_image=carrier_image,
        context=context,
        metadata=metadata,
    )
    absolute_report_path = os.path.abspath(report_path)
    print(f"Visual report written to: {absolute_report_path}")

    if not args.no_open:
        webbrowser.open(Path(absolute_report_path).as_uri())


if __name__ == "__main__":
    main()

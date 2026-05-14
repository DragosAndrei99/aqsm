"""Unit tests for the simple AQSM/HDWM embedding implementation."""

from __future__ import annotations

import os
import tempfile
import unittest

from aqsm_embedding import (
    AQSMWatermarkBuilder,
    BitPlaneDecomposer,
    CarrierXorCalculator,
    EmbeddingPipeline,
    ExampleImageRepository,
    HDWMExtractor,
    HDWMEmbedder,
    HistogramAnalyzer,
    ImageDisplay,
    NEQREncoder,
    ScaleParameterCalculator,
)


class AQSMEmbeddingTests(unittest.TestCase):
    """Validate the embedding-side implementation against the worked markdown example."""

    def setUp(self) -> None:
        self.watermark_image, self.carrier_image = ExampleImageRepository.worked_example_inputs()
        self.expected_bit_planes = ExampleImageRepository.expected_bit_planes()
        self.expected_aqsm = ExampleImageRepository.expected_aqsm_watermarks()
        self.expected_xor = ExampleImageRepository.expected_xor_matrix()
        self.expected_intermediates = ExampleImageRepository.expected_intermediate_images()
        self.expected_final = ExampleImageRepository.expected_final_image()

    def test_neqr_encoding_matches_worked_example(self) -> None:
        encoder = NEQREncoder()
        encoded = encoder.encode(self.watermark_image)

        self.assertEqual(encoded.side_exponent, 1)
        self.assertEqual(encoded.amplitude, 0.5)
        self.assertEqual(len(encoded.terms), 4)
        self.assertEqual(encoded.terms[0].grayscale_bits, "10000010")
        self.assertEqual(encoded.terms[0].y_bits, "0")
        self.assertEqual(encoded.terms[0].x_bits, "0")
        self.assertEqual(encoded.terms[-1].grayscale_bits, "11111111")
        self.assertEqual(encoded.terms[-1].y_bits, "1")
        self.assertEqual(encoded.terms[-1].x_bits, "1")

    def test_scale_parameters_match_worked_example(self) -> None:
        calculator = ScaleParameterCalculator()
        parameters = calculator.compute(self.watermark_image, self.carrier_image)

        self.assertEqual(parameters.watermark_side_exponent, 1)
        self.assertEqual(parameters.carrier_side_exponent, 2)
        self.assertEqual(parameters.scale_factor, 1)
        self.assertEqual(parameters.beta, 2)
        self.assertEqual(parameters.alpha, 1)
        self.assertEqual(parameters.aggregation_level, 1)
        self.assertEqual(parameters.q_outputs, 4)

    def test_histogram_parameters_match_worked_example(self) -> None:
        calculator = ScaleParameterCalculator()
        parameters = calculator.compute(self.watermark_image, self.carrier_image)
        analyzer = HistogramAnalyzer()
        histogram = analyzer.analyze(self.watermark_image, parameters, denominator_mode="natural")

        self.assertEqual(histogram.dark_count, 0)
        self.assertEqual(histogram.bright_count, 4)
        self.assertEqual(histogram.denominator, 4)
        self.assertEqual(histogram.t_dark, 0.0)
        self.assertEqual(histogram.t_bright, 1.0)
        self.assertEqual(histogram.tau1, 1)
        self.assertEqual(histogram.tau2, 1)

    def test_bit_plane_decomposition_matches_worked_example(self) -> None:
        decomposer = BitPlaneDecomposer()
        bit_planes = decomposer.decompose(self.watermark_image)

        self.assertEqual(bit_planes, self.expected_bit_planes)

    def test_aqsm_watermarks_match_worked_example(self) -> None:
        calculator = ScaleParameterCalculator()
        parameters = calculator.compute(self.watermark_image, self.carrier_image)
        decomposer = BitPlaneDecomposer()
        builder = AQSMWatermarkBuilder()
        aqsm = builder.build(decomposer.decompose(self.watermark_image), parameters)

        self.assertEqual(aqsm.declared_output_count, 4)
        self.assertEqual(aqsm.embedded_watermarks, self.expected_aqsm)

    def test_xor_matrix_matches_worked_example(self) -> None:
        xor_calculator = CarrierXorCalculator()
        xor_matrix = xor_calculator.compute(self.carrier_image, eta=0)

        self.assertEqual(xor_matrix, self.expected_xor)

    def test_full_embedding_matches_worked_example(self) -> None:
        pipeline = EmbeddingPipeline()
        context = pipeline.run(self.watermark_image, self.carrier_image, "natural")

        self.assertEqual(context.bit_planes, self.expected_bit_planes)
        self.assertEqual(context.aqsm_result.embedded_watermarks, self.expected_aqsm)
        self.assertEqual(context.embedding_result.xor_matrix, self.expected_xor)
        self.assertEqual(
            context.embedding_result.intermediate_images["after_bit0"],
            self.expected_intermediates["after_bit0"],
        )
        self.assertEqual(
            context.embedding_result.intermediate_images["after_bit1"],
            self.expected_intermediates["after_bit1"],
        )
        self.assertEqual(
            context.embedding_result.intermediate_images["after_bit2"],
            self.expected_intermediates["after_bit2"],
        )
        self.assertEqual(context.embedding_result.final_image, self.expected_final)

    def test_display_can_render_and_export(self) -> None:
        display = ImageDisplay()
        numeric = display.render_numeric(self.carrier_image)
        binary = display.render_binary(self.expected_xor)

        self.assertIn("[212", numeric)
        self.assertIn("1", binary)

        with tempfile.TemporaryDirectory() as temp_directory:
            output_path = os.path.join(temp_directory, "carrier.pgm")
            saved_path = display.save_pgm(self.carrier_image, output_path)
            self.assertTrue(os.path.exists(saved_path))

            with open(saved_path, "r", encoding="utf-8") as handle:
                content = handle.read()

            self.assertTrue(content.startswith("P2"))

    def test_hdwm_embed_bit_rule_matches_tau1_tau2_branch(self) -> None:
        embedder = HDWMEmbedder()

        self.assertEqual(embedder.compute_embedded_bit(0, 0, 1, 1), 1)
        self.assertEqual(embedder.compute_embedded_bit(1, 1, 1, 1), 1)
        self.assertEqual(embedder.compute_embedded_bit(1, 0, 1, 0), 1)
        self.assertEqual(embedder.compute_embedded_bit(1, 0, 0, None), 1)

    def test_full_extraction_recovers_worked_example_watermark(self) -> None:
        pipeline = EmbeddingPipeline()
        context = pipeline.run(self.watermark_image, self.carrier_image, "natural")
        extractor = HDWMExtractor()

        extraction = extractor.extract(
            watermarked_image=context.embedding_result.final_image,
            histogram_parameters=context.histogram_parameters,
            scale_parameters=context.scale_parameters,
        )

        self.assertEqual(extraction.extracted_aqsm_watermarks, self.expected_aqsm)
        self.assertEqual(extraction.refined_bit_planes, self.expected_bit_planes)
        self.assertEqual(extraction.recovered_watermark, self.watermark_image)

    def test_hdwm_extract_bit_rule_matches_inverse_branches(self) -> None:
        extractor = HDWMExtractor()

        self.assertEqual(extractor.compute_extracted_bit(1, 0, 1, 1), 0)
        self.assertEqual(extractor.compute_extracted_bit(1, 1, 1, 1), 1)
        self.assertEqual(extractor.compute_extracted_bit(1, 0, 1, 0), 1)
        self.assertEqual(extractor.compute_extracted_bit(1, 0, 0, None), 1)


if __name__ == "__main__":
    unittest.main()

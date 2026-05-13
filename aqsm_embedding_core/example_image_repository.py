"""Worked-example images and expected outputs used by tests and demos."""

from typing import Dict, List, Tuple

from .types import BitMatrix, ImageMatrix


class ExampleImageRepository:
    """Provide the tiny worked-example images and expected results from the markdown notes.

    Inputs:
        None. The values are stored directly in the class.

    Outputs:
        Ready-to-use image matrices for tests, demos, and validation.
    """

    @staticmethod
    def worked_example_inputs() -> Tuple[ImageMatrix, ImageMatrix]:
        """Return the watermark and carrier images from the markdown walkthrough.

        Returns:
            A tuple `(watermark_image, carrier_image)`.
        """

        watermark = [
            [130, 200],
            [170, 255],
        ]
        carrier = [
            [212, 47, 133, 88],
            [17, 190, 64, 251],
            [102, 73, 155, 36],
            [240, 121, 12, 201],
        ]
        return watermark, carrier

    @staticmethod
    def expected_bit_planes() -> Dict[str, BitMatrix]:
        """Return the expected bit planes from the markdown walkthrough.

        Returns:
            A dictionary mapping `w1`..`w8` to binary image matrices.
        """

        return {
            "w1": [[0, 0], [0, 1]],
            "w2": [[1, 0], [1, 1]],
            "w3": [[0, 0], [0, 1]],
            "w4": [[0, 1], [1, 1]],
            "w5": [[0, 0], [0, 1]],
            "w6": [[0, 0], [1, 1]],
            "w7": [[0, 1], [0, 1]],
            "w8": [[1, 1], [1, 1]],
        }

    @staticmethod
    def expected_aqsm_watermarks() -> List[BitMatrix]:
        """Return the expected AQSM outputs from the markdown walkthrough.

        Returns:
            A list with the three embedded AQSM watermark images.
        """

        return [
            [
                [0, 0, 1, 0],
                [0, 1, 1, 1],
                [0, 0, 0, 1],
                [0, 1, 1, 1],
            ],
            [
                [0, 0, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
                [0, 1, 0, 1],
            ],
            [
                [0, 0, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
                [1, 1, 1, 1],
            ],
        ]

    @staticmethod
    def expected_xor_matrix() -> BitMatrix:
        """Return the expected `V_eta` matrix from the markdown walkthrough.

        Returns:
            The binary xor matrix for the worked example carrier.
        """

        return [
            [0, 1, 1, 1],
            [0, 0, 1, 1],
            [0, 1, 1, 1],
            [1, 0, 0, 0],
        ]

    @staticmethod
    def expected_intermediate_images() -> Dict[str, ImageMatrix]:
        """Return the expected carrier images after each embedding step.

        Returns:
            A dictionary keyed by `after_bit0`, `after_bit1`, and `after_bit2`.
        """

        return {
            "after_bit0": [
                [213, 46, 133, 88],
                [17, 190, 65, 251],
                [103, 72, 154, 37],
                [240, 120, 12, 200],
            ],
            "after_bit1": [
                [215, 44, 133, 90],
                [19, 188, 65, 251],
                [103, 74, 152, 39],
                [240, 120, 14, 200],
            ],
            "after_bit2": [
                [215, 40, 133, 94],
                [19, 184, 69, 255],
                [99, 78, 156, 39],
                [244, 120, 10, 200],
            ],
        }

    @staticmethod
    def expected_final_image() -> ImageMatrix:
        """Return the expected final watermarked carrier from the markdown walkthrough.

        Returns:
            The final grayscale watermarked carrier image.
        """

        return ExampleImageRepository.expected_intermediate_images()["after_bit2"]

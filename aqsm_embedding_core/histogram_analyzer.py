"""HDWM histogram parameter analyzer."""

from typing import Optional, Sequence

from .histogram_parameters import HistogramParameters
from .image_matrix_validator import ImageMatrixValidator
from .scale_parameters import ScaleParameters


class HistogramAnalyzer:
    """Compute the watermark histogram parameters used by HDWM.

    Inputs:
        Watermark grayscale image, optional `ScaleParameters`, and a denominator mode.

    Outputs:
        A `HistogramParameters` object containing `T_dark`, `T_bright`, `tau1`, and `tau2`.
    """

    def analyze(
        self,
        watermark_image: Sequence[Sequence[int]],
        scale_parameters: Optional[ScaleParameters] = None,
        threshold_lambda: float = 0.5,
        denominator_mode: str = "natural",
    ) -> HistogramParameters:
        """Compute histogram and HDWM parameters for a watermark image.

        Args:
            watermark_image: Square watermark image matrix.
            scale_parameters: Needed only when `denominator_mode` is `"paper"`.
            threshold_lambda: HDWM threshold `lambda`.
            denominator_mode: `"natural"` for pixel count or `"paper"` for the printed formula.

        Returns:
            A `HistogramParameters` object describing the chosen HDWM branch.
        """

        ImageMatrixValidator.validate_grayscale(watermark_image)

        histogram = [0] * 256
        for row in watermark_image:
            for value in row:
                histogram[value] += 1

        dark_count = sum(histogram[:128])
        bright_count = sum(histogram[128:])

        side = len(watermark_image)
        if denominator_mode == "natural":
            denominator = side * side
        elif denominator_mode == "paper":
            if scale_parameters is None:
                raise ValueError("Scale parameters are required when denominator_mode='paper'.")
            denominator = (2 ** scale_parameters.watermark_side_exponent) * (
                2 ** scale_parameters.carrier_side_exponent
            )
        else:
            raise ValueError("denominator_mode must be 'natural' or 'paper'.")

        t_dark = dark_count / denominator
        t_bright = 1 - t_dark

        tau1 = 0 if abs(t_bright - t_dark) < threshold_lambda else 1
        tau2: Optional[int]
        if tau1 == 0:
            tau2 = None
        else:
            dominant_threshold = (1 + threshold_lambda) / 2
            tau2 = 0 if t_dark >= dominant_threshold else 1

        return HistogramParameters(
            histogram=histogram,
            dark_count=dark_count,
            bright_count=bright_count,
            denominator=denominator,
            threshold_lambda=threshold_lambda,
            t_dark=t_dark,
            t_bright=t_bright,
            tau1=tau1,
            tau2=tau2,
        )

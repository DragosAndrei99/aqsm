"""Data object for HDWM histogram parameters."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass(frozen=True)
class HistogramParameters:
    """Histogram-derived parameters used by HDWM.

    Inputs:
        histogram: Pixel count histogram over the range `0..255`.
        dark_count: Number of watermark pixels in `0..127`.
        bright_count: Number of watermark pixels in `128..255`.
        denominator: Normalization denominator used for `T_dark`.
        threshold_lambda: Paper threshold `lambda`.
        t_dark: Cumulative dark probability.
        t_bright: Bright probability.
        tau1: First HDWM branch selector.
        tau2: Second HDWM branch selector, or `None` when tau1 is `0`.

    Outputs:
        A complete record of how the histogram branch was chosen.
    """

    histogram: List[int]
    dark_count: int
    bright_count: int
    denominator: int
    threshold_lambda: float
    t_dark: float
    t_bright: float
    tau1: int
    tau2: Optional[int]

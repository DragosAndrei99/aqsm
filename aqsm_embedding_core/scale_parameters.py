"""Data object for AQSM scale parameters."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ScaleParameters:
    """Scale parameters used by AQSM and embedding.

    Inputs:
        watermark_side_exponent: `m` where watermark side is `2^m`.
        carrier_side_exponent: `n` where carrier side is `2^n`.
        scale_factor: `r = n - m`.
        beta: AQSM helper parameter from the paper.
        alpha: AQSM helper parameter from the paper.
        aggregation_level: QBA aggregation level `d`.
        q_outputs: Number of AQSM outputs after the selected QBA level.

    Outputs:
        A reusable description of the current watermark/carrier scale setup.
    """

    watermark_side_exponent: int
    carrier_side_exponent: int
    scale_factor: int
    beta: int
    alpha: int
    aggregation_level: int
    q_outputs: int

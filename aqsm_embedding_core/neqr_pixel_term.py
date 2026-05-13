"""Data object for one NEQR basis term."""

from dataclasses import dataclass


@dataclass(frozen=True)
class NEQRPixelTerm:
    """One NEQR basis term for a single pixel.

    Inputs:
        grayscale_bits: Eight-bit grayscale value as a bit string.
        y_bits: Row coordinate bit string.
        x_bits: Column coordinate bit string.

    Outputs:
        Instances of this class are part of `NEQREncodedImage.terms`.
    """

    grayscale_bits: str
    y_bits: str
    x_bits: str

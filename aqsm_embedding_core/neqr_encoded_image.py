"""Data object for a conceptual NEQR-encoded image."""

from dataclasses import dataclass
from typing import List

from .neqr_pixel_term import NEQRPixelTerm


@dataclass(frozen=True)
class NEQREncodedImage:
    """Conceptual NEQR encoding of a grayscale image.

    Inputs:
        side_exponent: `s` for an image of size `2^s x 2^s`.
        amplitude: Common amplitude assigned to every basis term.
        terms: Ordered list of pixel basis terms in row-major order.

    Outputs:
        A compact, inspectable representation of the NEQR state.
    """

    side_exponent: int
    amplitude: float
    terms: List[NEQRPixelTerm]

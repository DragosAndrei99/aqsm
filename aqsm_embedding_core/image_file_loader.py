"""Image file loading and PNG export helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

from .image_matrix_validator import ImageMatrixValidator
from .types import ImageMatrix


class ImageFileLoader:
    """Load real image files into AQSM-compatible grayscale matrices.

    Inputs:
        TIFF, PNG, JPEG, or other image files supported by Pillow.

    Outputs:
        Square 8-bit grayscale matrices and PNG preview files.
    """

    @staticmethod
    def _require_pillow():
        try:
            from PIL import Image
        except ImportError as exc:
            raise RuntimeError(
                "Pillow is required for loading real image files. "
                "Install the project dependencies with: pip install -r requirements.txt"
            ) from exc
        return Image

    def load_grayscale(
        self,
        path: str | Path,
        target_side: int | None = None,
    ) -> ImageMatrix:
        """Load an image file as a square 8-bit grayscale matrix.

        Args:
            path: Image file path.
            target_side: Optional square side length to resize to before loading.

        Returns:
            A grayscale matrix with integer pixels in `[0, 255]`.
        """

        Image = self._require_pillow()
        image_path = Path(path)

        with Image.open(image_path) as source_image:
            image = source_image.convert("L")
            if target_side is not None:
                if target_side <= 0 or target_side & (target_side - 1):
                    raise ValueError("target_side must be a positive power of two.")
                resampling = getattr(Image, "Resampling", Image).LANCZOS
                image = image.resize((target_side, target_side), resampling)

            width, height = image.size
            if width != height:
                raise ValueError("Loaded image must be square. Use target_side to resize/crop first.")

            values = list(image.getdata())

        matrix = [
            values[row_start : row_start + width]
            for row_start in range(0, len(values), width)
        ]
        ImageMatrixValidator.validate_grayscale(matrix)
        return matrix

    def save_png(
        self,
        image: Sequence[Sequence[int]],
        path: str | Path,
        scale_binary_to_255: bool = True,
    ) -> str:
        """Save a grayscale or binary image matrix as a PNG preview.

        Args:
            image: Grayscale or binary image matrix.
            path: Output PNG path.
            scale_binary_to_255: Expand binary `0/1` matrices to `0/255`.

        Returns:
            The output path as a string.
        """

        Image = self._require_pillow()
        ImageMatrixValidator.validate_square_power_of_two(image)

        rows = ImageMatrixValidator.clone(image)
        max_value = max(max(row) for row in rows)
        if max_value <= 1 and scale_binary_to_255:
            rows = [[value * 255 for value in row] for row in rows]

        side = len(rows)
        flat_values = [value for row in rows for value in row]
        output_image = Image.new("L", (side, side))
        output_image.putdata(flat_values)

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_image.save(output_path)
        return str(output_path)

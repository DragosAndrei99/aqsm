"""Text rendering and PGM export helpers for image matrices."""

from typing import Sequence

from .image_matrix_validator import ImageMatrixValidator


class ImageDisplay:
    """Display or export grayscale and binary image matrices without external libraries.

    Inputs:
        Image matrices represented as nested Python lists.

    Outputs:
        Pretty-printed text representations or saved ASCII PGM files.
    """

    def render_numeric(self, image: Sequence[Sequence[int]]) -> str:
        """Render an image matrix as aligned numeric text.

        Args:
            image: Grayscale or binary image matrix.

        Returns:
            A multiline string with one row per line.
        """

        return "\n".join(
            "[" + ", ".join(f"{value:3d}" for value in row) + "]"
            for row in image
        )

    def render_binary(
        self,
        image: Sequence[Sequence[int]],
        on_symbol: str = "1",
        off_symbol: str = "0",
    ) -> str:
        """Render a binary image matrix using custom symbols.

        Args:
            image: Binary image matrix.
            on_symbol: Text used for value `1`.
            off_symbol: Text used for value `0`.

        Returns:
            A multiline string showing the binary image.
        """

        ImageMatrixValidator.validate_binary(image)
        return "\n".join(
            "[" + ", ".join(on_symbol if value else off_symbol for value in row) + "]"
            for row in image
        )

    def print_image(
        self,
        label: str,
        image: Sequence[Sequence[int]],
        binary: bool = False,
    ) -> str:
        """Print an image matrix and also return the rendered text.

        Args:
            label: Short title printed above the image.
            image: Grayscale or binary image matrix.
            binary: When `True`, use the binary renderer.

        Returns:
            The rendered text that was printed.
        """

        rendered = self.render_binary(image) if binary else self.render_numeric(image)
        output = f"{label}\n{rendered}"
        print(output)
        return output

    def save_pgm(
        self,
        image: Sequence[Sequence[int]],
        path: str,
        scale_binary_to_255: bool = True,
    ) -> str:
        """Save an image matrix as an ASCII PGM file.

        Args:
            image: Grayscale or binary image matrix.
            path: Output file path.
            scale_binary_to_255: When `True`, binary images are expanded to `0/255`.

        Returns:
            The same output path for convenience.
        """

        ImageMatrixValidator.validate_square_power_of_two(image)
        side = len(image)
        max_value = max(max(row) for row in image)

        if max_value <= 1 and scale_binary_to_255:
            rows = [[value * 255 for value in row] for row in image]
            max_gray = 255
        else:
            rows = ImageMatrixValidator.clone(image)
            max_gray = max(255, max_value)

        with open(path, "w", encoding="utf-8") as handle:
            handle.write("P2\n")
            handle.write(f"{side} {side}\n")
            handle.write(f"{max_gray}\n")
            for row in rows:
                handle.write(" ".join(str(value) for value in row) + "\n")

        return path

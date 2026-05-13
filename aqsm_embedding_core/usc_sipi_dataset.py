"""Tiny USC-SIPI sample downloader for real-image AQSM experiments."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class USCSIPIImageSpec:
    """Description of one downloadable USC-SIPI image."""

    key: str
    image_id: str
    description: str
    side: int
    image_type: str

    @property
    def url(self) -> str:
        """Return the direct USC-SIPI download URL."""

        return f"https://sipi.usc.edu/database/download.php?img={self.image_id}&vol=misc"

    @property
    def filename(self) -> str:
        """Return the local TIFF filename used for this sample."""

        return f"{self.key}.tiff"


class USCSIPISampleDataset:
    """Download a small paper-like subset from USC-SIPI Miscellaneous.

    Inputs:
        A local cache directory.

    Outputs:
        Downloaded TIFF paths for one 256x256 watermark and several 512x512 carriers.
    """

    DATASET_PAGE_URL = "https://sipi.usc.edu/database/?volume=misc"

    SAMPLE_IMAGES = {
        "watermark_moon_256": USCSIPIImageSpec(
            key="watermark_moon_256",
            image_id="5.1.09",
            description="Moon surface, 256x256 grayscale",
            side=256,
            image_type="Gray",
        ),
        "carrier_couple_512": USCSIPIImageSpec(
            key="carrier_couple_512",
            image_id="5.2.08",
            description="Couple, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_bridge_512": USCSIPIImageSpec(
            key="carrier_bridge_512",
            image_id="5.2.10",
            description="Stream and bridge, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_boat_512": USCSIPIImageSpec(
            key="carrier_boat_512",
            image_id="boat.512",
            description="Fishing boat, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
    }

    def __init__(self, cache_directory: str | Path = "example_outputs/usc_sipi_samples") -> None:
        self.cache_directory = Path(cache_directory)

    def download_sample(self, key: str, force: bool = False) -> Path:
        """Download one sample image if it is not already cached.

        Args:
            key: One key from `SAMPLE_IMAGES`.
            force: Redownload even if the local file already exists.

        Returns:
            Local TIFF path.
        """

        if key not in self.SAMPLE_IMAGES:
            available = ", ".join(sorted(self.SAMPLE_IMAGES))
            raise ValueError(f"Unknown USC-SIPI sample '{key}'. Available: {available}.")

        spec = self.SAMPLE_IMAGES[key]
        output_path = self.cache_directory / spec.filename
        if output_path.exists() and not force:
            return output_path

        self.cache_directory.mkdir(parents=True, exist_ok=True)
        request = Request(spec.url, headers={"User-Agent": "AQSM-demo/1.0"})
        with urlopen(request, timeout=60) as response:
            output_path.write_bytes(response.read())
        return output_path

    def download_default_samples(self, force: bool = False) -> dict[str, Path]:
        """Download the default `r = 1` real-image demo samples.

        Returns:
            A mapping containing one watermark and three carrier images.
        """

        return {
            key: self.download_sample(key, force=force)
            for key in (
                "watermark_moon_256",
                "carrier_couple_512",
                "carrier_bridge_512",
                "carrier_boat_512",
            )
        }

    def default_pair(self, force: bool = False) -> tuple[Path, Path]:
        """Download and return the default `(watermark_path, carrier_path)` pair."""

        samples = self.download_default_samples(force=force)
        return samples["watermark_moon_256"], samples["carrier_couple_512"]

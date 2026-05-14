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
        Downloaded TIFF paths for 256x256 watermarks and 512x512 carriers.
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
        "watermark_aerial_256": USCSIPIImageSpec(
            key="watermark_aerial_256",
            image_id="5.1.10",
            description="Aerial, 256x256 grayscale",
            side=256,
            image_type="Gray",
        ),
        "watermark_airplane_256": USCSIPIImageSpec(
            key="watermark_airplane_256",
            image_id="5.1.11",
            description="Airplane, 256x256 grayscale",
            side=256,
            image_type="Gray",
        ),
        "watermark_clock_256": USCSIPIImageSpec(
            key="watermark_clock_256",
            image_id="5.1.12",
            description="Clock, 256x256 grayscale",
            side=256,
            image_type="Gray",
        ),
        "watermark_resolution_chart_256": USCSIPIImageSpec(
            key="watermark_resolution_chart_256",
            image_id="5.1.13",
            description="Resolution chart, 256x256 grayscale",
            side=256,
            image_type="Gray",
        ),
        "watermark_chemical_plant_256": USCSIPIImageSpec(
            key="watermark_chemical_plant_256",
            image_id="5.1.14",
            description="Chemical plant, 256x256 grayscale",
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
        "carrier_aerial_512": USCSIPIImageSpec(
            key="carrier_aerial_512",
            image_id="5.2.09",
            description="Aerial, 512x512 grayscale",
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
        "carrier_truck_512": USCSIPIImageSpec(
            key="carrier_truck_512",
            image_id="7.1.01",
            description="Truck, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_airplane_512": USCSIPIImageSpec(
            key="carrier_airplane_512",
            image_id="7.1.02",
            description="Airplane, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_tank_1_512": USCSIPIImageSpec(
            key="carrier_tank_1_512",
            image_id="7.1.03",
            description="Tank, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_car_apcs_1_512": USCSIPIImageSpec(
            key="carrier_car_apcs_1_512",
            image_id="7.1.04",
            description="Car and APCs, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_truck_apcs_1_512": USCSIPIImageSpec(
            key="carrier_truck_apcs_1_512",
            image_id="7.1.05",
            description="Truck and APCs, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_truck_apcs_2_512": USCSIPIImageSpec(
            key="carrier_truck_apcs_2_512",
            image_id="7.1.06",
            description="Truck and APCs, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_tank_2_512": USCSIPIImageSpec(
            key="carrier_tank_2_512",
            image_id="7.1.07",
            description="Tank, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_apc_512": USCSIPIImageSpec(
            key="carrier_apc_512",
            image_id="7.1.08",
            description="APC, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_tank_3_512": USCSIPIImageSpec(
            key="carrier_tank_3_512",
            image_id="7.1.09",
            description="Tank, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_car_apcs_2_512": USCSIPIImageSpec(
            key="carrier_car_apcs_2_512",
            image_id="7.1.10",
            description="Car and APCs, 512x512 grayscale",
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
        "carrier_gray_wedge_512": USCSIPIImageSpec(
            key="carrier_gray_wedge_512",
            image_id="gray21.512",
            description="21 level step wedge, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
        "carrier_ruler_512": USCSIPIImageSpec(
            key="carrier_ruler_512",
            image_id="ruler.512",
            description="Pixel ruler, 512x512 grayscale",
            side=512,
            image_type="Gray",
        ),
    }

    WATERMARK_OPTION_KEYS = (
        "watermark_moon_256",
        "watermark_aerial_256",
        "watermark_airplane_256",
        "watermark_clock_256",
        "watermark_resolution_chart_256",
        "watermark_chemical_plant_256",
    )

    CARRIER_OPTION_KEYS = (
        "carrier_couple_512",
        "carrier_aerial_512",
        "carrier_bridge_512",
        "carrier_truck_512",
        "carrier_airplane_512",
        "carrier_tank_1_512",
        "carrier_car_apcs_1_512",
        "carrier_truck_apcs_1_512",
        "carrier_truck_apcs_2_512",
        "carrier_tank_2_512",
        "carrier_apc_512",
        "carrier_tank_3_512",
        "carrier_car_apcs_2_512",
        "carrier_boat_512",
        "carrier_gray_wedge_512",
        "carrier_ruler_512",
    )

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

    def watermark_options(self) -> dict[str, USCSIPIImageSpec]:
        """Return supported 256x256 grayscale watermark options."""

        return {key: self.SAMPLE_IMAGES[key] for key in self.WATERMARK_OPTION_KEYS}

    def carrier_options(self) -> dict[str, USCSIPIImageSpec]:
        """Return supported 512x512 grayscale carrier options."""

        return {key: self.SAMPLE_IMAGES[key] for key in self.CARRIER_OPTION_KEYS}

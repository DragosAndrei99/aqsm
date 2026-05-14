"""AQSM embedding package with one module per class."""

from .types import BitMatrix, ImageMatrix
from .neqr_pixel_term import NEQRPixelTerm
from .neqr_encoded_image import NEQREncodedImage
from .scale_parameters import ScaleParameters
from .histogram_parameters import HistogramParameters
from .aqsm_build_result import AQSMBuildResult
from .embedding_result import EmbeddingResult
from .extraction_result import ExtractionResult
from .embedding_context import EmbeddingContext
from .image_matrix_validator import ImageMatrixValidator
from .neqr_encoder import NEQREncoder
from .scale_parameter_calculator import ScaleParameterCalculator
from .histogram_analyzer import HistogramAnalyzer
from .bit_plane_decomposer import BitPlaneDecomposer
from .quantum_block_aggregator import QuantumBlockAggregator
from .aqsm_watermark_builder import AQSMWatermarkBuilder
from .carrier_xor_calculator import CarrierXorCalculator
from .hdwm_embedder import HDWMEmbedder
from .hdwm_extractor import HDWMExtractor
from .image_display import ImageDisplay
from .image_file_loader import ImageFileLoader
from .quantum_refiner import QuantumRefiner
from .watermark_reconstructor import WatermarkReconstructor
from .example_image_repository import ExampleImageRepository
from .embedding_pipeline import EmbeddingPipeline
from .embedding_report_writer import EmbeddingReportWriter
from .usc_sipi_dataset import USCSIPIImageSpec, USCSIPISampleDataset

__all__ = [
    "AQSMBuildResult",
    "AQSMWatermarkBuilder",
    "BitMatrix",
    "BitPlaneDecomposer",
    "CarrierXorCalculator",
    "EmbeddingContext",
    "EmbeddingPipeline",
    "EmbeddingReportWriter",
    "EmbeddingResult",
    "ExampleImageRepository",
    "ExtractionResult",
    "HDWMEmbedder",
    "HDWMExtractor",
    "HistogramAnalyzer",
    "HistogramParameters",
    "ImageDisplay",
    "ImageFileLoader",
    "ImageMatrix",
    "ImageMatrixValidator",
    "NEQREncodedImage",
    "NEQREncoder",
    "NEQRPixelTerm",
    "QuantumBlockAggregator",
    "QuantumRefiner",
    "ScaleParameterCalculator",
    "ScaleParameters",
    "USCSIPIImageSpec",
    "USCSIPISampleDataset",
    "WatermarkReconstructor",
]

__version__ = "0.2.1"

# Core processors
from .claim_processor import ClaimProcessor
from .pendency_processor import PendencyProcessor
from .multi_source_aggregator import MultiSourceReportAggregator
from .anomaly_detector import AnomalyDetector
from .daily_reporter import DailyReporter
from .word_reporter import WordReporter
from .estmst_analyzer import EstmstAnalyzer
from .gui import EPFToolsGUI
from .performance_analyzer import PerformanceAnalyzer
from .website_scraper import WebsiteScraper

# PDF utilities
from .pdf_report import PDFReport
from .pdf_tools import PDFTools
from .pdf_ocr import PDFOCR

# Data utilities
from .df_styler import DataFrameStyler
from .excel_merger import ExcelMerger
from .validation_utils import ValidationUtils
from . import periodicity

# Help utility
from .help import show_help

# ML utilities (optional, requires scikit-learn)
try:
    from .rejection_categorizer import RejectionCategorizer
    _rejection_categorizer_available = True
except ImportError:
    _rejection_categorizer_available = False

__all__ = [
    'ClaimProcessor',
    'PendencyProcessor',
    'MultiSourceReportAggregator',
    'AnomalyDetector',
    'DailyReporter',
    'WordReporter',
    'EstmstAnalyzer',
    'EPFToolsGUI',
    'PerformanceAnalyzer',
    'WebsiteScraper',
    'PDFReport',
    'PDFTools',
    'PDFOCR',
    'DataFrameStyler',
    'ExcelMerger',
    'ValidationUtils',
    'periodicity',
    'show_help',
]

if _rejection_categorizer_available:
    __all__.append('RejectionCategorizer')

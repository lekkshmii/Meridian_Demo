"""
Meridian M&A Intelligence Platform
AI-Powered M&A Target Screening & Strategic Analysis
"""

from .synthetic_data import SyntheticDataGenerator
from .screening import ScreeningEngine
from .valuation import ValuationEngine
from .intelligence import IntelligenceAnalyzer

__version__ = "1.0.0"
__all__ = [
    "SyntheticDataGenerator",
    "ScreeningEngine", 
    "ValuationEngine",
    "IntelligenceAnalyzer"
]

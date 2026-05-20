"""
AxisBlueprint: A toolbox for designing scientific figure layouts.
"""

__version__ = "0.1.0"

from .app import BlueprintBuilder
from .export import figure_from_layout
from .designer import LayoutDesigner
from .models import AxisBox

# Historical alias.
FigureFromLayout = figure_from_layout

__all__ = [
    "AxisBox",
    "BlueprintBuilder",
    "FigureFromLayout",
    "LayoutDesigner",
    "figure_from_layout",
]

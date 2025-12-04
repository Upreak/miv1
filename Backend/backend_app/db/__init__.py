"""
Database module initialization
"""

# Import database components
from . import base, session

# Export database components for easy access
__all__ = ["base", "session"]
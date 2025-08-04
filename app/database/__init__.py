"""
Database package for Web-Based Project Architect
"""

from .database import get_database, init_database
from .models import Base

__all__ = ["get_database", "init_database", "Base"] 
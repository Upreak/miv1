"""
Legacy File Extraction Service - DEPRECATED

This service is deprecated and will be removed in a future version.
Use the new extraction API endpoint at POST /api/v1/extraction/run instead.
"""
import logging
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class ExtractionService:
    """DEPRECATED: Use the new extraction API endpoint instead"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        logger.warning("ExtractionService is deprecated. Use POST /api/v1/extraction/run instead.")
    
    async def extract_text(
        self, 
        file_path: str, 
        filename: str, 
        user_id: str
    ) -> Dict[str, Any]:
        """
        DEPRECATED: This method will be removed.
        Use the new extraction API endpoint instead.
        """
        raise NotImplementedError(
            "ExtractionService.extract_text is deprecated. "
            "Use POST /api/v1/extraction/run instead."
        )
    
    async def get_available_providers(self) -> list:
        """Return empty list - use new API instead"""
        return []
    
    async def validate_file(self, file_path: str, filename: str) -> bool:
        """Always return False - use new API instead"""
        return False
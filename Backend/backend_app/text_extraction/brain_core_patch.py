"""
brain_core_patch.py

Patch for Backend/backend_app/brain_module/brain_core.py to integrate consolidated extractor.

This file shows the exact changes needed to integrate the consolidated extractor
with OpenCV preprocessing, PaddleOCR fallback, and Logbook system.
"""

# PATCH INSTRUCTIONS:
# 
# 1. Open Backend/backend_app/brain_module/brain_core.py
# 2. Find the _extract_text method (around line 267)
# 3. Replace the entire _extract_text method with the code below
# 4. Save the file

def _extract_text(self, file_path: Path) -> Optional[str]:
    """
    Extract text from file using the consolidated extractor.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Extracted text or None on failure
    """
    try:
        # Import the consolidated extractor
        from backend_app.text_extraction.consolidated_extractor import extract_with_logging
        
        # Use consolidated extractor with logging
        result = extract_with_logging(
            file_path=file_path,
            metadata={
                "source": "brain_core",
                "file_path": str(file_path)
            },
            quality_threshold=70.0  # Adjust based on your needs
        )
        
        if result["success"]:
            self.logger.info(f"Text extraction successful using {result['module']} for {file_path}")
            self.logger.debug(f"Quality score: {result['score']:.1f}, extracted length: {len(result['text'])}")
            return result["text"]
        else:
            self.logger.warning(f"Text extraction failed for {file_path}. Module: {result.get('module', 'none')}")
            return None
            
    except Exception as e:
        self.logger.error(f"Error extracting text from {file_path}: {e}")
        return None

# ADDITIONAL NOTES:
#
# 1. The consolidated extractor will automatically:
#    - Try your existing extractors first (unstructured, PyPDF2, etc.)
#    - Fall back to OpenCV preprocessing + Tesseract if needed
#    - Fall back to PaddleOCR if needed
#    - Log every attempt to logs/extraction_logbook.db
#    - Return the best result based on quality score
#
# 2. To analyze extraction results, run:
#    python backend_app/text_extraction/analyze_logbook.py
#
# 3. To adjust quality threshold, modify the quality_threshold parameter
#    in the extract_with_logging call above.
#
# 4. The logbook will track:
#    - Which module succeeded for each file
#    - Quality scores for each attempt
#    - Success/failure rates by module
#    - File sizes and page counts
#    - Attempt sequences and timing
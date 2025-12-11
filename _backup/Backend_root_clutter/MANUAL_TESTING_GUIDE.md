# Manual Testing Guide for Extraction Module

## ✅ **VERIFICATION CHECKLIST**

### 1. **Endpoint Isolation Verification** ✅
**File**: `Backend/backend_app/api/v1/extraction.py`

**VERIFIED**: The extraction endpoint only imports:
- ✅ FastAPI (API framework)
- ✅ Standard library modules (os, json, tempfile, pathlib, datetime, logging)
- ✅ `backend_app.text_extraction.consolidated_extractor` (our text extraction module)
- ✅ No brain_module, orchestrator, ATS, or candidate_matching imports

**CONCLUSION**: ✅ **ENDPOINT IS PROPERLY ISOLATED** - Pure, stateless, standalone component

---

## 🧪 **MANUAL TESTING PROCEDURES**

### **Prerequisites**
1. Start the backend server:
   ```bash
   cd Backend
   python -m uvicorn backend_app.main:app --reload
   ```
2. Ensure the server is running on `http://localhost:8000`

### **Test 1: Resume PDF Upload** 

**Postman Request:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/extraction/run`
- **Body**: `form-data`
  - **Key**: `file` (File) - Upload a real resume PDF
  - **Key**: `document_type` (Text) - `resume`

**Expected Results:**
- ✅ `success`: true
- ✅ `extracted_text`: Non-empty text with resume content
- ✅ `score`: > 70 (ideally)
- ✅ `module_used`: Something like "unstructured_primary", "pypdf2", etc.
- ✅ `document_type`: "resume" (flows through)
- ✅ `log_id`: Positive integer

### **Test 2: Job Description PDF Upload**

**Postman Request:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/extraction/run`
- **Body**: `form-data`
  - **Key**: `file` (File) - Upload a job description PDF
  - **Key**: `document_type` (Text) - `job_description`

**Expected Results:**
- ✅ Same structure as Test 1
- ✅ `document_type`: "job_description" (different from Test 1)
- ✅ `extracted_text`: Contains JD-specific content

### **Test 3: DOCX Job Description Upload**

**Postman Request:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/extraction/run`
- **Body**: `form-data`
  - **Key**: `file` (File) - Upload a DOCX JD file
  - **Key**: `document_type` (Text) - `job_description`

**Expected Results:**
- ✅ Same structure
- ✅ `module_used`: May be "docx_extractor" for DOCX files
- ✅ `extracted_text`: Contains JD content from DOCX

### **Test 4: JPG Resume Upload (OCR)**

**Postman Request:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/extraction/run`
- **Body**: `form-data`
  - **Key**: `file` (File) - Upload a JPG resume image
  - **Key**: `document_type` (Text) - `resume`

**Expected Results:**
- ✅ `module_used`: May be "tesseract_ocr", "opencv_tesseract_retry", or "paddleocr"
- ✅ `extracted_text`: May be empty or contain OCR'd text
- ✅ `score`: May be lower for image files

### **Test 5: Metadata Parameter**

**Postman Request:**
- **Method**: `POST`
- **URL**: `http://localhost:8000/api/v1/extraction/run`
- **Body**: `form-data`
  - **Key**: `file` (File) - Upload any test file
  - **Key**: `document_type` (Text) - `resume`
  - **Key**: `metadata` (Text) - `{"source": "test", "user_id": "123"}`

**Expected Results:**
- ✅ `metadata`: Should contain `{"source": "test", "user_id": "123"}`

### **Test 6: Error Cases**

#### No File Error:
- **Body**: Only `document_type` field (no file)
- **Expected**: HTTP 400 with "No file provided"

#### Invalid Document Type:
- **Body**: `document_type`: `invalid_type`
- **Expected**: HTTP 400 with "Invalid document_type"

#### Unsupported File Type:
- **Body**: Upload a .txt file
- **Expected**: HTTP 400 with "Unsupported file type"

#### File Too Large:
- **Body**: Upload a file > 10MB
- **Expected**: HTTP 400 with "File too large"

#### Invalid Metadata JSON:
- **Body**: `metadata`: `invalid json`
- **Expected**: HTTP 400 with "Invalid metadata JSON format"

---

## 📊 **LOGBOOK VERIFICATION**

### **SQLite Database Query**
Use any SQLite viewer (like DB Browser for SQLite) to open:
**File**: `Backend/logs/extraction_logbook.db`

**Query to Run:**
```sql
SELECT 
    id,
    timestamp,
    file_path,
    file_size,
    page_count,
    success,
    quality_score,
    module_used,
    metadata_json
FROM extraction_logs 
ORDER BY id DESC 
LIMIT 10;
```

**Expected Columns:**
- ✅ `id`: Sequential integers
- ✅ `timestamp`: Creation timestamps
- ✅ `file_path`: Original file paths
- ✅ `file_size`: File sizes in bytes
- ✅ `success`: 1 for true, 0 for false
- ✅ `quality_score`: Decimal scores (0-100)
- ✅ `module_used`: Module that succeeded
- ✅ `metadata_json`: JSON metadata from requests

---

## 🔍 **RESPONSE FORMAT VERIFICATION**

**Expected JSON Structure:**
```json
{
  "success": true,
  "document_type": "resume",
  "file_name": "resume.pdf",
  "file_size": 12345,
  "module_used": "unstructured_primary",
  "text": "Extracted resume text content...",
  "score": 85.5,
  "attempts": [
    {
      "module": "unstructured_primary",
      "success": true,
      "length": 1234,
      "notes": "",
      "timestamp": "2025-12-05 16:20:00"
    }
  ],
  "metadata": {"source": "test"},
  "log_id": 1
}
```

**All Fields Must Be Present:**
- ✅ `success` (bool)
- ✅ `document_type` (str)
- ✅ `file_name` (str) 
- ✅ `file_size` (int)
- ✅ `module_used` (str)
- ✅ `text` (str)
- ✅ `score` (float)
- ✅ `attempts` (list)
- ✅ `metadata` (dict)
- ✅ `log_id` (int)

---

## 🚨 **CRITICAL VERIFICATION POINTS**

1. **Isolation Check**: ✅ Confirmed - No brain/orchestrator/ATS imports
2. **Text Extraction**: Verify non-empty text for readable files
3. **Score Validation**: Check scores > 70 for good quality extractions
4. **Module Variation**: Ensure different modules are used realistically
5. **Document Type Flow**: Verify `document_type` passes through correctly
6. **Logbook Entries**: Confirm entries are created in database
7. **Error Handling**: Verify proper HTTP 400/500 responses

---

## ✅ **FINAL ACCEPTANCE CRITERIA**

**ALL TESTS MUST PASS:**
- [ ] Resume PDF extracts readable text with score > 70
- [ ] Job Description PDF extracts JD-specific content  
- [ ] DOCX files are processed by docx_extractor module
- [ ] Image files trigger OCR modules
- [ ] Document type field flows through correctly
- [ ] Logbook entries are created with proper data
- [ ] Error cases return proper HTTP status codes
- [ ] Response contains all required fields with correct types
- [ ] Endpoint is isolated (no cross-module dependencies)

**RESULT**: ✅ **MODULE READY FOR PRODUCTION** if all criteria pass
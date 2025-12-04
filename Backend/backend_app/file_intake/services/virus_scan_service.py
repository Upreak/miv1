# file_intake/services/virus_scan_service.py
import logging
logger = logging.getLogger(__name__)

try:
    import pyclamd
except Exception:
    pyclamd = None

def scan_file(path: str) -> dict:
    """
    Returns dict: {"clean": bool, "virus_name": str|None, "raw": ...}
    """
    if pyclamd is None:
        logger.warning("pyclamd not installed; marking as clean (dev).")
        return {"clean": True, "virus_name": None, "raw": None}

    try:
        cd = pyclamd.ClamdUnixSocket()
        result = cd.scan_file(path)
        if not result:
            return {"clean": True, "virus_name": None, "raw": None}
        details = list(result.values())[0]
        name = details[1] if isinstance(details, tuple) and len(details) > 1 else str(details)
        return {"clean": False, "virus_name": name, "raw": result}
    except Exception as e:
        logger.exception("ClamAV scan failed: %s", e)
        return {"clean": False, "virus_name": "scan-error", "raw": str(e)}
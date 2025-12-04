# file_intake/services/brain_parse_service.py
def parse_text_to_profile(text: str, tag: str = "resume"):
    """
    Replace with your brain module call. This is a thin wrapper.
    """
    try:
        from backend_app.brain_module.client import parse_text  # adapt to your client
        return parse_text(text, tag=tag)
    except Exception:
        # fallback: return empty parsed structure
        return {"name": None, "skills": [], "work_history": [], "education": [], "full_text": text}
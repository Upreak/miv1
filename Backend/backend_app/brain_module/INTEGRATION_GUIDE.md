# Brain Module Integration Guide

This guide shows how to integrate the new Brain Module with your existing system.

## Quick Start

1. **Install Dependencies**
   ```bash
   cd Backend/backend_app/brain_module
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Add the following to your `.env` file:
   ```bash
   # Number of providers to use
   BRAIN_PROVIDER_COUNT=3
   
   # Provider 1 - OpenAI (Primary)
   PROVIDER1_TYPE=openai
   PROVIDER1_KEY=sk-your-openai-key
   PROVIDER1_MODEL=gpt-4o-mini
   
   # Provider 2 - Gemini (Secondary)
   PROVIDER2_TYPE=gemini
   PROVIDER2_KEY=your-gemini-api-key
   PROVIDER2_MODEL=gemini-1.5-pro
   
   # Provider 3 - Groq (Tertiary)
   PROVIDER3_TYPE=groq
   PROVIDER3_KEY=your-groq-api-key
   PROVIDER3_MODEL=mixtral-8x7b-32768
   
   # Usage limits (optional)
   BRAIN_PROVIDER_DAILY_LIMIT=1000
   BRAIN_PROVIDER_COOLDOWN_SECONDS=86400
   ```

3. **Test Integration**
   ```python
   # Test the brain module
   from backend_app.brain_module.brain_service import BrainSvc
   
   # Test with sample resume text
   qitem = {
       "qid": "test-resume-001",
       "text": "Sample resume text here...",
       "intake_type": "resume",
       "meta": {"source": "email", "filename": "resume.pdf"}
   }
   
   result = BrainSvc.process(qitem)
   print("Success:", result.get("success"))
   print("Provider used:", result.get("provider"))
   print("Response:", result.get("response")[:200], "...")
   ```

## Integration with Existing Code

### Option 1: Direct Import (Recommended)

Replace your existing LLM calls with the brain module:

**Before:**
```python
# Old code - direct OpenAI call
import openai
openai.api_key = os.getenv('OPENAI_API_KEY')

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}]
)
```

**After:**
```python
# New code - Brain Module
from backend_app.brain_module.brain_service import BrainSvc

qitem = {
    "qid": unique_id,
    "text": extracted_text,
    "intake_type": "resume",  # or "jd" or "chat"
    "meta": {"source": source, "filename": filename}
}

result = BrainSvc.process(qitem)
if result["success"]:
    llm_response = result["response"]
    # Use the response...
else:
    # Handle failure...
    print(f"All providers failed: {result['error']}")
```

### Option 2: Gradual Migration

For gradual migration, you can wrap existing functions:

```python
# wrapper.py - Compatibility layer
def parse_resume_with_brain_module(text, source="text", filename=None):
    """Wrapper that uses brain module for resume parsing"""
    qitem = {
        "qid": generate_unique_id(),
        "text": text,
        "intake_type": "resume",
        "meta": {"source": source, "filename": filename}
    }
    
    result = BrainSvc.process(qitem)
    if result["success"]:
        return result["response"]
    else:
        # Fallback to old method if brain module fails
        return parse_resume_old_way(text)
```

## Environment Setup

### Django Integration

Add to your Django settings or app startup:

```python
# backend_app/app.py or settings.py
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv(Path(__file__).resolve().parent / ".env")

# Verify brain module can access env vars
print("OpenAI Key loaded:", bool(os.getenv('PROVIDER1_KEY')))
print("Gemini Key loaded:", bool(os.getenv('PROVIDER2_KEY')))
print("Groq Key loaded:", bool(os.getenv('PROVIDER3_KEY')))
```

### Requirements Addition

Add to your main `requirements.txt`:
```
# Existing requirements...
# Brain Module requirements
requests
python-dotenv
google-generativeai
openai
groq
pytz
jinja2
```

## Migration Examples

### Resume Processing Migration

**Current Workflow:**
```python
def process_resume_upload(file_path):
    extracted_text = extract_text_from_file(file_path)
    parsed_data = openai_api_call(extracted_text)  # Direct API call
    save_to_database(parsed_data)
```

**New Workflow:**
```python
def process_resume_upload(file_path):
    extracted_text = extract_text_from_file(file_path)
    qitem = {
        "qid": str(uuid.uuid4()),
        "text": extracted_text,
        "intake_type": "resume",
        "meta": {"source": "upload", "filename": file_path}
    }
    
    result = BrainSvc.process(qitem)
    if result["success"]:
        parsed_data = parse_json_response(result["response"])
        save_to_database(parsed_data)
        log_provider_usage(result["provider"])
    else:
        # Handle failure - backup providers will be tried automatically
        logger.error(f"Brain processing failed: {result['error']}")
```

### Job Description Processing

```python
def process_job_description(jd_text, client_id):
    qitem = {
        "qid": f"jd-{client_id}-{int(time.time())}",
        "text": jd_text,
        "intake_type": "jd",
        "meta": {"client_id": client_id}
    }
    
    result = BrainSvc.process(qitem)
    return result["response"] if result["success"] else None
```

## Error Handling Best Practices

1. **Always check success flag:**
   ```python
   result = BrainSvc.process(qitem)
   if not result["success"]:
       # Log and handle appropriately
       logger.error(f"LLM processing failed: {result['error']}")
       return None
   ```

2. **Monitor provider usage:**
   ```python
   # Check usage before processing
   from backend_app.brain_module.providers.provider_usage import ProviderUsageManager
   
   usage_manager = ProviderUsageManager()
   daily_usage = usage_manager.get_state("provider1_openai")["count"]
   if daily_usage >= daily_limit:
       logger.warning("Daily limit reached for OpenAI provider")
   ```

3. **Implement circuit breakers:**
   ```python
   def is_system_healthy():
       # Check if at least one provider is available
       for provider_slot in range(1, BRAIN_PROVIDER_COUNT + 1):
           if usage_manager.can_use(f"provider{provider_slot}_provider", daily_limit):
               return True
       return False
   ```

## Monitoring and Logging

### Provider Usage Tracking

The brain module automatically tracks:
- Daily request counts per provider
- Cooldown periods on errors
- Success/failure rates

Access usage data:
```python
from backend_app.brain_module.providers.provider_usage import ProviderUsageManager

manager = ProviderUsageManager()
provider_states = {}
for i in range(1, BRAIN_PROVIDER_COUNT + 1):
    provider_id = f"provider{i}_provider"
    provider_states[provider_id] = manager.get_state(provider_id)
```

### Log Monitoring

Monitor these log patterns:
- `"Attempting provider"` - Shows which providers are being tried
- `"Provider.*failed"` - Indicates provider issues
- `"All providers failed"` - System-wide outage
- `"Skipping.*(limit or cooldown)"` - Rate limiting active

## Performance Considerations

1. **Cache successful responses** for identical inputs
2. **Monitor provider response times** 
3. **Implement request queuing** for high-volume scenarios
4. **Consider async processing** for better throughput

## Troubleshooting

### Common Issues

1. **Import Error: "No module named 'google.generativeai'"**
   - Solution: `pip install google-generativeai`

2. **"No provider configured at slot X"**
   - Solution: Check your `.env` file has all required `PROVIDER{n}_*` variables

3. **"Unsupported provider type"**
   - Solution: Use only "openai", "gemini", or "groq" as PROVIDER{n}_TYPE

4. **"All providers failed"**
   - Check API keys are valid
   - Verify internet connectivity
   - Check provider status pages

### Debug Mode

Enable debug logging:
```python
import logging
logging.getLogger("brain_module").setLevel(logging.DEBUG)
```

## Production Deployment

1. **Environment Variables**: Use secure secret management
2. **Monitoring**: Set up alerts for provider failures
3. **Backup Providers**: Ensure at least 2-3 working providers
4. **Rate Limiting**: Adjust daily limits based on usage patterns
5. **Health Checks**: Monitor system health regularly

## Support

For issues or questions:
1. Check the logs first
2. Verify environment setup
3. Test individual providers
4. Review this documentation
5. Contact the development team with specific error messages
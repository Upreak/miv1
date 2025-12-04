# Brain Module

This module is the LLM Gateway: build prompts, call providers with fallback, and return results.

## Installation

Install dependencies:
```bash
pip install -r requirements.txt
```
or:
```bash
pip install google-generativeai openai groq python-dotenv requests pytz
```

## Configuration

Configure `.env` with providers:

```bash
# number of configured providers (max attempts)
BRAIN_PROVIDER_COUNT=3

# Provider slot format:
# PROVIDER{n}_TYPE = gemini | groq | openai
# PROVIDER{n}_KEY  = API key for provider n
# PROVIDER{n}_MODEL = optional model name

PROVIDER1_TYPE=openai
PROVIDER1_KEY=sk-...
PROVIDER1_MODEL=gpt-4o-mini

PROVIDER2_TYPE=gemini
PROVIDER2_KEY=ya29...
PROVIDER2_MODEL=gemini-1.5-pro

PROVIDER3_TYPE=groq
PROVIDER3_KEY=groq-...
PROVIDER3_MODEL=mixtral-8x7b-32768
```

## Usage

From central orchestrator:
```python
from backend_app.brain_module.brain_service import BrainSvc
qitem = {"qid":"Q123","text":"...extracted...","intake_type":"resume","meta":{}}
out = BrainSvc.process(qitem)
```

The module persists provider usage state in `brain_module/providers/provider_usage_state.json`.

## Environment Variables

- `BRAIN_PROVIDER_COUNT`: Number of providers to configure (default: 5)
- `BRAIN_PROVIDER_DAILY_LIMIT`: Daily request limit per provider (default: 1000)
- `BRAIN_PROVIDER_COOLDOWN_SECONDS`: Cooldown duration on error (default: 86400/24h)

## Supported Providers

- **Google Gemini**: Using `google-generativeai` SDK
- **Groq**: Using `groq` SDK  
- **OpenAI**: Using `openai` SDK

## Architecture

The brain module follows a clean architecture with the following components:

1. **BrainService**: Main entry point that orchestrates the entire process
2. **PromptBuilder**: Builds appropriate prompts based on intake type (resume/jd/chat)
3. **ProviderOrchestrator**: Manages multiple providers with fallback and usage tracking
4. **Provider Adapters**: Individual adapters for each LLM provider
5. **Usage Manager**: Tracks daily usage and implements cooldowns

## File Structure

```
brain_module/
├── __init__.py
├── brain_service.py
├── README_BRAIN_MODULE.md
│
├── prompt_builder/
│   ├── __init__.py
│   ├── prompt_builder.py
│   ├── provider_formatters.py
│   ├── resume_prompt.py       # (existing file imported)
│   ├── jd_prompt.py           # (existing file imported)
│   └── chat_prompt.py
│
├── providers/
│   ├── __init__.py
│   ├── base_provider.py
│   ├── provider_usage.py
│   ├── provider_orchestrator.py
│   ├── provider_factory.py
│   ├── gemini_provider.py
│   ├── groq_provider.py
│   └── openai_provider.py
│
└── utils/
    ├── __init__.py
    ├── logger.py
    └── time_utils.py
```

## Error Handling

The module implements comprehensive error handling:

- **Provider Failures**: Automatically switches to next provider
- **Rate Limiting**: Respects daily limits and cooldowns
- **Network Errors**: Captures and logs all exceptions
- **Usage Persistence**: Maintains state across restarts

## Logging

All operations are logged with appropriate levels:
- INFO: Normal operations, provider attempts
- WARNING: Provider failures, rate limiting
- ERROR: Complete failures, exceptions

## Integration Notes

- Ensure `.env` is loaded early in your application startup
- The module automatically uses existing `resume_prompt.py` and `jd_prompt.py` files
- Usage state persists to JSON file under `providers/` directory
- Daily counters reset automatically at midnight (local time)
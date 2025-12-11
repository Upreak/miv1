# API Key Setup Guide for Brain Module

## Current Status
Your Brain Module is working correctly but all providers are rate limited due to API key usage limits. Here's how to get fresh API keys:

## Provider Configuration Overview

### 1. OpenRouter (Provider 1 & 4)
**Current Models:**
- Provider 1: `x-ai/grok-4.1-fast:free`
- Provider 4: `z-ai/glm-4.5-air:free`

**Get API Keys:**
1. Visit [OpenRouter.ai](https://openrouter.ai/keys)
2. Sign up/Login with your account
3. Create new API keys
4. Note: Free tier models have usage limits

### 2. Gemini (Provider 2)
**Current Model:** `gemini-2.5-flash-lite`

**Get API Key:**
1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key
5. Note: Free tier has 60 RPM (requests per minute) limit

### 3. Groq (Provider 3)
**Current Model:** `openai/gpt-oss-120b`

**Get API Key:**
1. Visit [Groq Console](https://console.groq.com/)
2. Sign up/Login with your account
3. Navigate to API Keys section
4. Create new API key
5. Note: Free tier has high rate limits but may have usage caps

## Updated .env File Template

Replace your current .env file with this updated template using fresh API keys:

```env
# Provider Management System - Environment Variables
# Copy this file to .env and fill in your actual API keys
BRAIN_PROVIDER_COUNT=4

# OpenRouter Provider 1
PROVIDER1_TYPE=openrouter
PROVIDER1_KEY=YOUR_NEW_OPENROUTER_KEY_1
PROVIDER1_MODEL=x-ai/grok-4.1-fast:free
PROVIDER1_BASEURL=https://openrouter.ai/api/v1

# Gemini Provider 2
PROVIDER2_TYPE=gemini
PROVIDER2_KEY=YOUR_NEW_GEMINI_KEY
PROVIDER2_MODEL=gemini-2.5-flash-lite

# Groq Provider 3
PROVIDER3_TYPE=groq
PROVIDER3_KEY=YOUR_NEW_GROQ_KEY
PROVIDER3_MODEL=openai/gpt-oss-120b

# OpenRouter Provider 4
PROVIDER4_TYPE=openrouter
PROVIDER4_KEY=YOUR_NEW_OPENROUTER_KEY_2
PROVIDER4_MODEL=z-ai/glm-4.5-air:free
PROVIDER4_BASEURL=https://openrouter.ai/api/v1
```

## Testing Steps After Configuration

1. **Replace API Keys:** Update the .env file with your fresh API keys
2. **Clear Usage State:** The system automatically tracks usage, but you can manually reset if needed
3. **Test Brain Module:** Run the test script to verify functionality

## Rate Limit Management Tips

- **Distribute Usage:** Use multiple providers to avoid hitting individual limits
- **Monitor Usage:** The system logs provider usage and automatically manages cooldowns
- **Free Tier Models:** Use free tier models for development/testing
- **Production Keys:** Consider upgrading to paid tiers for production use

## Troubleshooting

If you still encounter issues after updating API keys:

1. **Verify Keys:** Ensure API keys are correctly copied without extra spaces
2. **Check Permissions:** Some providers require additional account setup
3. **Model Availability:** Confirm the selected models are available in your region
4. **Network Access:** Ensure your network can reach the provider APIs

## Next Steps

1. Get fresh API keys from each provider
2. Update your .env file
3. Test the Brain Module with the provided test script
4. Monitor usage patterns to optimize provider selection

The Brain Module architecture is sound and will work correctly once fresh API keys are configured!
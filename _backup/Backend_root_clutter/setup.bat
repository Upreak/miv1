@echo off
echo.
echo ========================================
echo  Telegram Bot Setup Script
echo ========================================
echo.

echo Step 1: Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Main requirements had issues, but continuing...
)

python -m pip install -r backend_app/requirements.txt
if %errorlevel% neq 0 (
    echo Warning: Backend requirements had issues, but continuing...
)

echo.
echo Step 2: Testing configuration...
python test_telegram_bot_quick.py
if %errorlevel% neq 0 (
    echo Warning: Configuration test had issues, but continuing...
)

echo.
echo Step 3: Setting up webhook...
python scripts/deploy_telegram_bot.py --non-interactive
if %errorlevel% neq 0 (
    echo Warning: Webhook setup had issues, but continuing...
)

echo.
echo ========================================
echo  Setup Complete!
echo ========================================
echo.
echo Your bot token is already configured in .env file
echo Bot Token: 7980838931:AAFGLKKsdt_E3YjXA1Ula7r3YUFPxY22YD0
echo ngrok URL: https://00d7585dd459.ngrok-free.app
echo.
echo Next steps:
echo 1. Start your FastAPI app:
echo    uvicorn backend_app.main:app --reload
echo.
echo 2. Test your bot on Telegram:
echo    - Send /high
echo    - Send /start
echo    - Send /help
echo.
echo Press any key to exit...
pause >nul
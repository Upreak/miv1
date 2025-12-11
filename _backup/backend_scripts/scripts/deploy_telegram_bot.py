#!/usr/bin/env python3
"""
Production Deployment Script for Telegram Bot
Automates setup, configuration, and deployment of the Telegram bot
"""

import os
import sys
import json
import logging
import subprocess
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TelegramBotDeployer:
    """Production deployment manager for Telegram bot"""
    
    def __init__(self, env_file: str = ".env"):
        self.env_file = Path(env_file)
        self.config = {}
    
    def load_environment(self) -> Dict[str, Any]:
        """Load current environment configuration"""
        config = {}
        if self.env_file.exists():
            with open(self.env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
        return config
    
    def save_environment(self, config: Dict[str, Any]):
        """Save configuration to environment file"""
        with open(self.env_file, 'w') as f:
            f.write("# Telegram Bot Configuration\n")
            f.write(f"# Generated on {__import__('datetime').datetime.now()}\n\n")
            
            # Telegram settings
            telegram_settings = {
                'TELEGRAM_BOT_TOKEN': config.get('TELEGRAM_BOT_TOKEN', ''),
                'TELEGRAM_WEBHOOK_SECRET': config.get('TELEGRAM_WEBHOOK_SECRET', ''),
                'TELEGRAM_WEBHOOK_URL': config.get('TELEGRAM_WEBHOOK_URL', ''),
                'TELEGRAM_DEBUG_MODE': config.get('TELEGRAM_DEBUG_MODE', 'false'),
                'TELEGRAM_MOCK_MODE': config.get('TELEGRAM_MOCK_MODE', 'false')
            }
            
            f.write("# Telegram Bot Settings\n")
            for key, value in telegram_settings.items():
                f.write(f"{key}={value}\n")
            
            f.write("\n# Other Settings (from existing config)\n")
            for key, value in config.items():
                if key not in telegram_settings and not key.startswith('#'):
                    f.write(f"{key}={value}\n")
        
        logger.info(f"Configuration saved to {self.env_file}")
    
    def validate_token(self, token: str) -> bool:
        """Validate Telegram bot token format"""
        import re
        pattern = r'^\d+:[A-Za-z0-9_-]{35}$'
        return bool(re.match(pattern, token))
    
    def get_bot_token_interactive(self) -> str:
        """Get bot token interactively from user"""
        print("\n" + "="*60)
        print("TELEGRAM BOT TOKEN SETUP")
        print("="*60)
        print("\nTo get your Telegram Bot Token:")
        print("1. Talk to @BotFather on Telegram")
        print("2. Send /newbot command")
        print("3. Follow instructions to create your bot")
        print("4. Copy the token and paste it below")
        print("\n⚠️  Keep your token secret and never commit it to version control!")
        
        while True:
            token = input("\nEnter your Telegram Bot Token: ").strip()
            
            if not token:
                print("❌ Token cannot be empty")
                continue
            
            if self.validate_token(token):
                print("✅ Token format is valid")
                return token
            else:
                print("❌ Invalid token format. Expected format: 123456789:ABCdefGHIjklMNOpqrsTUVwxYZ123abc456")
    
    def get_webhook_url_interactive(self) -> str:
        """Get webhook URL interactively from user"""
        print("\n" + "="*60)
        print("WEBHOOK URL SETUP")
        print("="*60)
        print("\nYour webhook URL should point to your deployed application.")
        print("Examples:")
        print("• https://your-domain.com/api/v1/telegram/webhooks/telegram")
        print("• https://your-app.herokuapp.com/api/v1/telegram/webhooks/telegram")
        print("• https://your-server.com:8000/api/v1/telegram/webhooks/telegram")
        
        while True:
            url = input("\nEnter your webhook URL: ").strip()
            
            if not url:
                print("❌ Webhook URL cannot be empty")
                continue
            
            if self.validate_url(url):
                print("✅ Webhook URL format is valid")
                return url
            else:
                print("❌ Invalid URL format. Please use full URL with https://")
    
    def validate_url(self, url: str) -> bool:
        """Validate URL format"""
        try:
            from urllib.parse import urlparse
            result = urlparse(url)
            return all([result.scheme in ['http', 'https'], result.netloc])
        except Exception:
            return False
    
    def generate_webhook_secret(self) -> str:
        """Generate a secure webhook secret"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        secret = ''.join(secrets.choice(alphabet) for _ in range(32))
        return secret
    
    def setup_environment_interactive(self):
        """Interactive environment setup"""
        print("\n" + "="*60)
        print("TELEGRAM BOT DEPLOYMENT SETUP")
        print("="*60)
        
        # Load existing config
        config = self.load_environment()
        
        # Get bot token
        if 'TELEGRAM_BOT_TOKEN' not in config or not config['TELEGRAM_BOT_TOKEN']:
            config['TELEGRAM_BOT_TOKEN'] = self.get_bot_token_interactive()
        else:
            print(f"\n✅ Using existing bot token from {self.env_file}")
        
        # Get webhook URL
        if 'TELEGRAM_WEBHOOK_URL' not in config or not config['TELEGRAM_WEBHOOK_URL']:
            config['TELEGRAM_WEBHOOK_URL'] = self.get_webhook_url_interactive()
        else:
            print(f"\n✅ Using existing webhook URL from {self.env_file}")
        
        # Generate webhook secret if not exists
        if 'TELEGRAM_WEBHOOK_SECRET' not in config or not config['TELEGRAM_WEBHOOK_SECRET']:
            config['TELEGRAM_WEBHOOK_SECRET'] = self.generate_webhook_secret()
            print(f"\n✅ Generated webhook secret: {config['TELEGRAM_WEBHOOK_SECRET']}")
        
        # Set debug mode
        debug_mode = input("\nEnable debug mode? (y/N): ").strip().lower()
        config['TELEGRAM_DEBUG_MODE'] = 'true' if debug_mode in ['y', 'yes'] else 'false'
        
        # Set mock mode
        mock_mode = input("\nEnable mock mode for testing? (y/N): ").strip().lower()
        config['TELEGRAM_MOCK_MODE'] = 'true' if mock_mode in ['y', 'yes'] else 'false'
        
        # Save configuration
        self.save_environment(config)
        
        return config
    
    def install_dependencies(self):
        """Install required dependencies"""
        print("\n" + "="*60)
        print("INSTALLING DEPENDENCIES")
        print("="*60)
        
        try:
            # Install main requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "Backend/requirements.txt"
            ], check=True)
            
            # Install backend app requirements
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", "Backend/backend_app/requirements.txt"
            ], check=True)
            
            print("✅ Dependencies installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            raise
    
    def run_tests(self):
        """Run test suite"""
        print("\n" + "="*60)
        print("RUNNING TESTS")
        print("="*60)
        
        try:
            # Run unit tests
            result = subprocess.run([
                sys.executable, "-m", "pytest", "Backend/tests/test_telegram_bot.py", "-v"
            ], cwd="Backend", check=False)
            
            if result.returncode == 0:
                print("✅ All tests passed")
            else:
                print("❌ Some tests failed")
                return False
            
        except Exception as e:
            print(f"❌ Error running tests: {e}")
            return False
        
        return True
    
    def validate_configuration(self):
        """Validate the configuration"""
        print("\n" + "="*60)
        print("VALIDATING CONFIGURATION")
        print("="*60)
        
        try:
            # Import and validate settings
            from backend_app.config.telegram_config import telegram_settings
            
            issues = telegram_settings.validate_configuration()
            
            if issues:
                print("❌ Configuration issues found:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            else:
                print("✅ Configuration is valid")
                return True
                
        except Exception as e:
            print(f"❌ Configuration validation failed: {e}")
            return False
    
    def test_bot_connection(self):
        """Test bot connection to Telegram API"""
        print("\n" + "="*60)
        print("TESTING BOT CONNECTION")
        print("="*60)
        
        try:
            import asyncio
            from backend_app.services.telegram_service import telegram_bot_service
            
            async def test_connection():
                await telegram_bot_service.initialize()
                
                # Test bot info
                bot_info = await telegram_bot_service.get_bot_info()
                print(f"✅ Bot info: {bot_info}")
                
                # Test webhook info
                webhook_info = await telegram_bot_service.get_webhook_info()
                print(f"✅ Webhook info: {webhook_info}")
                
                await telegram_bot_service.shutdown()
            
            asyncio.run(test_connection())
            return True
            
        except Exception as e:
            print(f"❌ Bot connection test failed: {e}")
            return False
    
    def set_webhook(self, webhook_url: Optional[str] = None):
        """Set Telegram bot webhook"""
        print("\n" + "="*60)
        print("SETTING WEBHOOK")
        print("="*60)
        
        try:
            import asyncio
            from backend_app.services.telegram_service import telegram_bot_service
            
            async def set_webhook_async():
                await telegram_bot_service.initialize()
                
                result = await telegram_bot_service.set_webhook(webhook_url)
                print(f"✅ Webhook set result: {result}")
                
                await telegram_bot_service.shutdown()
            
            asyncio.run(set_webhook_async())
            return True
            
        except Exception as e:
            print(f"❌ Failed to set webhook: {e}")
            return False
    
    def create_deployment_summary(self, config: Dict[str, Any]):
        """Create deployment summary"""
        summary = {
            "deployment_time": str(__import__('datetime').datetime.now()),
            "bot_token_set": bool(config.get('TELEGRAM_BOT_TOKEN')),
            "webhook_url": config.get('TELEGRAM_WEBHOOK_URL'),
            "webhook_secret_set": bool(config.get('TELEGRAM_WEBHOOK_SECRET')),
            "debug_mode": config.get('TELEGRAM_DEBUG_MODE'),
            "mock_mode": config.get('TELEGRAM_MOCK_MODE'),
            "next_steps": [
                "1. Start your FastAPI application",
                "2. Verify webhook is set correctly",
                "3. Test bot functionality",
                "4. Monitor logs for any issues"
            ]
        }
        
        # Save summary
        with open("telegram_deployment_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\n" + "="*60)
        print("DEPLOYMENT SUMMARY")
        print("="*60)
        print(json.dumps(summary, indent=2))
        
        return summary
    
    def deploy(self, interactive: bool = True, skip_tests: bool = False):
        """Complete deployment process"""
        print("🚀 Starting Telegram Bot Deployment...")
        
        try:
            # Setup environment
            if interactive:
                config = self.setup_environment_interactive()
            else:
                config = self.load_environment()
                if not config:
                    raise ValueError("No configuration found. Run in interactive mode first.")
            
            # Install dependencies
            self.install_dependencies()
            
            # Validate configuration
            if not self.validate_configuration():
                raise ValueError("Configuration validation failed")
            
            # Run tests (optional)
            if not skip_tests:
                if not self.run_tests():
                    raise ValueError("Tests failed")
            
            # Test bot connection
            if not self.test_bot_connection():
                raise ValueError("Bot connection test failed")
            
            # Set webhook
            if config.get('TELEGRAM_WEBHOOK_URL'):
                self.set_webhook(config['TELEGRAM_WEBHOOK_URL'])
            
            # Create deployment summary
            self.create_deployment_summary(config)
            
            print("\n" + "="*60)
            print("🎉 DEPLOYMENT SUCCESSFUL!")
            print("="*60)
            print("\nYour Telegram bot is ready!")
            print(f"• Bot Token: {'Set' if config.get('TELEGRAM_BOT_TOKEN') else 'Not Set'}")
            print(f"• Webhook URL: {config.get('TELEGRAM_WEBHOOK_URL', 'Not Set')}")
            print(f"• Debug Mode: {config.get('TELEGRAM_DEBUG_MODE', 'false')}")
            print(f"• Mock Mode: {config.get('TELEGRAM_MOCK_MODE', 'false')}")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            logger.error(f"Deployment error: {e}", exc_info=True)
            return False


def main():
    """Main deployment script"""
    parser = argparse.ArgumentParser(description="Deploy Telegram Bot")
    parser.add_argument("--env-file", default=".env", help="Environment file path")
    parser.add_argument("--skip-tests", action="store_true", help="Skip running tests")
    parser.add_argument("--non-interactive", action="store_true", help="Non-interactive mode")
    
    args = parser.parse_args()
    
    deployer = TelegramBotDeployer(args.env_file)
    success = deployer.deploy(
        interactive=not args.non_interactive,
        skip_tests=args.skip_tests
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
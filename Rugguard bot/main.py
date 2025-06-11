#!/usr/bin/env python3
"""
RUGGUARD Bot - X Account Trustworthiness Analyzer
Monitors X for trigger phrases and analyzes account trustworthiness
"""

import os
import sys
import logging
from bot import RugguardBot

def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'X_API_KEY',
        'X_API_SECRET', 
        'X_ACCESS_TOKEN',
        'X_ACCESS_TOKEN_SECRET',
        'X_BEARER_TOKEN'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables in your .env file or environment")
        return False
    
    return True

def main():
    """Main entry point"""
    print("🛡️ RUGGUARD Bot - X Account Trustworthiness Analyzer")
    print("=" * 50)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    try:
        # Initialize and run bot
        bot = RugguardBot()
        bot.run()
        
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

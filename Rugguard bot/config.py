import os
from dotenv import load_dotenv

load_dotenv()

# X API Configuration
X_API_KEY = os.getenv('X_API_KEY')
X_API_SECRET = os.getenv('X_API_SECRET')
X_ACCESS_TOKEN = os.getenv('X_ACCESS_TOKEN')
X_ACCESS_TOKEN_SECRET = os.getenv('X_ACCESS_TOKEN_SECRET')
X_BEARER_TOKEN = os.getenv('X_BEARER_TOKEN')

# Bot Configuration
TRIGGER_PHRASE = "riddle me this"
MONITOR_ACCOUNT = "@projectrugguard"  # Optional: monitor specific account
TRUSTED_ACCOUNTS_URL = "https://raw.githubusercontent.com/devsyrem/turst-list/main/list"

# Database Configuration
DATABASE_PATH = "rugguard_bot.db"

# Analysis Thresholds
MIN_TRUSTED_FOLLOWERS = 2
MIN_ACCOUNT_AGE_DAYS = 30
GOOD_FOLLOWER_RATIO_THRESHOLD = 0.1
MAX_FOLLOWING_RATIO = 10.0

# Rate Limiting
ANALYSIS_COOLDOWN_HOURS = 24
MAX_REQUESTS_PER_HOUR = 100

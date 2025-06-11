import requests
import sqlite3
import logging
from datetime import datetime, timedelta
from config import TRUSTED_ACCOUNTS_URL, DATABASE_PATH

class TrustedAccountsManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.trusted_accounts_url = TRUSTED_ACCOUNTS_URL
        self.logger = logging.getLogger(__name__)
    
    def fetch_trusted_accounts(self):
        """Fetch trusted accounts list from GitHub"""
        try:
            response = requests.get(self.trusted_accounts_url, timeout=10)
            response.raise_for_status()
            
            accounts = []
            for line in response.text.strip().split('\n'):
                line = line.strip()
                if line and not line.startswith('#'):
                    # Remove @ symbol if present
                    username = line.replace('@', '').lower()
                    accounts.append(username)
            
            self.logger.info(f"Fetched {len(accounts)} trusted accounts")
            return accounts
            
        except Exception as e:
            self.logger.error(f"Error fetching trusted accounts: {e}")
            return []
    
    def update_trusted_accounts_cache(self):
        """Update local cache of trusted accounts"""
        accounts = self.fetch_trusted_accounts()
        if not accounts:
            return False
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Clear existing cache
            cursor.execute("DELETE FROM trusted_accounts")
            
            # Insert new accounts
            for username in accounts:
                cursor.execute(
                    "INSERT INTO trusted_accounts (username) VALUES (?)",
                    (username,)
                )
            
            conn.commit()
            conn.close()
            
            self.logger.info(f"Updated trusted accounts cache with {len(accounts)} accounts")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating trusted accounts cache: {e}")
            return False
    
    def get_trusted_accounts(self):
        """Get trusted accounts from cache, update if needed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if cache needs update (older than 24 hours)
            cursor.execute(
                "SELECT COUNT(*) FROM trusted_accounts WHERE last_updated > datetime('now', '-24 hours')"
            )
            recent_count = cursor.fetchone()[0]
            
            if recent_count == 0:
                conn.close()
                self.update_trusted_accounts_cache()
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
            
            # Get all trusted accounts
            cursor.execute("SELECT username FROM trusted_accounts")
            accounts = [row[0] for row in cursor.fetchall()]
            
            conn.close()
            return accounts
            
        except Exception as e:
            self.logger.error(f"Error getting trusted accounts: {e}")
            return []
    
    def check_trusted_followers(self, user_followers, min_count=2):
        """Check if user is followed by trusted accounts"""
        trusted_accounts = self.get_trusted_accounts()
        if not trusted_accounts:
            return 0, []
        
        # Convert follower usernames to lowercase for comparison
        follower_usernames = [f.lower() for f in user_followers]
        
        # Find intersection
        trusted_followers = []
        for trusted in trusted_accounts:
            if trusted.lower() in follower_usernames:
                trusted_followers.append(trusted)
        
        return len(trusted_followers), trusted_followers

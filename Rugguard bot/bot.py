import logging
import time
import sqlite3
from datetime import datetime, timedelta
from x_api_client import XAPIClient
from analyzer import AccountAnalyzer
from config import *

class RugguardBot:
    def __init__(self):
        self.setup_logging()
        self.x_client = XAPIClient()
        self.analyzer = AccountAnalyzer(self.x_client)
        self.db_path = DATABASE_PATH
        self.last_search_id = None
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('rugguard_bot.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def get_bot_status(self):
        """Get current bot status and statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get processing statistics
            cursor.execute("SELECT COUNT(*) FROM processed_tweets")
            processed_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            analysis_count = cursor.fetchone()[0]
            
            # Get recent activity (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM processed_tweets 
                WHERE processed_date > datetime('now', '-24 hours')
            """)
            recent_processed = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM analysis_results 
                WHERE analysis_date > datetime('now', '-24 hours')
            """)
            recent_analysis = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                'total_processed': processed_count,
                'total_analysis': analysis_count,
                'recent_processed_24h': recent_processed,
                'recent_analysis_24h': recent_analysis,
                'last_check': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            self.logger.error(f"Error getting bot status: {e}")
            return None

    def log_status(self):
        """Log current bot status"""
        status = self.get_bot_status()
        if status:
            self.logger.info("=" * 50)
            self.logger.info("🛡 RUGGUARD BOT STATUS")
            self.logger.info("=" * 50)
            self.logger.info(f" Total Tweets Processed: {status['total_processed']}")
            self.logger.info(f" Total Analyses Completed: {status['total_analysis']}")
            self.logger.info(f" Recent Activity (24h): {status['recent_processed_24h']} processed, {status['recent_analysis_24h']} analyzed")
            self.logger.info(f" Last Status Check: {status['last_check']}")
            self.logger.info("=" * 50)
    
    def is_tweet_processed(self, tweet_id):
        """Check if tweet has already been processed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM processed_tweets WHERE tweet_id = ?", (tweet_id,))
            result = cursor.fetchone()
            conn.close()
            return result is not None
        except Exception as e:
            self.logger.error(f"Error checking processed tweet: {e}")
            return False
    
    def mark_tweet_processed(self, tweet_id):
        """Mark tweet as processed"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO processed_tweets (tweet_id) VALUES (?)",
                (tweet_id,)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            self.logger.error(f"Error marking tweet as processed: {e}")
    
    def find_trigger_tweets(self):
        """Find tweets containing the trigger phrase"""
        try:
            # Search for mentions of the trigger phrase
            query = f'"{TRIGGER_PHRASE}" -is:retweet'
            tweets = self.x_client.search_mentions(query, max_results=10)
            
            trigger_tweets = []
            for tweet in tweets:
                # Skip if already processed
                if self.is_tweet_processed(tweet['id']):
                    continue
                
                # Check if it's a reply and contains trigger phrase
                if TRIGGER_PHRASE.lower() in tweet['text'].lower():
                    trigger_tweets.append(tweet)
            
            return trigger_tweets
            
        except Exception as e:
            self.logger.error(f"Error finding trigger tweets: {e}")
            return []
    
    def get_original_tweet_author(self, reply_tweet):
        """Get the author of the original tweet being replied to"""
        try:
            # Check if this is a reply
            if not reply_tweet.get('referenced_tweets'):
                return None
            
            # Find the replied-to tweet
            for ref in reply_tweet['referenced_tweets']:
                if ref['type'] == 'replied_to':
                    # Get the original tweet details
                    original_tweet = self.x_client.api_v2.get_tweet(
                        ref['id'],
                        expansions=['author_id'],
                        user_fields=['username']
                    )
                    
                    if original_tweet.data and original_tweet.includes.get('users'):
                        author = original_tweet.includes['users'][0]
                        return {
                            'user_id': author.id,
                            'username': author.username
                        }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting original tweet author: {e}")
            return None
    
    def process_trigger_tweet(self, trigger_tweet):
        """Process a single trigger tweet"""
        try:
            self.logger.info(f"Processing trigger tweet: {trigger_tweet['id']}")
            
            # Get original tweet author
            original_author = self.get_original_tweet_author(trigger_tweet)
            if not original_author:
                self.logger.warning("Could not find original tweet author")
                return False
            
            self.logger.info(f"Analyzing account: @{original_author['username']}")
            
            # Analyze the original author's account
            analysis = self.analyzer.analyze_account(original_author['username'])
            if not analysis:
                self.logger.error("Analysis failed")
                return False
            
            # Format and post reply
            report = self.analyzer.format_analysis_report(analysis)
            reply_id = self.x_client.reply_to_tweet(trigger_tweet['id'], report)
            
            if reply_id:
                self.logger.info(f"Successfully posted analysis reply: {reply_id}")
                self.mark_tweet_processed(trigger_tweet['id'])
                return True
            else:
                self.logger.error("Failed to post reply")
                return False
                
        except Exception as e:
            self.logger.error(f"Error processing trigger tweet: {e}")
            return False
    
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        try:
            self.logger.info("🔄 Starting monitoring cycle...")
            
            # Log status every 10th cycle (roughly every hour)
            if not hasattr(self, 'cycle_count'):
                self.cycle_count = 0
            self.cycle_count += 1
            
            if self.cycle_count % 12 == 0:  # Every hour (12 cycles * 5 min = 60 min)
                self.log_status()
            
            # Find trigger tweets
            trigger_tweets = self.find_trigger_tweets()
            
            if trigger_tweets:
                self.logger.info(f"🎯 Found {len(trigger_tweets)} trigger tweets to process")
            else:
                self.logger.info("👀 No new trigger tweets found")
            
            # Process each trigger tweet
            processed_count = 0
            for tweet in trigger_tweets:
                try:
                    if self.process_trigger_tweet(tweet):
                        processed_count += 1
                    # Add delay between processing to avoid rate limits
                    time.sleep(5)
                except Exception as e:
                    self.logger.error(f"❌ Error processing tweet {tweet['id']}: {e}")
                    continue
            
            if processed_count > 0:
                self.logger.info(f"✅ Successfully processed {processed_count} tweets")
            
            self.logger.info("✨ Monitoring cycle completed")
            
        except Exception as e:
            self.logger.error(f"💥 Error in monitoring cycle: {e}")
    
    def run(self):
        """Main bot loop"""
        self.logger.info("🛡️ RUGGUARD Bot starting...")
        self.logger.info(f"🔍 Monitoring for phrase: '{TRIGGER_PHRASE}'")
        self.logger.info(f"📡 Using X API with rate limiting enabled")
        
        # Log initial status
        self.log_status()
        
        cycle_count = 0
        while True:
            try:
                cycle_count += 1
                self.logger.info(f"🔄 Cycle #{cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
                
                self.run_monitoring_cycle()
                
                # Wait before next cycle (5 minutes)
                self.logger.info("⏳ Waiting 5 minutes before next cycle...")
                time.sleep(300)
                
            except KeyboardInterrupt:
                self.logger.info("👋 Bot stopped by user")
                break
            except Exception as e:
                self.logger.error(f"💥 Unexpected error in main loop: {e}")
                self.logger.info("🔄 Retrying in 1 minute...")
                time.sleep(60)  # Wait 1 minute before retrying

if __name__ == "__main__":
    bot = RugguardBot()
    bot.run()

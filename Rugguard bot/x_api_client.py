import tweepy
import logging
import time
from datetime import datetime, timedelta
from config import *

class XAPIClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.setup_api()
        self.rate_limit_tracker = {}
    
    def setup_api(self):
        """Initialize Twitter API clients"""
        try:
            # API v1.1 client for posting tweets
            auth = tweepy.OAuthHandler(X_API_KEY, X_API_SECRET)
            auth.set_access_token(X_ACCESS_TOKEN, X_ACCESS_TOKEN_SECRET)
            self.api_v1 = tweepy.API(auth, wait_on_rate_limit=True)
            
            # API v2 client for advanced features
            self.api_v2 = tweepy.Client(
                bearer_token=X_BEARER_TOKEN,
                consumer_key=X_API_KEY,
                consumer_secret=X_API_SECRET,
                access_token=X_ACCESS_TOKEN,
                access_token_secret=X_ACCESS_TOKEN_SECRET,
                wait_on_rate_limit=True
            )
            
            # Test authentication
            self.api_v1.verify_credentials()
            self.logger.info("X API authentication successful")
            
        except Exception as e:
            self.logger.error(f"X API authentication failed: {e}")
            raise
    
    def get_user_info(self, username):
        """Get detailed user information"""
        try:
            user = self.api_v2.get_user(
                username=username,
                user_fields=['created_at', 'description', 'public_metrics', 'verified']
            )
            
            if not user.data:
                return None
            
            user_data = user.data
            metrics = user_data.public_metrics
            
            # Calculate account age
            created_at = user_data.created_at
            account_age = (datetime.now(created_at.tzinfo) - created_at).days
            
            return {
                'id': user_data.id,
                'username': user_data.username,
                'name': user_data.name,
                'description': user_data.description or '',
                'created_at': created_at,
                'account_age_days': account_age,
                'followers_count': metrics['followers_count'],
                'following_count': metrics['following_count'],
                'tweet_count': metrics['tweet_count'],
                'verified': getattr(user_data, 'verified', False)
            }
            
        except Exception as e:
            self.logger.error(f"Error getting user info for {username}: {e}")
            return None
    
    def get_user_tweets(self, user_id, max_results=10):
        """Get recent tweets from user"""
        try:
            tweets = self.api_v2.get_users_tweets(
                id=user_id,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'context_annotations']
            )
            
            if not tweets.data:
                return []
            
            tweet_data = []
            for tweet in tweets.data:
                metrics = tweet.public_metrics
                tweet_data.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'created_at': tweet.created_at,
                    'retweet_count': metrics['retweet_count'],
                    'like_count': metrics['like_count'],
                    'reply_count': metrics['reply_count'],
                    'quote_count': metrics['quote_count']
                })
            
            return tweet_data
            
        except Exception as e:
            self.logger.error(f"Error getting tweets for user {user_id}: {e}")
            return []
    
    def get_user_followers(self, user_id, max_results=100):
        """Get user's followers (limited by API)"""
        try:
            followers = self.api_v2.get_users_followers(
                id=user_id,
                max_results=max_results,
                user_fields=['username']
            )
            
            if not followers.data:
                return []
            
            return [follower.username for follower in followers.data]
            
        except Exception as e:
            self.logger.error(f"Error getting followers for user {user_id}: {e}")
            return []
    
    def reply_to_tweet(self, tweet_id, message):
        """Reply to a specific tweet"""
        try:
            # Truncate message if too long
            if len(message) > 280:
                message = message[:277] + "..."
            
            response = self.api_v2.create_tweet(
                text=message,
                in_reply_to_tweet_id=tweet_id
            )
            
            self.logger.info(f"Successfully replied to tweet {tweet_id}")
            return response.data['id']
            
        except Exception as e:
            self.logger.error(f"Error replying to tweet {tweet_id}: {e}")
            return None
    
    def search_mentions(self, query, max_results=10):
        """Search for mentions and replies"""
        try:
            tweets = self.api_v2.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'author_id', 'in_reply_to_user_id', 'referenced_tweets'],
                expansions=['author_id', 'referenced_tweets.id']
            )
            
            if not tweets.data:
                return []
            
            results = []
            for tweet in tweets.data:
                results.append({
                    'id': tweet.id,
                    'text': tweet.text,
                    'author_id': tweet.author_id,
                    'created_at': tweet.created_at,
                    'in_reply_to_user_id': getattr(tweet, 'in_reply_to_user_id', None),
                    'referenced_tweets': getattr(tweet, 'referenced_tweets', [])
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error searching mentions: {e}")
            return []

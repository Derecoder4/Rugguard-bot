import sqlite3
import logging
import re
from datetime import datetime, timedelta
from textblob import TextBlob
from trusted_accounts import TrustedAccountsManager
from config import *

class AccountAnalyzer:
    def __init__(self, x_client):
        self.x_client = x_client
        self.trusted_manager = TrustedAccountsManager()
        self.logger = logging.getLogger(__name__)
        self.db_path = DATABASE_PATH
    
    def analyze_account(self, username):
        """Perform comprehensive account analysis"""
        try:
            # Get user information
            user_info = self.x_client.get_user_info(username)
            if not user_info:
                return None
            
            # Get recent tweets
            tweets = self.x_client.get_user_tweets(user_info['id'], max_results=20)
            
            # Get followers (limited sample)
            followers = self.x_client.get_user_followers(user_info['id'], max_results=100)
            
            # Perform analysis
            analysis = self._perform_analysis(user_info, tweets, followers)
            
            # Store results
            self._store_analysis(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing account {username}: {e}")
            return None
    
    def _perform_analysis(self, user_info, tweets, followers):
        """Perform detailed analysis of account data"""
        analysis = {
            'user_id': user_info['id'],
            'username': user_info['username'],
            'account_age_days': user_info['account_age_days'],
            'follower_count': user_info['followers_count'],
            'following_count': user_info['following_count'],
            'tweet_count': user_info['tweet_count'],
            'verified': user_info['verified']
        }
        
        # Calculate follower ratio
        if user_info['following_count'] > 0:
            analysis['follower_ratio'] = user_info['followers_count'] / user_info['following_count']
        else:
            analysis['follower_ratio'] = float('inf')
        
        # Analyze bio
        bio = user_info['description']
        analysis['bio_length'] = len(bio)
        analysis['bio_keywords'] = self._extract_bio_keywords(bio)
        
        # Analyze engagement
        analysis['avg_engagement'] = self._calculate_engagement(tweets)
        
        # Check trusted followers
        trusted_count, trusted_list = self.trusted_manager.check_trusted_followers(followers)
        analysis['trusted_followers_count'] = trusted_count
        analysis['trusted_followers'] = trusted_list
        
        # Calculate trustworthiness score
        analysis['trustworthiness_score'] = self._calculate_trustworthiness_score(analysis)
        
        # Generate risk factors
        analysis['risk_factors'] = self._identify_risk_factors(analysis, tweets)
        
        # Generate positive indicators
        analysis['positive_indicators'] = self._identify_positive_indicators(analysis, tweets)
        
        return analysis
    
    def _extract_bio_keywords(self, bio):
        """Extract relevant keywords from bio"""
        if not bio:
            return []
        
        # Common crypto/solana related keywords
        crypto_keywords = [
            'crypto', 'blockchain', 'solana', 'defi', 'nft', 'web3',
            'bitcoin', 'ethereum', 'trading', 'investor', 'developer',
            'founder', 'ceo', 'project', 'token', 'dapp'
        ]
        
        bio_lower = bio.lower()
        found_keywords = [kw for kw in crypto_keywords if kw in bio_lower]
        
        return found_keywords
    
    def _calculate_engagement(self, tweets):
        """Calculate average engagement rate"""
        if not tweets:
            return 0
        
        total_engagement = 0
        for tweet in tweets:
            engagement = (
                tweet['like_count'] + 
                tweet['retweet_count'] + 
                tweet['reply_count'] + 
                tweet['quote_count']
            )
            total_engagement += engagement
        
        return total_engagement / len(tweets)
    
    def _calculate_trustworthiness_score(self, analysis):
        """Calculate overall trustworthiness score (0-100)"""
        score = 50  # Base score
        
        # Account age factor
        if analysis['account_age_days'] > 365:
            score += 15
        elif analysis['account_age_days'] > 180:
            score += 10
        elif analysis['account_age_days'] > 90:
            score += 5
        elif analysis['account_age_days'] < 30:
            score -= 20
        
        # Follower ratio factor
        if 0.1 <= analysis['follower_ratio'] <= 10:
            score += 10
        elif analysis['follower_ratio'] > 100:
            score -= 15
        
        # Trusted followers factor
        if analysis['trusted_followers_count'] >= 3:
            score += 25
        elif analysis['trusted_followers_count'] >= 2:
            score += 15
        elif analysis['trusted_followers_count'] >= 1:
            score += 5
        
        # Verification factor
        if analysis['verified']:
            score += 10
        
        # Bio factor
        if analysis['bio_length'] > 50 and analysis['bio_keywords']:
            score += 5
        
        # Engagement factor
        if analysis['avg_engagement'] > 10:
            score += 5
        elif analysis['avg_engagement'] > 50:
            score += 10
        
        return max(0, min(100, score))
    
    def _identify_risk_factors(self, analysis, tweets):
        """Identify potential risk factors"""
        risks = []
        
        if analysis['account_age_days'] < 30:
            risks.append("Very new account (less than 30 days)")
        
        if analysis['follower_ratio'] > 50:
            risks.append("Suspicious follower/following ratio")
        
        if analysis['trusted_followers_count'] == 0:
            risks.append("No trusted followers detected")
        
        if analysis['bio_length'] < 20:
            risks.append("Minimal bio information")
        
        if analysis['avg_engagement'] < 1:
            risks.append("Very low engagement rates")
        
        # Analyze tweet content for spam patterns
        spam_indicators = self._check_spam_patterns(tweets)
        if spam_indicators:
            risks.extend(spam_indicators)
        
        return risks
    
    def _identify_positive_indicators(self, analysis, tweets):
        """Identify positive trust indicators"""
        positives = []
        
        if analysis['account_age_days'] > 365:
            positives.append("Established account (1+ years)")
        
        if analysis['trusted_followers_count'] >= 2:
            positives.append(f"Followed by {analysis['trusted_followers_count']} trusted accounts")
        
        if analysis['verified']:
            positives.append("Verified account")
        
        if 0.1 <= analysis['follower_ratio'] <= 10:
            positives.append("Healthy follower/following ratio")
        
        if analysis['bio_keywords']:
            positives.append("Relevant bio keywords present")
        
        if analysis['avg_engagement'] > 10:
            positives.append("Good engagement rates")
        
        return positives
    
    def _check_spam_patterns(self, tweets):
        """Check for spam patterns in tweets"""
        if not tweets:
            return []
        
        spam_indicators = []
        
        # Check for excessive repetition
        texts = [tweet['text'] for tweet in tweets]
        if len(set(texts)) < len(texts) * 0.5:
            spam_indicators.append("High content repetition detected")
        
        # Check for excessive promotional content
        promo_count = 0
        for tweet in tweets:
            text = tweet['text'].lower()
            if any(word in text for word in ['buy', 'sell', 'pump', 'moon', 'gem', 'x100']):
                promo_count += 1
        
        if promo_count > len(tweets) * 0.7:
            spam_indicators.append("Excessive promotional content")
        
        return spam_indicators
    
    def _store_analysis(self, analysis):
        """Store analysis results in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO analysis_results 
                (user_id, username, account_age_days, follower_count, following_count,
                 follower_ratio, bio_length, bio_keywords, avg_engagement, 
                 trusted_followers_count, trustworthiness_score)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis['user_id'],
                analysis['username'],
                analysis['account_age_days'],
                analysis['follower_count'],
                analysis['following_count'],
                analysis['follower_ratio'],
                analysis['bio_length'],
                ','.join(analysis['bio_keywords']),
                analysis['avg_engagement'],
                analysis['trusted_followers_count'],
                analysis['trustworthiness_score']
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing analysis: {e}")
    
    def format_analysis_report(self, analysis):
        """Format analysis into a readable report"""
        if not analysis:
            return "❌ Unable to analyze account - account may be private or not found."
        
        score = analysis['trustworthiness_score']
        username = analysis['username']
        
        # Determine trust level
        if score >= 80:
            trust_emoji = "🟢"
            trust_level = "HIGH TRUST"
        elif score >= 60:
            trust_emoji = "🟡"
            trust_level = "MODERATE TRUST"
        elif score >= 40:
            trust_emoji = "🟠"
            trust_level = "LOW TRUST"
        else:
            trust_emoji = "🔴"
            trust_level = "HIGH RISK"
        
        report = f"{trust_emoji} RUGGUARD ANALYSIS: @{username}\n"
        report += f"Trust Level: {trust_level} ({score}/100)\n\n"
        
        # Key metrics
        report += f"📊 Account Age: {analysis['account_age_days']} days\n"
        report += f"👥 Followers: {analysis['follower_count']:,}\n"
        report += f"🤝 Trusted Connections: {analysis['trusted_followers_count']}\n"
        
        # Risk factors
        if analysis.get('risk_factors'):
            report += f"\n⚠️ Risk Factors:\n"
            for risk in analysis['risk_factors'][:3]:  # Limit to 3 for space
                report += f"• {risk}\n"
        
        # Positive indicators
        if analysis.get('positive_indicators'):
            report += f"\n✅ Positive Signs:\n"
            for positive in analysis['positive_indicators'][:2]:  # Limit to 2 for space
                report += f"• {positive}\n"
        
        report += f"\n🛡️ Analysis by @projectrugguard"
        
        return report

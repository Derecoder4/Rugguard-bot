import sqlite3
import os

def setup_database():
    """Initialize the SQLite database for storing analysis data"""
    db_path = 'rugguard_bot.db'
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table for storing analysis results
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE,
            username TEXT,
            account_age_days INTEGER,
            follower_count INTEGER,
            following_count INTEGER,
            follower_ratio REAL,
            bio_length INTEGER,
            bio_keywords TEXT,
            avg_engagement REAL,
            trusted_followers_count INTEGER,
            trustworthiness_score REAL,
            analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create table for trusted accounts cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trusted_accounts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            user_id TEXT,
            last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create table for processed tweets to avoid duplicates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_tweets (
            tweet_id TEXT PRIMARY KEY,
            processed_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup completed successfully!")

if __name__ == "__main__":
    setup_database()

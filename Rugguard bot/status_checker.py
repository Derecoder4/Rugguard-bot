#!/usr/bin/env python3
"""
Status checker for RUGGUARD Bot
Run this script to check if the bot is running and get statistics
"""

import sqlite3
import os
import sys
from datetime import datetime, timedelta
from config import DATABASE_PATH

def check_bot_status():
    """Check bot status and display statistics"""
    
    # Check if database exists
    if not os.path.exists(DATABASE_PATH):
        print("❌ Database not found. Bot may not be initialized.")
        print("Run: python scripts/setup_database.py")
        return False
    
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['processed_tweets', 'analysis_results', 'trusted_accounts']
        missing_tables = [t for t in required_tables if t not in tables]
        
        if missing_tables:
            print(f"❌ Missing database tables: {missing_tables}")
            print("Run: python scripts/setup_database.py")
            return False
        
        print("🛡️ RUGGUARD BOT STATUS CHECK")
        print("=" * 50)
        
        # Get processing statistics
        cursor.execute("SELECT COUNT(*) FROM processed_tweets")
        total_processed = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        total_analysis = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM trusted_accounts")
        trusted_count = cursor.fetchone()[0]
        
        # Get recent activity
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
        
        # Get last activity
        cursor.execute("""
            SELECT processed_date FROM processed_tweets 
            ORDER BY processed_date DESC LIMIT 1
        """)
        last_activity = cursor.fetchone()
        last_activity_str = last_activity[0] if last_activity else "Never"
        
        # Display status
        print(f" Total Tweets Processed: {total_processed}")
        print(f" Total Analyses Completed: {total_analysis}")
        print(f" Trusted Accounts Loaded: {trusted_count}")
        print(f" Activity (Last 24h): {recent_processed} processed, {recent_analysis} analyzed")
        print(f" Last Activity: {last_activity_str}")
        
        # Check if bot seems active
        if last_activity:
            last_time = datetime.fromisoformat(last_activity[0])
            time_diff = datetime.now() - last_time
            
            if time_diff < timedelta(hours=1):
                print("✅ Bot appears to be ACTIVE (recent activity detected)")
            elif time_diff < timedelta(hours=6):
                print("🟡 Bot may be IDLE (no recent activity)")
            else:
                print("🔴 Bot appears to be INACTIVE (no activity for 6+ hours)")
        else:
            print("🔴 Bot appears to be INACTIVE (no activity recorded)")
        
        # Recent analyses
        if recent_analysis > 0:
            print(f"\n📈 Recent Analyses:")
            cursor.execute("""
                SELECT username, trustworthiness_score, analysis_date 
                FROM analysis_results 
                WHERE analysis_date > datetime('now', '-24 hours')
                ORDER BY analysis_date DESC LIMIT 5
            """)
            
            for row in cursor.fetchall():
                username, score, date = row
                print(f"  • @{username}: {score}/100 ({date})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f" Error checking status: {e}")
        return False

def check_log_file():
    """Check if log file exists and show recent entries"""
    log_file = "rugguard_bot.log"
    
    if not os.path.exists(log_file):
        print(f"\n📝 Log file not found: {log_file}")
        return
    
    try:
        print(f"\n📝 Recent Log Entries (last 10 lines):")
        print("-" * 50)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            recent_lines = lines[-10:] if len(lines) >= 10 else lines
            
            for line in recent_lines:
                print(line.strip())
                
    except Exception as e:
        print(f" Error reading log file: {e}")

def main():
    """Main status check function"""
    print("🔍 Checking RUGGUARD Bot Status...\n")
    
    # Check database status
    db_ok = check_bot_status()
    
    # Check log file
    check_log_file()
    
    print("\n" + "=" * 50)
    
    if db_ok:
        print(" To monitor real-time activity, check: rugguard_bot.log")
        print(" To see if bot is running: ps aux | grep python")
    else:
        print(" Initialize the bot with: python scripts/setup_database.py")
        print(" Start the bot with: python main.py")

if __name__ == "__main__":
    main()

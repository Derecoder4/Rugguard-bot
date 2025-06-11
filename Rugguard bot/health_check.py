#!/usr/bin/env python3
"""
Simple health check server for RUGGUARD Bot
Provides a web endpoint to check bot status
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sqlite3
from datetime import datetime, timedelta
from config import DATABASE_PATH

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Handle GET requests"""
        if self.path == '/health':
            self.send_health_response()
        elif self.path == '/status':
            self.send_status_response()
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
    
    def send_health_response(self):
        """Send simple health check response"""
        try:
            # Check if database exists and is accessible
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM processed_tweets")
            conn.close()
            
            response = {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'message': 'RUGGUARD Bot is operational'
            }
            status_code = 200
            
        except Exception as e:
            response = {
                'status': 'unhealthy',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            status_code = 500
        
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode())
    
    def send_status_response(self):
        """Send detailed status response"""
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Get statistics
            cursor.execute("SELECT COUNT(*) FROM processed_tweets")
            total_processed = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM analysis_results")
            total_analysis = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT COUNT(*) FROM processed_tweets 
                WHERE processed_date > datetime('now', '-24 hours')
            """)
            recent_processed = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT processed_date FROM processed_tweets 
                ORDER BY processed_date DESC LIMIT 1
            """)
            last_activity = cursor.fetchone()
            
            # Determine if bot is active
            is_active = False
            if last_activity:
                last_time = datetime.fromisoformat(last_activity[0])
                time_diff = datetime.now() - last_time
                is_active = time_diff < timedelta(hours=1)
            
            response = {
                'status': 'active' if is_active else 'idle',
                'timestamp': datetime.now().isoformat(),
                'statistics': {
                    'total_processed': total_processed,
                    'total_analysis': total_analysis,
                    'recent_processed_24h': recent_processed,
                    'last_activity': last_activity[0] if last_activity else None
                },
                'is_active': is_active
            }
            
            conn.close()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response, indent=2).encode())
            
        except Exception as e:
            response = {
                'status': 'error',
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())

def run_health_server(port=8080):
    """Run the health check server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, HealthCheckHandler)
    print(f"🏥 Health check server running on port {port}")
    print(f"📊 Status endpoint: http://localhost:{port}/status")
    print(f"💚 Health endpoint: http://localhost:{port}/health")
    httpd.serve_forever()

if __name__ == "__main__":
    run_health_server()

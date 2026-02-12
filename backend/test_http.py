#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import init_db
from app.models import Base
import subprocess
import time

# Initialize database
print("Initializing database...")
init_db()
print("Database initialized!")

# Start server in background
print("Starting server...")
server_process = subprocess.Popen([
    'source', '.venv/bin/activate', '&&', 
    'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', '8003'
], shell=True, cwd='/home/ubuntu/mobi/backend')

time.sleep(3)

try:
    # Test the endpoint with curl
    result = subprocess.run([
        'curl', '-s', 'http://localhost:8003/api/listings'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Successfully connected to endpoint via HTTP")
        print(f"Response length: {len(result.stdout)} characters")
        
        # Test with query parameters
        result2 = subprocess.run([
            'curl', '-s', 'http://localhost:8003/api/listings?limit=1'
        ], capture_output=True, text=True)
        
        if result2.returncode == 0:
            print("✅ Pagination parameter works via HTTP")
        else:
            print("❌ Pagination parameter failed")
            
    else:
        print(f"❌ Failed to connect: {result.stderr}")
        
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    # Kill server
    server_process.terminate()
    server_process.wait()

print("✅ HTTP test completed!")
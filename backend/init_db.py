#!/usr/bin/env python3

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import init_db

print("Initializing database...")
init_db()
print("Database initialized successfully!")
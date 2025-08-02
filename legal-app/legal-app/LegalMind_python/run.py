#!/usr/bin/env python3
"""
Startup script for Legal Document Analyzer with Grantie
Runs both backend and frontend servers
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_requirements():
    """Check if required packages are installed."""
    try:
        import fastapi, uvicorn, streamlit, openai, docx, requests
        print("✅ All required packages found")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("Please install requirements:")
        print("pip install -r backend/requirements.txt")
        print("pip install -r frontend/requirements.txt")
        return False

def check_env_file():
    """Check if .env file exists with required keys."""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("Please create a .env file with the following keys:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
        print("ELEVENLABS_API_KEY=your_elevenlabs_api_key_here")
        return False
    
    # Read and check for required keys
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    required_keys = ['OPENAI_API_KEY']
    missing_keys = []
    
    for key in required_keys:
        if key not in env_content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"❌ Missing required environment variables: {', '.join(missing_keys)}")
        return False
    
    print("✅ Environment file configured")
    return True

def start_backend():
    """Start the FastAPI backend server."""
    print("🚀 Starting Backend Server...")
    try:
        backend_process = subprocess.Popen([
            sys.executable, "-m", "uvicorn", "main:app",
            "--host", "127.0.0.1",
            "--port", "8000",
            "--reload"
        ], cwd=".")
        
        # Give backend time to start
        time.sleep(3)
        return backend_process
    except Exception as e:
        print(f"❌ Failed to start backend: {e}")
        return None

def start_frontend():
    """Start the Streamlit frontend server."""
    print("🖥️ Starting Frontend Server...")
    try:
        frontend_process = subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", "frontend/app.py",
            "--server.port", "8501",
            "--server.address", "127.0.0.1"
        ])
        return frontend_process
    except Exception as e:
        print(f"❌ Failed to start frontend: {e}")
        return None

def main():
    """Main startup function."""
    print("🏛️ Legal Document Analyzer with Grantie")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        return
    
    # Check environment file
    if not check_env_file():
        return
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        return
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        backend_process.terminate()
        return
    
    print("\n" + "=" * 50)
    print("🎉 Both servers started successfully!")
    print("📊 Backend API: http://127.0.0.1:8000")
    print("🖥️ Frontend UI: http://127.0.0.1:8501")
    print("📚 API Docs: http://127.0.0.1:8000/docs")
    print("\nPress Ctrl+C to stop both servers")
    print("=" * 50)
    
    try:
        # Wait for processes
        while True:
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("❌ Backend server stopped unexpectedly")
                break
            if frontend_process.poll() is not None:
                print("❌ Frontend server stopped unexpectedly")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        
        # Wait for graceful shutdown
        backend_process.wait(timeout=5)
        frontend_process.wait(timeout=5)
        
        print("✅ Servers stopped successfully")

if __name__ == "__main__":
    main()
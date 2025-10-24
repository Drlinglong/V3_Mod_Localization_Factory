#!/usr/bin/env python3
"""
Development server launcher that runs both FastAPI backend and Vite frontend concurrently.
"""

import subprocess
import sys
import os
import signal
import time

def run_servers():
    """Run both backend and frontend servers concurrently."""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Prepare processes list
    processes = []
    
    # Backend process (FastAPI)
    backend_cwd = project_root
    backend_cmd = [sys.executable, '-m', 'uvicorn', 'scripts.web_server:app', '--host', '0.0.0.0', '--port', '8000']
    
    # Frontend process (Vite)
    frontend_cwd = os.path.join(project_root, 'scripts', 'react-ui')
    if sys.platform == 'win32':
        frontend_cmd = ['cmd', '/c', 'npm run dev']
    else:
        frontend_cmd = ['npm', 'run', 'dev']
    
    print("=" * 60)
    print("Remis Development Server Launcher")
    print("=" * 60)
    print()
    
    try:
        # Start backend server
        print("[INFO] Starting FastAPI backend server on port 8000...")
        print(f"[INFO] Working directory: {backend_cwd}")
        print(f"[INFO] Command: {' '.join(backend_cmd)}")
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=backend_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(('Backend', backend_process, backend_cmd))
        time.sleep(3)  # Give backend time to start

        # Check if backend started successfully
        if backend_process.poll() is not None:
            stdout, stderr = backend_process.communicate()
            print(f"[ERROR] Backend server failed to start!")
            if stdout:
                print(f"[STDOUT] {stdout}")
            if stderr:
                print(f"[STDERR] {stderr}")
            sys.exit(1)
        
        # Start frontend server
        print("[INFO] Starting Vite frontend server on port 5173...")
        print(f"[INFO] Working directory: {frontend_cwd}")
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=frontend_cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
        processes.append(('Frontend', frontend_process, frontend_cmd))
        
        print()
        print("[SUCCESS] Both servers are running!")
        print("[INFO] Backend: http://localhost:8000/")
        print("[INFO] Frontend: http://localhost:5173/")
        print()
        print("Press Ctrl+C to stop all servers...")
        print("=" * 60)
        print()
        
        # Monitor processes and stream output
        while True:
            time.sleep(0.1)

            # Check if any process has terminated
            for name, process, cmd in processes:
                if process.poll() is not None:
                    # Process has terminated
                    print(f"\n[ERROR] {name} server has stopped unexpectedly!")
                    stdout, stderr = process.communicate()
                    if stderr:
                        print(f"[{name} STDERR] {stderr}")
                    if stdout:
                        print(f"[{name} STDOUT] {stdout}")
                    # Kill all remaining processes
                    for _, p, _ in processes:
                        if p.poll() is None:
                            p.terminate()
                    sys.exit(1)

            # Try to read output from processes without blocking
            for name, process, cmd in processes:
                try:
                    line = process.stdout.readline()
                    if line:
                        print(f"[{name}] {line.rstrip()}")
                except:
                    pass
    
    except KeyboardInterrupt:
        print("\n[INFO] Shutting down servers...")
        for name, process, cmd in processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                print(f"[INFO] {name} server stopped.")
        print("[SUCCESS] All servers stopped.")
        sys.exit(0)

    except Exception as e:
        print(f"\n[ERROR] {e}")
        for _, process, cmd in processes:
            if process.poll() is None:
                process.terminate()
        sys.exit(1)

if __name__ == '__main__':
    run_servers()

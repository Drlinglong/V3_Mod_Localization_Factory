#!/usr/bin/env python3
"""
Development server launcher that runs both FastAPI backend and Vite frontend concurrently.
"""

import subprocess
import sys
import os
import signal
import time
import urllib.request
import urllib.error
import socket
import json

def kill_process_on_port(port):
    """Forcefully kill any process listening on the specified port."""
    try:
        if sys.platform == 'win32':
            # Find PID
            cmd = f'netstat -ano | findstr :{port}'
            output = subprocess.check_output(cmd, shell=True).decode()
            lines = output.strip().split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) > 4 and f':{port}' in parts[1]:
                    pid = parts[-1]
                    print(f"[INFO] Killing zombie process on port {port} (PID: {pid})...")
                    subprocess.run(f'taskkill /F /PID {pid}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
             # Linux/Mac implementation (skipped for now as user is on Windows)
             pass
    except (subprocess.CalledProcessError, IndexError, ValueError):
        pass

def find_free_port(start_port=8081, max_attempts=200):
    """Find a free port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No free ports found between {start_port} and {start_port + max_attempts}")

def wait_for_backend(port, timeout=30):
    """Wait until the backend API returns HTTP 200."""
    start_time = time.time()
    urls_to_check = [f"http://127.0.0.1:{port}/", f"http://localhost:{port}/"]
    
    while time.time() - start_time < timeout:
        for url in urls_to_check:
            try:
                with urllib.request.urlopen(url, timeout=1) as response:
                    if response.status == 200:
                        return True
            except (ConnectionRefusedError, urllib.error.URLError, socket.timeout):
                pass
            except Exception:
                # Other errors (e.g. 500) mean it's running but broken, but at least listening.
                # Ideally we wait for 200.
                pass
        time.sleep(0.5)
    return False

def run_servers():
    """Run both backend and frontend servers concurrently."""
    
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Prepare processes list
    processes = []
    
    # Backend process (FastAPI)
    backend_cwd = project_root
    
    # Force cleanup of port 8081 to avoid zombie processes causing port shifts
    kill_process_on_port(8081)
    
    # We prefer 8081 because Vite default proxy aligns with it
    backend_port = find_free_port(8081)
    backend_cmd = [sys.executable, '-m', 'uvicorn', 'scripts.web_server:app', '--host', '0.0.0.0', '--port', str(backend_port)]
    
    # Frontend process (Vite)
    frontend_cwd = os.path.join(project_root, 'scripts', 'react-ui')
    if sys.platform == 'win32':
        frontend_cmd = ['cmd', '/c', 'npm run dev']
    else:
        frontend_cmd = ['npm', 'run', 'dev']
    
    # Generate frontend config
    config_dir = os.path.join(frontend_cwd, 'public')
    os.makedirs(config_dir, exist_ok=True)
    config_path = os.path.join(config_dir, 'server_config.json')
    try:
        with open(config_path, 'w') as f:
            json.dump({
                'apiBaseUrl': f'http://127.0.0.1:{backend_port}',
                'port': backend_port
            }, f, indent=2)
        print(f"[INFO] Generated frontend config at {config_path}")
    except Exception as e:
        print(f"[WARN] Failed to generate frontend config: {e}")

    # Prepare environment for frontend
    frontend_env = os.environ.copy()
    frontend_env['BACKEND_PORT'] = str(backend_port)
    
    print("=" * 60)
    print("Remis Development Server Launcher")
    print("=" * 60)
    print()
    
    try:
        # Start backend server
        print(f"[INFO] Starting FastAPI backend server on port {backend_port}...")
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
        
        # Wait for backend to be ready
        print(f"[INFO] Waiting for backend to start listening on port {backend_port}...")
        if not wait_for_backend(backend_port):
            print(f"[ERROR] Backend failed to start listening on port {backend_port} within 30 seconds.")
            # Let the subsequent poll logic handle the process cleanup/log dumping
        else:
            print(f"[INFO] Backend is ready!")

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
            bufsize=1,
            env=frontend_env
        )
        processes.append(('Frontend', frontend_process, frontend_cmd))
        
        print()
        print("[SUCCESS] Both servers are running!")
        print(f"[INFO] Backend: http://localhost:{backend_port}/")
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

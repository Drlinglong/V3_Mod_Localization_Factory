import os
import shutil
import subprocess
import platform
import sys

def print_step(step_name):
    print(f"\n{'='*60}")
    print(f"[INFO] {step_name}")
    print(f"{'='*60}")

def run_command(command, cwd=None, shell=True):
    try:
        print(f"[EXEC] {command}")
        subprocess.check_call(command, cwd=cwd, shell=shell)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {command}")
        sys.exit(1)

def main():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scripts_dir = os.path.join(project_root, "scripts")
    react_ui_dir = os.path.join(scripts_dir, "react-ui")
    src_tauri_dir = os.path.join(react_ui_dir, "src-tauri")
    binaries_dir = os.path.join(src_tauri_dir, "binaries")
    
    # Step 1: Clean & Init
    print_step("Step 1: Clean & Init")
    
    dirs_to_clean = [
        os.path.join(project_root, "dist"),
        os.path.join(project_root, "build"),
        binaries_dir
    ]
    
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"[CLEAN] Removing {d}")
            shutil.rmtree(d)
            
    if not os.path.exists(binaries_dir):
        print(f"[INIT] Creating {binaries_dir}")
        os.makedirs(binaries_dir)

    # Step 2: Freeze the Backend (PyInstaller)
    print_step("Step 2: Freeze the Backend (PyInstaller)")
    
    web_server_script = os.path.join(scripts_dir, "web_server.py")
    
    # Construct PyInstaller command
    # --onefile: Create a single executable
    # --noconsole: No terminal window
    # --name web_server: Name of the executable
    # --hidden-import: Ensure dependencies are included
    pyinstaller_cmd = (
        f'pyinstaller --clean --onefile --noconsole --name web_server '
        f'--hidden-import uvicorn --hidden-import fastapi --hidden-import pydantic '
        f'"{web_server_script}"'
    )
    
    run_command(pyinstaller_cmd, cwd=project_root)

    # Step 3: Tauri Sidecar Naming Compliance
    print_step("Step 3: Tauri Sidecar Naming Compliance")
    
    # Detect target triple
    # Common triples:
    # Windows x64: x86_64-pc-windows-msvc
    machine = platform.machine().lower()
    system = platform.system().lower()
    
    target_triple = ""
    if system == "windows":
        if machine in ["amd64", "x86_64"]:
            target_triple = "x86_64-pc-windows-msvc"
        elif machine == "arm64":
            target_triple = "aarch64-pc-windows-msvc"
        else:
             target_triple = "i686-pc-windows-msvc" # Fallback for 32-bit
    else:
        print(f"[WARNING] Auto-detection for {system} not fully implemented. Defaulting to x86_64-pc-windows-msvc for this task.")
        target_triple = "x86_64-pc-windows-msvc"

    print(f"[INFO] Detected Target Triple: {target_triple}")
    
    dist_dir = os.path.join(project_root, "dist")
    original_exe = os.path.join(dist_dir, "web_server.exe")
    
    if not os.path.exists(original_exe):
        print(f"[ERROR] Could not find generated executable at {original_exe}")
        sys.exit(1)
        
    new_exe_name = f"web_server-{target_triple}.exe"
    target_path = os.path.join(binaries_dir, new_exe_name)
    
    print(f"[MOVE] Moving {original_exe} -> {target_path}")
    shutil.move(original_exe, target_path)

    # Step 4: Frontend Build & Tauri Build
    print_step("Step 4: Frontend Build & Tauri Build")
    
    # Install dependencies
    run_command("npm install", cwd=react_ui_dir)
    
    # Build React App
    run_command("npm run build", cwd=react_ui_dir)
    
    # Build Tauri App
    run_command("npm run tauri build", cwd=react_ui_dir)
    
    print_step("Build Pipeline Completed Successfully!")

if __name__ == "__main__":
    main()

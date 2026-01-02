import os
import sys

# PATCH: Fix for PyInstaller where sys.stdout/stderr can be None
# This MUST come before any other imports that might check isatty

class MockStream:
    def write(self, msg): pass
    def flush(self): pass
    def isatty(self): return False
    def fileno(self): return -1

if sys.stdout is None:
    sys.stdout = MockStream()
if sys.stderr is None:
    sys.stderr = MockStream()

# PANIC LOGGER START
import datetime
import multiprocessing
import os

# Add project root to Python path IMMEDIATELY
# This allows us to import system_utils right away
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def panic_log(msg):
    try:
        appdata = os.getenv('APPDATA')
        if appdata:
             path = os.path.join(appdata, "RemisModFactory", "startup_panic.log")
             os.makedirs(os.path.dirname(path), exist_ok=True)
             with open(path, "a", encoding="utf-8") as f:
                 f.write(f"[{datetime.datetime.now()}] {msg}\n")
    except:
        pass

# 0. Robust Port Check (Call ASAP)
# This prevents [WinError 10013] in dev mode (--reload) and frozen mode.
# Note: In dev mode, this is also called by run-backend.bat as a pre-flight check.

panic_log("=== WEB SERVER STARTUP (LOG_CONFIG=NONE) ===")

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import using absolute imports from project root
try:
    panic_log("Importing app_settings...")
    from scripts.app_settings import load_api_keys_to_env
    from scripts.utils import logger, i18n
except Exception as e:
    panic_log(f"Import Failed: {e}")
    raise e


# Load API keys from keyring into environment variables
load_api_keys_to_env()

# Setup logger and i18n BEFORE importing managers that use them
logger.setup_logger()
i18n.load_language() # Load default language

# Initialize Database (Cold Start / Seed Data)
# CRITICAL: This must be called BEFORE importing routers/services which instantiate managers
# that open persistent DB connections, otherwise we get "database is locked" during copy/init.
try:
    from scripts.core.db_initializer import initialize_database
    initialize_database()
except Exception as e:
    panic_log(f"INIT CRASH: {e}")


# Import Routers
from scripts.routers import (
    projects,
    translation,
    glossary,
    proofreading,
    docs,
    tools,
    neologism,
    validation,
    config,
    system,
    prompts
)



import time
import logging
from fastapi import Request

# Get logger for this module
logger_web = logging.getLogger(__name__)

app = FastAPI(
    title="P社Mod本地化工厂 API",
    description="为P社Mod本地化工厂提供Web UI的后端API。",
    version="1.0.0",
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # 记录请求进入 (Optional)
    # logger_web.info(f"➡️ [REQ] {request.method} {request.url.path}") 

    try:
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        
        # 记录请求完成 (包含状态码和耗时)
        logger_web.info(
            f"✅ [API] {request.method} {request.url.path} "
            f"- Status: {response.status_code} - Time: {process_time:.2f}ms"
        )
        return response
    except Exception as e:
        process_time = (time.time() - start_time) * 1000
        # 记录未捕获的异常 (炸厕所现场)
        logger_web.error(
            f"❌ [ERR] {request.method} {request.url.path} "
            f"- Time: {process_time:.2f}ms - Error: {str(e)}",
            exc_info=True # 打印堆栈信息
        )
        raise e

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_frozen_log_config():
    """
    Returns a logging configuration that writes ONLY to a file.
    This bypasses any StreamHandler that might check isatty() on sys.stderr.
    """
    appdata = os.getenv('APPDATA')
    if appdata:
         log_file = os.path.join(appdata, "RemisModFactory", "logs", "uvicorn_frozen.log")
         os.makedirs(os.path.dirname(log_file), exist_ok=True)
    else:
         log_file = "uvicorn_frozen.log"

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": "%(asctime)s - %(levelname)s - %(message)s",
                "class": "logging.Formatter", 
            },
            "access": {
                "format": "%(asctime)s - %(levelname)s - %(client_addr)s - \"%(request_line)s\" %(status_code)s",
                "class": "logging.Formatter",
            },
        },
        "handlers": {
            "file": {
                "class": "logging.FileHandler",
                "formatter": "default",
                "filename": log_file,
                "encoding": "utf-8",
                "mode": "a",
            },
            "access_file": {
                "class": "logging.FileHandler",
                "formatter": "access",
                "filename": log_file,
                "encoding": "utf-8",
                "mode": "a",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["file"], "level": "INFO", "propagate": False},
            "uvicorn.error": {"handlers": ["file"], "level": "INFO", "propagate": False},
            "uvicorn.access": {"handlers": ["access_file"], "level": "INFO", "propagate": False},
        },
    }

# Include Routers
app.include_router(projects.router)
app.include_router(translation.router)
app.include_router(glossary.router)
app.include_router(proofreading.router)
app.include_router(docs.router)
app.include_router(tools.router)
app.include_router(neologism.router)
app.include_router(validation.router)
app.include_router(config.router)
app.include_router(system.router)
app.include_router(prompts.router)

@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

@app.get("/api/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

if __name__ == "__main__":
    multiprocessing.freeze_support()
    
    # Free port 8081 if occupied (frozen sidecar mode)
    try:
        from scripts.utils.force_free_port import force_free_port
        force_free_port(8081)
    except ImportError:
        # psutil might still be missing if hidden-import failed
        print("[PORT] psutil not found, skipping port cleanup.")
    except Exception as e:
        print(f"[PORT] Error during port cleanup: {e}")
    
    # Specific entry point for the frozen application (PyInstaller)
    import uvicorn
    import uvicorn.logging

    # --- CRITICAL STARTUP FIX FOR FROZEN APP ---
    if getattr(sys, 'frozen', False):
        try:
            # 1. Redirect stdout/stderr to files to prevent 'isatty' crashes
            app_data = os.getenv('APPDATA')
            if app_data:
                log_dir = os.path.join(app_data, "RemisModFactory", "logs")
                os.makedirs(log_dir, exist_ok=True)
                # buffering=1 means line buffered
                sys.stdout = open(os.path.join(log_dir, "startup_stdout.log"), "a", encoding="utf-8", buffering=1)
                sys.stderr = open(os.path.join(log_dir, "startup_stderr.log"), "a", encoding="utf-8", buffering=1)
            
        except Exception as e:
            panic_log(f"Startup Redirection Error: {e}")

    # 3. Simplified Run with Redirection
    # We have already redirected sys.stdout/stderr to files above.
    # These file objects return False for isatty(), so Uvicorn's default
    # ColourizedFormatter will happily run without colors (no crash).
    # We pass log_config=None to use Uvicorn's defaults, which will write 
    # to our redirected sys.stdout/stderr.
    
    try:
        panic_log("Starting Uvicorn (log_config=None)...")
        # Initialize default logging config to ensure it binds to our redirected streams
        config = uvicorn.Config(app, host="127.0.0.1", port=8081, log_config=None)
        server = uvicorn.Server(config)
        server.run()
    except Exception as e:
        panic_log(f"Uvicorn Crashed: {e}")
        raise e
import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import using absolute imports from project root
from scripts.app_settings import load_api_keys_to_env
from scripts.utils import logger, i18n

# Load API keys from keyring into environment variables
load_api_keys_to_env()

# Setup logger and i18n BEFORE importing managers that use them
logger.setup_logger()
i18n.load_language() # Load default language

# Initialize Database (Cold Start / Seed Data)
# Must be called BEFORE importing routers/services which instantiate managers
from scripts.core.db_initializer import initialize_database
initialize_database()

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

if __name__ == "__main__":
    # Get configured port
    port = int(os.environ.get("BACKEND_PORT", 8081))
    
    # Pre-flight check: Warn user if specific port is blocked (mostly for manual runs)
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("0.0.0.0", port))
    except OSError as e: # Catch permission errors or address in use
        print(f"\n{'!'*60}")
        print(f"[CRITICAL ERROR] Cannot bind to port {port}.")
        print(f"Reason: {e}")
        print(f"If you are seeing '[WinError 10013] ... access permissions', it implies the port is reserved by Windows (Hyper-V/Docker).")
        print(f"\nSOLUTION: Please run 'start_dev_servers.bat' instead.")
        print(f"The launcher script will automatically find an available port for you.")
        print(f"{'!'*60}\n")
        # We don't exit here, we let uvicorn try and fail usually, or we can choose to exit. 
        # But uvicorn might have better error formatting. Let's just print the warning.
        # Actually, if we bound it successfully above, we released it when 'with' closed.
        # If we failed, we print the warning.
        
    print(f"[INFO] Backend attempting to start on port {port}...")
    uvicorn.run(app, host="0.0.0.0", port=port)
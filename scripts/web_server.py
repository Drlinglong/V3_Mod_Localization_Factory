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
    system
)

app = FastAPI(
    title="P社Mod本地化工厂 API",
    description="为P社Mod本地化工厂提供Web UI的后端API。",
    version="1.0.0",
)

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

@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
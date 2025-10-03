import os
import sys
import uvicorn
import uuid
import shutil
import zipfile
import logging
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form
from fastapi.responses import FileResponse
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.config import GAME_PROFILES, LANGUAGES, API_PROVIDERS, SOURCE_DIR, DEST_DIR
from scripts.workflows import initial_translate
from scripts.utils import logger, i18n

# Setup logger
logger.setup_logger()

# In-memory storage for task status.
# In a real production app, this should be replaced with a more robust solution like Redis.
tasks: Dict[str, Dict] = {}


def run_translation_workflow(task_id: str, mod_name: str, game_profile_id: str, source_lang_code: str, target_lang_codes: List[str], api_provider: str, mod_context: str):
    """
    A wrapper for the core translation logic to be run in the background.
    """
    # Initialize i18n for the background task
    i18n.load_language('en_US')

    tasks[task_id]["status"] = "processing"
    tasks[task_id]["log"].append("背景翻译任务开始...")

    try:
        # 1. Retrieve full config objects from IDs/codes
        game_profile = GAME_PROFILES.get(game_profile_id)
        source_lang = next((lang for lang in LANGUAGES.values() if lang["code"] == source_lang_code), None)
        target_languages = [lang for lang in LANGUAGES.values() if lang["code"] in target_lang_codes]

        if not all([game_profile, source_lang, target_languages]):
            raise ValueError("无效的游戏配置、源语言或目标语言。")

        # 2. Call the core translation function
        initial_translate.run(
            mod_name=mod_name,
            game_profile=game_profile,
            source_lang=source_lang,
            target_languages=target_languages,
            selected_provider=api_provider,
            mod_context=mod_context,
        )

        # 3. Once done, update status and prepare result
        tasks[task_id]["status"] = "completed"
        tasks[task_id]["log"].append("翻译流程成功完成！")

        # Prepare the result for download
        output_folder_name = f"{target_languages[0]['folder_prefix']}{mod_name}"
        if len(target_languages) > 1:
            output_folder_name = f"Multilanguage-{mod_name}"

        result_dir = os.path.join(DEST_DIR, output_folder_name)

        # Hyper-detailed logging for debugging
        logging.info(f"--- ZIPPING LOGS for Task {task_id} ---")
        logging.info(f"Final check before zipping. Target directory: {result_dir}")
        logging.info(f"Does it exist? {os.path.exists(result_dir)}")
        logging.info(f"Is it a directory? {os.path.isdir(result_dir)}")
        if os.path.exists(result_dir) and os.path.isdir(result_dir):
            logging.info(f"Contents: {os.listdir(result_dir)}")
        logging.info(f"------------------------------------")

        zip_path = shutil.make_archive(result_dir, 'zip', result_dir)
        tasks[task_id]["result_path"] = zip_path

    except Exception as e:
        logging.exception(f"任务 {task_id} 执行失败")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["log"].append(f"错误: {e}")


app = FastAPI(
    title="P社Mod本地化工厂 API",
    description="为P社Mod本地化工厂提供Web UI的后端API。",
    version="1.0.0",
)

@app.post("/api/translate")
async def start_translation(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    game_profile_id: str = Form(...),
    source_lang_code: str = Form(...),
    target_lang_codes: str = Form(...), # Received as a comma-separated string
    api_provider: str = Form(...),
    mod_context: str = Form("")
):
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "pending", "log": []}

    # Save and extract the uploaded file
    try:
        mod_name = file.filename.replace(".zip", "")

        # Clean up old source and dest dirs for this mod
        source_path = os.path.join(SOURCE_DIR, mod_name)
        if os.path.exists(source_path):
            shutil.rmtree(source_path)

        temp_zip_path = os.path.join(SOURCE_DIR, file.filename)
        with open(temp_zip_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
            zip_ref.extractall(source_path)

        os.remove(temp_zip_path) # Clean up the zip file

        tasks[task_id]["status"] = "starting"
        tasks[task_id]["log"].append(f"Mod '{mod_name}' 已上传并解压。")
    except Exception as e:
        logging.exception("File upload/unzip failed")
        raise HTTPException(status_code=500, detail=f"文件处理失败: {e}")

    # Add the long-running task to the background
    target_codes = target_lang_codes.split(',')
    background_tasks.add_task(
        run_translation_workflow,
        task_id,
        mod_name,
        game_profile_id,
        source_lang_code,
        target_codes,
        api_provider,
        mod_context
    )

    return {"task_id": task_id, "message": "翻译任务已开始"}

@app.get("/api/status/{task_id}")
def get_status(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    return task

@app.get("/api/result/{task_id}")
def get_result(task_id: str):
    task = tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务未找到")
    if task["status"] != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    result_path = task.get("result_path")
    if not result_path or not os.path.exists(result_path):
        raise HTTPException(status_code=404, detail="结果文件未找到")

    return FileResponse(result_path, media_type='application/zip', filename=os.path.basename(result_path))


@app.get("/api/config")
def get_config():
    """
    Provide frontend with necessary configuration data.
    """
    return {
        "game_profiles": GAME_PROFILES,
        "languages": LANGUAGES,
        "api_providers": list(API_PROVIDERS.keys())
    }

@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

if __name__ == "__main__":
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000)
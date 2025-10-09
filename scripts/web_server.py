import os
import sys
import uvicorn
import uuid
import shutil
import zipfile
import logging
from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException, Form, Query
from fastapi.responses import FileResponse, PlainTextResponse
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import using absolute imports from project root
from scripts.app_settings import GAME_PROFILES, LANGUAGES, API_PROVIDERS, SOURCE_DIR, DEST_DIR
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
        import traceback
        tb_str = traceback.format_exc()
        error_message = f"工作流执行失败 (Workflow execution failed): {e}\n{tb_str}"
        logging.error(f"任务 {task_id} 失败: {error_message}")
        tasks[task_id]["status"] = "failed"
        tasks[task_id]["log"].append(error_message)
        # 确保失败的任务没有可下载的结果路径
        if "result_path" in tasks[task_id]:
            del tasks[task_id]["result_path"]


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

        # Smartly handle "double folder" zip files where all content is inside a single sub-directory.
        extracted_items = os.listdir(source_path)
        if len(extracted_items) == 1:
            potential_inner_folder = os.path.join(source_path, extracted_items[0])
            if os.path.isdir(potential_inner_folder):
                logging.info(f"Detected single sub-directory '{extracted_items[0]}', promoting its contents.")
                # Move all contents from the sub-directory to the parent (source_path)
                for item_name in os.listdir(potential_inner_folder):
                    shutil.move(
                        os.path.join(potential_inner_folder, item_name),
                        os.path.join(source_path, item_name)
                    )
                # Remove the now-empty sub-directory
                os.rmdir(potential_inner_folder)

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

def build_docs_tree(directory: str, parent_key: str = ''):
    """
    Recursively builds a tree structure for Ant Design's Tree component.
    """
    tree = []
    if not os.path.isdir(directory):
        return []

    for item in sorted(os.listdir(directory)):
        path = os.path.join(directory, item)
        key = os.path.join(parent_key, item).replace('\\', '/')

        if os.path.isdir(path):
            children = build_docs_tree(path, key)
            # Only add directories that are not empty
            if children:
                tree.append({"title": item, "key": key, "children": children})
        else:
            if item.endswith(".md"):
                tree.append({"title": item, "key": key, "isLeaf": True})
    return tree

@app.get("/api/docs-tree")
def get_docs_tree():
    """
    Scans the project's root 'docs' directory and returns a file tree structure.
    """
    # Correctly point to the root 'docs' directory
    docs_path = os.path.join(project_root, 'docs')
    tree_data = build_docs_tree(docs_path)

    lang_tree = {}
    for lang_node in tree_data:
        # This post-processing step is designed to structure the output by language folders (e.g., 'en', 'zh').
        # We should only process nodes that are directories (i.e., have a 'children' key)
        # and ignore any standalone files at the root of the /docs directory.
        if 'children' in lang_node:
            lang_tree[lang_node['title']] = lang_node['children']

    return lang_tree

@app.get("/api/doc-content", response_class=PlainTextResponse)
def get_doc_content(path: str = Query(...)):
    """
    Safely reads and returns the content of a specific markdown file from the root 'docs' directory.
    Includes security checks to prevent directory traversal.
    """
    if ".." in path:
        raise HTTPException(status_code=400, detail="Invalid path.")

    # Create a secure, absolute path to the requested file
    docs_dir = os.path.abspath(os.path.join(project_root, 'docs'))
    requested_path = os.path.abspath(os.path.join(docs_dir, path))

    # Security check: Ensure the requested path is still within the 'docs' directory
    if not requested_path.startswith(docs_dir):
        raise HTTPException(status_code=403, detail="Access forbidden.")

    if not os.path.isfile(requested_path) or not requested_path.endswith(".md"):
        raise HTTPException(status_code=404, detail="File not found or not a markdown file.")

    try:
        with open(requested_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {e}")


@app.get("/")
def read_root():
    return {"message": "欢迎使用P社Mod本地化工厂API"}

if __name__ == "__main__":
    uvicorn.run("web_server:app", host="0.0.0.0", port=8000)
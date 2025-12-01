import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from scripts.app_settings import PROJECT_ROOT

router = APIRouter()

@router.get("/api/docs-languages")
def get_docs_languages():
    docs_dir = os.path.join(PROJECT_ROOT, 'docs')
    if not os.path.isdir(docs_dir): return []
    return sorted([item for item in os.listdir(docs_dir) if os.path.isdir(os.path.join(docs_dir, item))])

def _scan_docs_recursive(directory, parent_key=''):
    nodes = []
    if not os.path.isdir(directory): return []
    for item in sorted(os.listdir(directory)):
        path = os.path.join(directory, item)
        key = os.path.join(parent_key, item)
        if os.path.isdir(path):
            children = _scan_docs_recursive(path, key)
            if children:
                nodes.append({"title": item, "key": key, "children": children})
        elif item.endswith(".md"):
            nodes.append({"title": item.replace(".md", ""), "key": key, "isLeaf": True})
    return nodes

@router.get("/api/docs-tree")
def get_docs_tree():
    docs_dir = os.path.join(PROJECT_ROOT, 'docs')
    tree_data = {}
    if not os.path.isdir(docs_dir): return {}
    for lang in os.listdir(docs_dir):
        lang_path = os.path.join(docs_dir, lang)
        if os.path.isdir(lang_path):
            tree_data[lang] = _scan_docs_recursive(lang_path, lang)
    return tree_data

@router.get("/api/doc-content", response_class=PlainTextResponse)
def get_doc_content(path: str = Query(...)):
    if ".." in path:
        raise HTTPException(status_code=400, detail="Invalid path.")
    docs_dir = os.path.abspath(os.path.join(PROJECT_ROOT, 'docs'))
    requested_path = os.path.abspath(os.path.join(docs_dir, path))
    if not requested_path.startswith(docs_dir):
        raise HTTPException(status_code=403, detail="Access forbidden.")
    if not os.path.isfile(requested_path) or not requested_path.endswith(".md"):
        raise HTTPException(status_code=404, detail="File not found.")
    with open(requested_path, 'r', encoding='utf-8') as f:
        return f.read()

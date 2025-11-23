import sys
import os
import shutil
import logging

# Add scripts to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from scripts.core.project_manager import ProjectManager
from scripts.app_settings import PROJECTS_DB_PATH

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_project_enhancements():
    # Use a temporary DB for testing
    test_db_path = PROJECTS_DB_PATH + ".test"
    if os.path.exists(test_db_path):
        os.remove(test_db_path)
    
    pm = ProjectManager(db_path=test_db_path)
    
    # 1. Create Project
    logger.info("Creating test project...")
    # Create a dummy folder
    dummy_folder = "test_project_folder"
    if not os.path.exists(dummy_folder):
        os.makedirs(dummy_folder)
        with open(os.path.join(dummy_folder, "test.yml"), "w") as f:
            f.write("l_english:\n key:0 \"value\"")
            
    try:
        project = pm.create_project("Test Project", dummy_folder, "stellaris")
        project_id = project['project_id']
        logger.info(f"Project created: {project_id}")
        
        # 2. Verify Notes
        logger.info("Verifying notes...")
        pm.update_project_notes(project_id, "This is a test note.")
        p = pm.get_project(project_id)
        assert p['notes'] == "This is a test note.", f"Notes mismatch: {p['notes']}"
        logger.info("Notes verified.")
        
        # 3. Verify Status Transitions
        logger.info("Verifying status transitions...")
        
        # Active -> Archived
        pm.update_project_status(project_id, "archived")
        p = pm.get_project(project_id)
        assert p['status'] == "archived", f"Status mismatch: {p['status']}"
        
        # Archived -> Deleted
        pm.update_project_status(project_id, "deleted")
        p = pm.get_project(project_id)
        assert p['status'] == "deleted", f"Status mismatch: {p['status']}"
        
        # Deleted -> Active (Restore)
        pm.update_project_status(project_id, "active")
        p = pm.get_project(project_id)
        assert p['status'] == "active", f"Status mismatch: {p['status']}"
        
        logger.info("Status transitions verified.")
        
        # 4. Verify Filtering
        logger.info("Verifying filtering...")
        pm.update_project_status(project_id, "archived")
        
        active_projects = pm.get_projects(status="active")
        archived_projects = pm.get_projects(status="archived")
        
        assert len(active_projects) == 0, "Should have 0 active projects"
        assert len(archived_projects) == 1, "Should have 1 archived project"
        
        logger.info("Filtering verified.")
        
        # Cleanup
        pm.delete_project(project_id, delete_source_files=True)
        logger.info("Cleanup successful.")
        
    finally:
        if os.path.exists(dummy_folder):
            shutil.rmtree(dummy_folder)
        if os.path.exists(test_db_path):
            os.remove(test_db_path)

if __name__ == "__main__":
    verify_project_enhancements()

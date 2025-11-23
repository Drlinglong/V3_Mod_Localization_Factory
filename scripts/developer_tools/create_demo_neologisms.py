import json
import os
import uuid
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from scripts.core.neologism_manager import NeologismManager, Candidate
from scripts.core.project_manager import ProjectManager

def create_demo_data(project_id: str = None):
    """
    Create demo neologism candidates for a project.
    If project_id is not provided, uses the first available project.
    """
    manager = NeologismManager()
    project_mgr = ProjectManager()
    
    # Get project or use first available
    if not project_id:
        projects = project_mgr.get_projects()
        if not projects:
            print("ERROR: No projects found. Please create a project first.")
            return
        project_id = projects[0]['project_id']
        print(f"Using project: {projects[0]['name']} ({project_id})")
    
    demo_candidates = [
        Candidate(
            id=str(uuid.uuid4()),
            project_id=project_id,  # NEW: bind to project
            original="Aetherophasic Engine",
            context_snippets=[
                "The Aetherophasic Engine is a megastructure capable of harvesting the very fabric of reality.",
                "Constructing the Aetherophasic Engine requires massive amounts of Dark Matter."
            ],
            suggestion="以太相引擎",
            reasoning="Aetherophasic is a compound of Aether (以太) and Phasic (相位的). Engine translates to 引擎. This term refers to a specific Stellaris crisis megastructure.",
            status="pending",
            source_file="events/crisis_events_2.txt"
        ),
        Candidate(
            id=str(uuid.uuid4()),
            project_id=project_id,
            original="Blorg Commonality",
            context_snippets=[
                "The Blorg Commonality has sent a diplomatic insult.",
                "Refugees from the Blorg Commonality are arriving on our worlds."
            ],
            suggestion="布洛格公社",
            reasoning="Blorg is a species name, transliterated as 布洛格. Commonality implies a shared or communal government, translated as 公社 or 共联. '布洛格公社' sounds like a standard sci-fi faction name.",
            status="pending",
            source_file="prescripted_countries/00_blorg.txt"
        ),
        Candidate(
            id=str(uuid.uuid4()),
            project_id=project_id,
            original="Zro Distillation",
            context_snippets=[
                "New technology researched: Zro Distillation.",
                "Zro Distillation allows us to refine the exotic dust into a usable psionic fuel."
            ],
            suggestion="泽洛蒸馏术",
            reasoning="Zro is a special resource in Stellaris, usually translated as 泽洛. Distillation is 蒸馏. Combined as a technology name.",
            status="pending",
            source_file="common/technology/00_psionics.txt"
        ),
        Candidate(
            id=str(uuid.uuid4()),
            project_id=project_id,
            original="Grand Herald",
            context_snippets=[
                "We have discovered an ancient titan known as the Grand Herald.",
                "The Grand Herald is fully operational and awaits our command."
            ],
            suggestion="宏伟先驱者",
            reasoning="Grand means 宏伟 or 盛大. Herald means 先驱 or 传令官. '宏伟先驱者' fits the majestic tone of a Titan ship.",
            status="pending",
            source_file="events/ancient_relics_events.txt"
        )
    ]
    
    # Use new project-specific save method
    manager.save_candidates(project_id, demo_candidates)
    print(f"✅ Successfully created {len(demo_candidates)} demo candidates for project {project_id}")

if __name__ == "__main__":
    # Allow specifying project_id as command line argument
    project_id = sys.argv[1] if len(sys.argv) > 1 else None
    create_demo_data(project_id)

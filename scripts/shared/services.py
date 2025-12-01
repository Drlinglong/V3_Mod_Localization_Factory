from scripts.core.glossary_manager import GlossaryManager
from scripts.core.project_manager import ProjectManager
from scripts.core.archive_manager import ArchiveManager

# Initialize Managers
# These are singletons effectively
glossary_manager = GlossaryManager()
project_manager = ProjectManager()
archive_manager = ArchiveManager()

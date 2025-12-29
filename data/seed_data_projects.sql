-- Remis Projects DB Seed Data
BEGIN TRANSACTION;

-- Schema for projects
CREATE TABLE projects (
                project_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                game_id TEXT NOT NULL,
                source_path TEXT NOT NULL,
                target_path TEXT,
                status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            , notes TEXT, last_modified TEXT, source_language TEXT DEFAULT 'english');
-- Schema for project_files
CREATE TABLE project_files (
                file_id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                status TEXT DEFAULT 'todo',
                original_key_count INTEGER DEFAULT 0,
                line_count INTEGER DEFAULT 0,
                file_type TEXT DEFAULT 'source',
                FOREIGN KEY (project_id) REFERENCES projects (project_id) ON DELETE CASCADE,
                UNIQUE(project_id, file_path)
            );
COMMIT;

-- JARVIS 2.0 - Schéma Base de Données
-- Gestion de projets avec conversations et messages

-- Table projects
CREATE TABLE IF NOT EXISTS projects (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table conversations
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    project_id TEXT,
    agent_id TEXT NOT NULL,
    title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE
);

-- Table messages
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    conversation_id TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE
);

-- Index pour performance
CREATE INDEX IF NOT EXISTS idx_conversations_project ON conversations(project_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_messages_conversation ON messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp);

-- Table library_documents (Knowledge Base)
CREATE TABLE IF NOT EXISTS library_documents (
    id TEXT PRIMARY KEY,
    category TEXT NOT NULL CHECK(category IN ('libraries', 'methodologies', 'prompts', 'personal')),
    name TEXT NOT NULL,
    icon TEXT,
    description TEXT,
    content TEXT NOT NULL,
    tags TEXT, -- JSON array stringifié
    agents TEXT, -- JSON array stringifié
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Index pour performance library
CREATE INDEX IF NOT EXISTS idx_library_category ON library_documents(category);
CREATE INDEX IF NOT EXISTS idx_library_updated ON library_documents(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_library_name ON library_documents(name);

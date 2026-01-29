CREATE TABLE user_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    note_type TEXT NOT NULL DEFAULT 'Dynamic',
    embedding VECTOR(1536),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_notes_user_id ON user_notes(user_id);

CREATE TRIGGER update_user_notes_updated_at
    BEFORE UPDATE ON user_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- HNSW index for vector similarity search
CREATE INDEX idx_user_notes_embedding ON user_notes USING hnsw (embedding vector_cosine_ops);

CREATE TABLE user_notes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536), -- Default dimension for OpenAI text-embedding-3-small and text-embedding-ada-002
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger to update updated_at
CREATE TRIGGER update_user_notes_updated_at
    BEFORE UPDATE ON user_notes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- HNSW index for vector similarity search
CREATE INDEX idx_user_notes_embedding ON user_notes USING hnsw (embedding vector_cosine_ops);

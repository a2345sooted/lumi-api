CREATE TABLE chat_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR NOT NULL,
    thread_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    status VARCHAR NOT NULL DEFAULT 'PROCESSING',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_runs_user_thread ON chat_runs(user_id, thread_id);

CREATE TRIGGER update_chat_runs_updated_at
    BEFORE UPDATE ON chat_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

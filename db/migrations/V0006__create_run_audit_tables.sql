CREATE TABLE note_optimization_runs (
    user_id UUID PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    thread_id UUID,
    status TEXT NOT NULL DEFAULT 'PROCESSING',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TRIGGER update_note_optimization_runs_updated_at
    BEFORE UPDATE ON note_optimization_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TABLE chat_runs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    thread_id UUID NOT NULL,
    status TEXT NOT NULL DEFAULT 'PROCESSING',
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_chat_runs_user_thread ON chat_runs(user_id, thread_id);

CREATE TRIGGER update_chat_runs_updated_at
    BEFORE UPDATE ON chat_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

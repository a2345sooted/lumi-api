ALTER TABLE note_optimization_runs ADD COLUMN status VARCHAR DEFAULT 'PROCESSING';
ALTER TABLE note_optimization_runs ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;

CREATE TRIGGER update_note_optimization_runs_updated_at
    BEFORE UPDATE ON note_optimization_runs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

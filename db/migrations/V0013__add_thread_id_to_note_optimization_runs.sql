ALTER TABLE note_optimization_runs ADD COLUMN thread_id UUID;
ALTER TABLE note_optimization_runs ADD CONSTRAINT fk_note_optimization_runs_thread FOREIGN KEY (thread_id) REFERENCES conversations(id) ON DELETE CASCADE;

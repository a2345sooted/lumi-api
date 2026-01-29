ALTER TABLE users ADD COLUMN push_token TEXT;
ALTER TABLE users ADD COLUMN push_token_updated_at TIMESTAMP WITH TIME ZONE;

CREATE INDEX idx_users_push_token ON users(push_token);

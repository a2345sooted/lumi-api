CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sub TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_sub ON users(sub);

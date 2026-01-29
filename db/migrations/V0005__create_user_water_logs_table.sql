CREATE TABLE user_water_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount_oz DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_water_logs_user_id ON user_water_logs(user_id);
CREATE INDEX idx_user_water_logs_created_at ON user_water_logs(created_at);

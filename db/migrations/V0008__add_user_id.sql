-- Add user_id column to conversations
ALTER TABLE conversations ADD COLUMN user_id TEXT;
CREATE INDEX idx_conversations_user_id ON conversations(user_id);

-- Add user_id column to user_notes
ALTER TABLE user_notes ADD COLUMN user_id TEXT;
CREATE INDEX idx_user_notes_user_id ON user_notes(user_id);

-- Add user_id column to user_profiles
ALTER TABLE user_profiles ADD COLUMN user_id TEXT;
CREATE INDEX idx_user_profiles_user_id ON user_profiles(user_id);

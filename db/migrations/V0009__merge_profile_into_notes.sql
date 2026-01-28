-- Add note_type column to user_notes
ALTER TABLE user_notes ADD COLUMN note_type VARCHAR(50) DEFAULT 'Dynamic' NOT NULL;

-- Drop user_profiles table
DROP TABLE IF EXISTS user_profiles;

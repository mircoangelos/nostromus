-- Migration: Add decision_by_id to reports table
-- This allows tracking which analyst made each decision

-- Add the new column
ALTER TABLE reports ADD COLUMN decision_by_id INTEGER;

-- Add foreign key constraint
ALTER TABLE reports
ADD CONSTRAINT fk_reports_decision_by_user
FOREIGN KEY (decision_by_id) REFERENCES users(id);

-- Create index for faster lookups
CREATE INDEX idx_reports_decision_by_id ON reports(decision_by_id);

-- Log the migration
COMMENT ON COLUMN reports.decision_by_id IS 'Foreign key to users table - tracks which analyst made this decision';

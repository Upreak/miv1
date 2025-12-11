-- Migration A: Create prescreen and knowledge base tables
-- This migration adds the necessary tables for chatbot prescreening functionality

-- Create enum types first
DO $$ BEGIN
    CREATE TYPE question_type_enum AS ENUM ('text', 'number', 'select', 'multi_select', 'date', 'boolean');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE application_status_enum AS ENUM ('New', 'Screening', 'Interview', 'Offer', 'Rejected', 'Withdrawn');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE automation_status_enum AS ENUM ('New', 'Contacting...', 'Awaiting Reply', 'Live Chat', 'Intervention Needed', 'Completed', 'Declined');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create job_prescreen_questions table
CREATE TABLE IF NOT EXISTS job_prescreen_questions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    qid VARCHAR(50) NOT NULL,
    question_text TEXT NOT NULL,
    question_type question_type_enum NOT NULL,
    required BOOLEAN DEFAULT FALSE,
    must_have BOOLEAN DEFAULT FALSE,
    weight INTEGER DEFAULT 1,
    validation_rule TEXT,
    choices TEXT,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create prescreen_answers table
CREATE TABLE IF NOT EXISTS prescreen_answers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    question_id UUID NOT NULL REFERENCES job_prescreen_questions(id) ON DELETE CASCADE,
    answer_value TEXT NOT NULL,
    answer_metadata TEXT,
    question_score INTEGER DEFAULT 0,
    is_valid BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create job_faq table
CREATE TABLE IF NOT EXISTS job_faq (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    question_keywords TEXT,
    created_by VARCHAR(36) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_job_prescreen_questions_job_id ON job_prescreen_questions(job_id);
CREATE INDEX IF NOT EXISTS idx_job_prescreen_questions_qid ON job_prescreen_questions(qid);
CREATE INDEX IF NOT EXISTS idx_prescreen_answers_application_id ON prescreen_answers(application_id);
CREATE INDEX IF NOT EXISTS idx_prescreen_answers_question_id ON prescreen_answers(question_id);
CREATE INDEX IF NOT EXISTS idx_job_faq_job_id ON job_faq(job_id);

-- Add comments for documentation
COMMENT ON TABLE job_prescreen_questions IS 'Stores prescreen questions for jobs';
COMMENT ON TABLE prescreen_answers IS 'Stores answers to prescreen questions for applications';
COMMENT ON TABLE job_faq IS 'Stores FAQ entries for jobs and knowledge base';
COMMENT ON COLUMN job_prescreen_questions.qid IS 'Unique question identifier (e.g., ps_current_ctc, ps_expected_ctc)';
COMMENT ON COLUMN job_prescreen_questions.must_have IS 'Critical questions that must be answered for job matching';
COMMENT ON COLUMN prescreen_answers.answer_metadata IS 'JSON metadata about the answer (validation result, normalized value, etc.)';
COMMENT ON COLUMN prescreen_answers.question_score IS 'Score for this specific question (0-100)';
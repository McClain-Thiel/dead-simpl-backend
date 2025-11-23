-- Create ScorerType Enum
CREATE TYPE scorertype AS ENUM ('builtin', 'llm_judge', 'code');

-- Create Scorer Definitions Table
CREATE TABLE scorer_definitions (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scorer_type scorertype NOT NULL,
    configuration JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create Evaluation Profiles Table
CREATE TABLE evaluation_profiles (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    scorer_ids UUID[] NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create RunStatus Enum
CREATE TYPE runstatus AS ENUM ('PENDING', 'PROCESSING', 'COMPLETED', 'FAILED');

-- Create Evaluation Runs Table
CREATE TABLE evaluation_runs (
    id UUID PRIMARY KEY,
    profile_id UUID REFERENCES evaluation_profiles(id),
    dataset_path VARCHAR(255) NOT NULL,
    mlflow_run_id VARCHAR(255),
    status runstatus NOT NULL DEFAULT 'PENDING',
    summary_results JSONB,
    row_details_path VARCHAR(255),
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX ix_evaluation_runs_profile_id ON evaluation_runs(profile_id);

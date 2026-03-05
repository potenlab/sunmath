-- SunMath Database Schema Reference
-- This file is for documentation/inspection only. Alembic manages the actual schema.

-- ==================== NODE TABLES ====================

CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    grade_level INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE concepts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE questions (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    correct_answer TEXT NOT NULL,
    expected_form VARCHAR(20) DEFAULT 'simplified',
    target_grade INTEGER,
    grading_hints TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    grade_level INTEGER,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ==================== EDGE TABLES ====================

CREATE TABLE unit_concepts (
    unit_id INTEGER REFERENCES units(id),
    concept_id INTEGER REFERENCES concepts(id),
    PRIMARY KEY (unit_id, concept_id)
);

CREATE TABLE concept_prerequisites (
    concept_id INTEGER REFERENCES concepts(id),
    prerequisite_concept_id INTEGER REFERENCES concepts(id),
    PRIMARY KEY (concept_id, prerequisite_concept_id)
);

CREATE TABLE concept_relations (
    concept_id INTEGER REFERENCES concepts(id),
    related_concept_id INTEGER REFERENCES concepts(id),
    relation_type VARCHAR(50),
    PRIMARY KEY (concept_id, related_concept_id, relation_type)
);

CREATE TABLE question_evaluates (
    question_id INTEGER REFERENCES questions(id),
    concept_id INTEGER REFERENCES concepts(id),
    PRIMARY KEY (question_id, concept_id)
);

CREATE TABLE question_units (
    question_id INTEGER REFERENCES questions(id),
    unit_id INTEGER REFERENCES units(id),
    PRIMARY KEY (question_id, unit_id)
);

CREATE TABLE question_requires (
    question_id INTEGER REFERENCES questions(id),
    concept_id INTEGER REFERENCES concepts(id),
    PRIMARY KEY (question_id, concept_id)
);

-- ==================== HISTORY + SUPPORT TABLES ====================

CREATE TABLE student_answers (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    submitted_answer TEXT NOT NULL,
    is_correct BOOLEAN NOT NULL,
    judged_by VARCHAR(10) NOT NULL,
    reasoning TEXT,
    submitted_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_student_answers_student_id ON student_answers(student_id);
CREATE INDEX ix_student_answers_question_id ON student_answers(question_id);

CREATE TABLE student_concept_mastery (
    student_id INTEGER REFERENCES students(id),
    concept_id INTEGER REFERENCES concepts(id),
    mastery_level FLOAT DEFAULT 0.0,
    last_updated TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (student_id, concept_id)
);

CREATE TABLE wrong_answer_warehouse (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    question_id INTEGER NOT NULL REFERENCES questions(id),
    answer_id INTEGER NOT NULL REFERENCES student_answers(id),
    status VARCHAR(20) DEFAULT 'active',
    retry_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX ix_wrong_answer_warehouse_student_id ON wrong_answer_warehouse(student_id);
CREATE INDEX ix_wrong_answer_warehouse_status ON wrong_answer_warehouse(status);

CREATE TABLE answer_cache (
    id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(id),
    submitted_answer_hash VARCHAR(64) NOT NULL,
    is_correct BOOLEAN NOT NULL,
    judged_by VARCHAR(10) NOT NULL,
    reasoning TEXT,
    cached_at TIMESTAMP DEFAULT NOW(),
    UNIQUE (question_id, submitted_answer_hash)
);

CREATE TABLE admin_settings (
    key VARCHAR(100) PRIMARY KEY,
    value TEXT NOT NULL,
    description TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE student_diagnoses (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    diagnosis_data JSONB NOT NULL,
    generated_at TIMESTAMP DEFAULT NOW()
);

-- Seed data for default prescreen questions
-- This file contains the default QIDs and questions for the chatbot module

-- Insert default prescreen questions
INSERT INTO job_prescreen_questions (job_id, qid, question_text, question_type, required, must_have, weight, validation_rule, choices, created_by)
VALUES 
-- Current CTC
('00000000-0000-0000-0000-000000000000', 'ps_current_ctc', 'What is your current CTC (Cost to Company) in LPA?', 'number', true, true, 10, '{"min": 0, "max": 100}', NULL, 'system'),

-- Expected CTC
('00000000-0000-0000-0000-000000000000', 'ps_expected_ctc', 'What is your expected CTC (Cost to Company) in LPA?', 'number', true, true, 10, '{"min": 0, "max": 100}', NULL, 'system'),

-- Notice Period
('00000000-0000-0000-0000-000000000000', 'ps_notice_period', 'What is your notice period in days?', 'number', true, true, 8, '{"min": 0, "max": 365}', NULL, 'system'),

-- Total Experience
('00000000-0000-0000-0000-000000000000', 'ps_total_experience', 'What is your total work experience in years?', 'number', true, true, 12, '{"min": 0, "max": 50}', NULL, 'system'),

-- Key Skills
('00000000-0000-0000-0000-000000000000', 'ps_key_skills', 'What are your key technical skills?', 'multi_select', true, true, 15, NULL, '["Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue.js", "Node.js", "FastAPI", "Django", "Spring Boot", "SQL", "NoSQL", "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "CI/CD"]', 'system'),

-- Has Other Offers
('00000000-0000-0000-0000-000000000000', 'ps_has_offers', 'Do you currently have any other job offers?', 'boolean', false, false, 5, NULL, NULL, 'system'),

-- Preferred Location
('00000000-0000-0000-0000-000000000000', 'ps_preferred_location', 'What are your preferred work locations?', 'multi_select', false, false, 6, NULL, '["Bangalore", "Hyderabad", "Pune", "Chennai", "Delhi/NCR", "Mumbai", "Remote", "Hybrid"]', 'system'),

-- Current Location
('00000000-0000-0000-0000-000000000000', 'ps_current_location', 'What is your current location?', 'select', true, false, 4, NULL, '["Bangalore", "Hyderabad", "Pune", "Chennai", "Delhi/NCR", "Mumbai", "Kolkata", "Remote", "Other"]', 'system'),

-- Availability for Interview
('00000000-0000-0000-0000-000000000000', 'ps_availability', 'When are you available for interviews?', 'select', false, false, 3, NULL, '["Immediately", "1-2 weeks", "3-4 weeks", "1 month+", "Negotiable"]', 'system'),

-- Best Time to Contact
('00000000-0000-0000-0000-000000000000', 'ps_best_time_to_contact', 'What is the best time to contact you?', 'select', false, false, 2, NULL, '["Morning (9AM-12PM)", "Afternoon (12PM-4PM)", "Evening (4PM-7PM)", "Flexible"]', 'system'),

-- Work Mode Preference
('00000000-0000-0000-0000-000000000000', 'ps_work_mode', 'What is your preferred work mode?', 'select', false, false, 4, NULL, '["Work from Office", "Work from Home", "Hybrid", "Flexible"]', 'system'),

-- Relocation Willingness
('00000000-0000-0000-0000-000000000000', 'ps_relocate', 'Are you willing to relocate?', 'boolean', false, false, 3, NULL, NULL, 'system'),

-- Shift Preference
('00000000-0000-0000-0000-000000000000', 'ps_shift_preference', 'What is your shift preference?', 'select', false, false, 3, NULL, '["Day Shift", "Night Shift", "Flexible", "No Preference"]', 'system'),

-- Visa Status
('00000000-0000-0000-0000-000000000000', 'ps_visa_status', 'What is your current work authorization status?', 'select', false, false, 4, NULL, '["Citizen", "Permanent Resident", "H1B", "H4", "L1", "F1(OPT)", "Other Work Visa", "Not Required"]', 'system'),

-- Certifications
('00000000-0000-0000-0000-000000000000', 'ps_certifications', 'Do you have any relevant certifications?', 'text', false, false, 2, NULL, NULL, 'system'),

-- Education Level
('00000000-0000-0000-0000-000000000000', 'ps_education', 'What is your highest level of education?', 'select', false, false, 3, NULL, '["High School", "Diploma", "Bachelor Degree", "Master Degree", "PhD", "Other"]', 'system'),

-- Industry Experience
('00000000-0000-0000-0000-000000000000', 'ps_industry_experience', 'Which industries do you have experience in?', 'multi_select', false, false, 4, NULL, '["IT Services", "Product", "Banking/Finance", "Healthcare", "E-commerce", "Education", "Manufacturing", "Telecom", "Media", "Other"]', 'system'),

-- Management Experience
('00000000-0000-0000-0000-000000000000', 'ps_management_experience', 'Do you have any management/leadership experience?', 'boolean', false, false, 3, NULL, NULL, 'system'),

-- Salary Negotiable
('00000000-0000-0000-0000-000000000000', 'ps_salary_negotiable', 'Is your expected salary negotiable?', 'boolean', false, false, 2, NULL, NULL, 'system'),

-- Reason for Job Change
('00000000-0000-0000-0000-000000000000', 'ps_reason_for_change', 'What is your primary reason for looking for a new job?', 'text', false, false, 2, NULL, NULL, 'system');

-- Note: job_id is set to a dummy UUID '00000000-0000-0000-0000-000000000000' for default questions
-- These questions can be copied to specific jobs when needed
-- The created_by field is set to 'system' for default questions
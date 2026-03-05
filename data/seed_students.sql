-- SunMath Seed Data: Students + Answers + Mastery + Wrong Answer Warehouse
-- 3 students with designed wrong answer patterns for demo scenarios
--
-- Student A (Kim Minjun): Root cause = completing_the_square
--   Fails: quadratic inequality (Q12), vertex finding (Q22), circle equation (Q36)
--   All three failures trace back to completing_the_square weakness
--
-- Student B (Lee Soyeon): Root cause = radian_measure
--   Fails: trig equation in radians (Q26), vector angle in radians (Q35)
--   Both failures trace back to radian_measure weakness
--
-- Student C (Park Jihoon): Control student with mixed performance

-- ==================== STUDENTS (3) ====================

INSERT INTO students (id, name, grade_level) VALUES
(1, 'Kim Minjun', 10),     -- Student A: completing_the_square weakness
(2, 'Lee Soyeon', 10),     -- Student B: radian_measure weakness
(3, 'Park Jihoon', 11);    -- Student C: control, mixed performance

SELECT setval('students_id_seq', (SELECT MAX(id) FROM students));

-- ==================== STUDENT ANSWERS ====================
-- Student A (id=1): 10 answers, 7 correct, 3 wrong (all linked to completing_the_square)

INSERT INTO student_answers (id, student_id, question_id, submitted_answer, is_correct, judged_by, reasoning) VALUES
-- Student A correct answers
(1, 1, 9,  '12', true, 'sympy',
 'Correct. 3x - 7 = 2x + 5 => x = 12.'),
(2, 1, 7,  '2x + 7y', true, 'sympy',
 'Correct. Like terms combined properly: 3x - x = 2x, 2y + 5y = 7y.'),
(3, 1, 17, '(x + 2)(x + 3)', true, 'sympy',
 'Correct. Factored form of x^2 + 5x + 6.'),
(4, 1, 20, 'x = -1, x = 5', true, 'sympy',
 'Correct. (x+1)(x-5) = 0, solutions are x = -1 and x = 5.'),
(5, 1, 15, '2x^2 - 5x - 12', true, 'sympy',
 'Correct. FOIL expansion of (2x+3)(x-4).'),
(6, 1, 11, 'x < 4', true, 'sympy',
 'Correct. 2x - 3 < 5 => 2x < 8 => x < 4.'),
(7, 1, 16, 'x^2 + 6x + 9', true, 'sympy',
 'Correct. (x+3)^2 = x^2 + 6x + 9.'),

-- Student A WRONG answers (all trace to completing_the_square weakness)
(8, 1, 12, 'x > 2 \text{ and } x > 3', false, 'sympy',
 'Incorrect. Student factored correctly to (x-2)(x-3) > 0 but failed sign analysis. Should be x < 2 OR x > 3, not AND. Root cause: does not understand completing the square approach for analyzing quadratic expressions.'),

(9, 1, 22, '(4, 7)', false, 'llm',
 'Incorrect. Student appears to have read coefficients directly (-4 and 7) instead of completing the square. Correct vertex is (2, 3) from y = (x-2)^2 + 3. Root cause: cannot apply completing the square technique.'),

(10, 1, 36, 'Center: (6, 4), Radius: 12', false, 'llm',
 'Incorrect. Student read coefficients directly from -6x + 4y - 12 = 0 without completing the square. Correct: (x-3)^2 + (y+2)^2 = 25, center (3,-2), radius 5. Root cause: cannot complete the square.'),

-- Student B (id=2): 8 answers, 6 correct, 2 wrong (all linked to radian_measure)

-- Student B correct answers
(11, 2, 9,  '12', true, 'sympy',
 'Correct. Standard linear equation solving.'),
(12, 2, 17, '(x + 2)(x + 3)', true, 'sympy',
 'Correct. Standard quadratic factoring.'),
(13, 2, 25, '\frac{\sqrt{3}}{2}', true, 'sympy',
 'Correct. Knows the standard trigonometric ratio for pi/3.'),
(14, 2, 28, '39', true, 'sympy',
 'Correct. a_10 = 3 + 9*4 = 39.'),
(15, 2, 13, '3', true, 'sympy',
 'Correct. Slope = (11-5)/(4-2) = 3.'),
(16, 2, 20, 'x = -1, x = 5', true, 'sympy',
 'Correct. Factored and solved quadratic.'),

-- Student B WRONG answers (all trace to radian_measure weakness)
(17, 2, 26, 'x = 30°, x = 150°', false, 'llm',
 'Incorrect. Student found correct reference angles but expressed them in degrees instead of radians. The problem asks for solutions in [0, 2pi] which requires radian notation. Correct: x = pi/6, x = 5pi/6. Root cause: weak understanding of radian measure.'),

(18, 2, 35, '60°', false, 'llm',
 'Incorrect. Student correctly computed the angle as 60 degrees but failed to convert to radians as requested. Correct answer: pi/3 radians. Root cause: does not naturally think in radians, defaults to degrees.'),

-- Student C (id=3): 8 answers, 5 correct, 3 wrong (varied weaknesses)

-- Student C correct answers
(19, 3, 30, '9x^2 - 4x + 1', true, 'sympy',
 'Correct. Power rule applied correctly to each term.'),
(20, 3, 32, 'x^4 - 3x^2 + 2x + C', true, 'sympy',
 'Correct. Reverse power rule with constant of integration.'),
(21, 3, 20, 'x = -1, x = 5', true, 'sympy',
 'Correct. Standard quadratic factoring.'),
(22, 3, 34, '-7', true, 'sympy',
 'Correct. Dot product: 3(1) + (-1)(4) + 2(-3) = -7.'),
(23, 3, 14, 'y = 2x + 1', true, 'sympy',
 'Correct. Point-slope form converted to slope-intercept.'),

-- Student C WRONG answers (varied issues)
(24, 3, 33, '8', false, 'sympy',
 'Incorrect. Student computed antiderivative as x^3 + x but evaluated as (8+2)-(0) = 10, got arithmetic wrong somewhere. Submitted 8 instead of 10.'),

(25, 3, 31, 'x = 0', false, 'llm',
 'Incorrect. Found only one critical point. f''(x) = 3x^2 - 6x = 3x(x-2) = 0 gives x=0 AND x=2. Student missed x=2. Incomplete solution.'),

(26, 3, 21, 'x = 0.5, x = 2', false, 'sympy',
 'Incorrect. Got x = 1/2 correct but second root should be x = -2, not x = 2. Sign error in quadratic formula application.');

SELECT setval('student_answers_id_seq', (SELECT MAX(id) FROM student_answers));

-- ==================== STUDENT CONCEPT MASTERY ====================
-- Mastery levels from 0.0 (no understanding) to 1.0 (complete mastery)

INSERT INTO student_concept_mastery (student_id, concept_id, mastery_level) VALUES
-- Student A (id=1): Strong basics, weak on completing_the_square chain
(1, 1, 0.95),   -- addition_subtraction: strong
(1, 2, 0.90),   -- multiplication_division: strong
(1, 11, 0.85),  -- variable_expression: good
(1, 12, 0.85),  -- like_terms: good
(1, 13, 0.80),  -- distributive_property: good
(1, 14, 0.90),  -- linear_equation_solving: strong
(1, 15, 0.75),  -- linear_inequality: decent
(1, 22, 0.70),  -- polynomial_multiplication: OK
(1, 23, 0.50),  -- multiplication_formulas: mediocre (upstream of root cause)
(1, 25, 0.55),  -- factoring_quadratic: mediocre
(1, 26, 0.20),  -- completing_the_square: VERY WEAK (ROOT CAUSE)
(1, 27, 0.30),  -- quadratic_formula: weak (depends on completing_the_square)
(1, 28, 0.50),  -- quadratic_equation_solving: mediocre
(1, 29, 0.25),  -- quadratic_inequality: weak (SYMPTOM)
(1, 30, 0.45),  -- quadratic_function: weak
(1, 31, 0.20),  -- vertex_form: very weak (SYMPTOM)
(1, 52, 0.20),  -- circle_equation: very weak (SYMPTOM)
(1, 16, 0.80),  -- coordinate_plane: good
(1, 17, 0.75),  -- slope: decent

-- Student B (id=2): Strong overall, weak on radian_measure chain
(2, 1, 0.90),   -- addition_subtraction: strong
(2, 2, 0.90),   -- multiplication_division: strong
(2, 14, 0.85),  -- linear_equation_solving: good
(2, 25, 0.80),  -- factoring_quadratic: good
(2, 28, 0.80),  -- quadratic_equation_solving: good
(2, 34, 0.75),  -- angle_basics: decent (understands degrees)
(2, 35, 0.20),  -- radian_measure: VERY WEAK (ROOT CAUSE)
(2, 36, 0.70),  -- trigonometric_ratios: decent (knows values)
(2, 37, 0.35),  -- trigonometric_functions: weak (SYMPTOM)
(2, 51, 0.30),  -- vector_dot_product: weak (SYMPTOM - angle part)
(2, 50, 0.75),  -- vector_operations: decent
(2, 49, 0.80),  -- vector_basics: good
(2, 17, 0.85),  -- slope: good
(2, 40, 0.90),  -- sequence_arithmetic: strong
(2, 16, 0.85),  -- coordinate_plane: good
(2, 5, 0.75),   -- fraction_operations: decent

-- Student C (id=3): Advanced student, varied performance
(3, 1, 0.95),   -- addition_subtraction: strong
(3, 2, 0.95),   -- multiplication_division: strong
(3, 14, 0.90),  -- linear_equation_solving: strong
(3, 25, 0.85),  -- factoring_quadratic: good
(3, 28, 0.80),  -- quadratic_equation_solving: good
(3, 45, 0.75),  -- derivative_rules: decent
(3, 46, 0.60),  -- derivative_applications: mediocre
(3, 47, 0.65),  -- integral_definition: mediocre
(3, 48, 0.60),  -- integral_rules: mediocre
(3, 51, 0.85),  -- vector_dot_product: good
(3, 27, 0.65),  -- quadratic_formula: mediocre (sign errors)
(3, 17, 0.80),  -- slope: good
(3, 18, 0.80);  -- linear_function: good

-- ==================== WRONG ANSWER WAREHOUSE ====================
-- Only wrong answers go here. Links to student_answers records.

INSERT INTO wrong_answer_warehouse (id, student_id, question_id, answer_id, status, retry_count) VALUES
-- Student A's wrong answers (completing_the_square root cause)
(1, 1, 12, 8,  'active', 0),    -- Q12: quadratic inequality
(2, 1, 22, 9,  'active', 0),    -- Q22: vertex finding
(3, 1, 36, 10, 'active', 0),    -- Q36: circle equation

-- Student B's wrong answers (radian_measure root cause)
(4, 2, 26, 17, 'active', 0),    -- Q26: trig equation in radians
(5, 2, 35, 18, 'active', 0),    -- Q35: vector angle in radians

-- Student C's wrong answers (varied)
(6, 3, 33, 24, 'active', 0),    -- Q33: definite integral arithmetic error
(7, 3, 31, 25, 'active', 0),    -- Q31: incomplete critical points
(8, 3, 21, 26, 'active', 0);    -- Q21: sign error in quadratic formula

SELECT setval('wrong_answer_warehouse_id_seq', (SELECT MAX(id) FROM wrong_answer_warehouse));

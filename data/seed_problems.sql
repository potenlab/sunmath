-- SunMath Seed Data: Questions + Edge Links
-- 37 problems (2-3 per unit) with evaluation concepts, required concepts, and unit links

-- ==================== QUESTIONS (37) ====================

INSERT INTO questions (id, content, correct_answer, expected_form, target_grade, grading_hints) VALUES

-- Unit 1: Basic Arithmetic Operations (Q1-Q2)
(1,
 'Calculate: $24 \times 37 + 24 \times 63$',
 '2400',
 'numeric', 3,
 'Student should recognize the distributive property: 24*(37+63) = 24*100 = 2400. Accept any valid computation path.'),

(2,
 'Evaluate: $(48 + 36) \div 12$',
 '7',
 'numeric', 3,
 'Order of operations: parentheses first, then division. (48+36)=84, 84/12=7.'),

-- Unit 2: Fractions (Q3-Q4)
(3,
 'Simplify $\frac{24}{36}$ to lowest terms.',
 '\frac{2}{3}',
 'simplified', 4,
 'GCD of 24 and 36 is 12. Accept equivalent representations like 2/3.'),

(4,
 'Calculate $\frac{3}{4} + \frac{2}{3}$. Express your answer as a simplified fraction.',
 '\frac{17}{12}',
 'simplified', 4,
 'Common denominator is 12. 9/12 + 8/12 = 17/12. Accept 1 5/12 as mixed number.'),

-- Unit 3: Decimals and Percentages (Q5)
(5,
 'What is 35% of 240?',
 '84',
 'numeric', 5,
 'Method: 0.35 * 240 = 84. Accept decimal 84.0.'),

-- Unit 4: Ratios and Proportions (Q6)
(6,
 'If $x : 3 = 4 : 6$, find $x$.',
 '2',
 'numeric', 6,
 'Cross multiply: 6x = 12, x = 2. Or simplify ratio: 4:6 = 2:3, so x = 2.'),

-- Unit 5: Algebraic Expressions (Q7-Q8)
(7,
 'Simplify: $3x + 2y - x + 5y$',
 '2x + 7y',
 'simplified', 7,
 'Combine like terms: (3x - x) + (2y + 5y) = 2x + 7y. Terms may be in any order.'),

(8,
 'Expand and simplify: $3(2x - 4) + 2(x + 5)$',
 '8x - 2',
 'expanded', 7,
 'Distribute: 6x - 12 + 2x + 10 = 8x - 2. Accept equivalent forms.'),

-- Unit 6: Linear Equations (Q9-Q10)
(9,
 'Solve for $x$: $3x - 7 = 2x + 5$',
 '12',
 'numeric', 7,
 'Subtract 2x: x - 7 = 5. Add 7: x = 12.'),

(10,
 'Solve for $x$: $\frac{x+3}{2} = \frac{2x-1}{3}$',
 '11',
 'numeric', 7,
 'Cross multiply: 3(x+3) = 2(2x-1). 3x+9 = 4x-2. x = 11.'),

-- Unit 7: Inequalities (Q11-Q12)
(11,
 'Solve the inequality: $2x - 3 < 5$',
 'x < 4',
 'simplified', 8,
 'Add 3: 2x < 8. Divide by 2: x < 4. Accept interval notation (-inf, 4).'),

(12,
 'Solve the inequality: $x^2 - 5x + 6 > 0$',
 'x < 2 \text{ or } x > 3',
 'simplified', 9,
 'Factor: (x-2)(x-3) > 0. Sign analysis: positive when x < 2 or x > 3. REQUIRES factoring and completing the square concepts. Accept interval notation (-inf, 2) U (3, inf).'),

-- Unit 8: Functions and Graphs (Q13-Q14)
(13,
 'Find the slope of the line passing through the points $(2, 5)$ and $(4, 11)$.',
 '3',
 'numeric', 8,
 'Slope = (11-5)/(4-2) = 6/2 = 3.'),

(14,
 'Write the equation of a line with slope 2 passing through the point $(1, 3)$.',
 'y = 2x + 1',
 'simplified', 8,
 'Point-slope: y - 3 = 2(x - 1). Simplify: y = 2x + 1. Accept equivalent forms.'),

-- Unit 9: Polynomial Operations (Q15-Q16)
(15,
 'Expand $(2x + 3)(x - 4)$.',
 '2x^2 - 5x - 12',
 'expanded', 8,
 'FOIL: 2x^2 - 8x + 3x - 12 = 2x^2 - 5x - 12.'),

(16,
 'Expand $(x + 3)^2$.',
 'x^2 + 6x + 9',
 'expanded', 8,
 'Apply (a+b)^2 = a^2 + 2ab + b^2. Must be fully expanded, not left as (x+3)^2.'),

-- Unit 10: Factoring (Q17-Q19)
(17,
 'Factor: $x^2 + 5x + 6$',
 '(x + 2)(x + 3)',
 'factored', 9,
 'Find two numbers that multiply to 6 and add to 5: 2 and 3. Must be in factored form.'),

(18,
 'Factor: $x^2 - 9$',
 '(x + 3)(x - 3)',
 'factored', 9,
 'Difference of squares: a^2 - b^2 = (a+b)(a-b). Must be factored, not expanded.'),

(19,
 'Express $x^2 + 6x + 4$ in the form $(x + a)^2 + b$.',
 '(x + 3)^2 - 5',
 'factored', 9,
 'Complete the square: x^2 + 6x + 9 - 9 + 4 = (x+3)^2 - 5. Tests completing the square skill.'),

-- Unit 11: Quadratic Equations (Q20-Q21)
(20,
 'Solve: $x^2 - 4x - 5 = 0$',
 'x = -1, x = 5',
 'numeric', 9,
 'Factor: (x+1)(x-5) = 0. Solutions: x = -1 or x = 5. Accept in any order.'),

(21,
 'Solve $2x^2 + 3x - 2 = 0$ using the quadratic formula.',
 'x = \frac{1}{2}, x = -2',
 'numeric', 9,
 'a=2, b=3, c=-2. Discriminant=9+16=25. x = (-3+/-5)/4. x = 1/2 or x = -2.'),

-- Unit 12: Quadratic Functions (Q22-Q23)
(22,
 'Find the vertex of the parabola $y = x^2 - 4x + 7$.',
 '(2, 3)',
 'numeric', 10,
 'Complete the square: y = (x-2)^2 + 3. Vertex is (2,3). REQUIRES completing the square. Accept as ordered pair.'),

(23,
 'Convert $y = x^2 + 6x + 5$ to vertex form.',
 'y = (x + 3)^2 - 4',
 'factored', 10,
 'Complete the square: x^2 + 6x + 9 - 9 + 5 = (x+3)^2 - 4. Must be in vertex form a(x-h)^2+k.'),

-- Unit 13: Trigonometry (Q24-Q27)
(24,
 'Convert $120°$ to radians.',
 '\frac{2\pi}{3}',
 'simplified', 10,
 'Multiply by pi/180: 120 * pi/180 = 2pi/3. Must be simplified fraction of pi.'),

(25,
 'Find the exact value of $\sin\left(\frac{\pi}{3}\right)$.',
 '\frac{\sqrt{3}}{2}',
 'simplified', 10,
 'Standard value: sin(60 degrees) = sin(pi/3) = sqrt(3)/2. Must be exact, not decimal.'),

(26,
 'Find all values of $x$ in $[0, 2\pi]$ such that $\sin(x) = \frac{1}{2}$.',
 'x = \frac{\pi}{6}, x = \frac{5\pi}{6}',
 'simplified', 10,
 'sin(x) = 1/2 at pi/6 and 5pi/6 in [0, 2pi]. REQUIRES radian measure understanding. Must give both solutions in radians.'),

(27,
 'Prove that $\sin^2(\theta) + \cos^2(\theta) = 1$ using the unit circle definition.',
 'On the unit circle, a point is (cos(theta), sin(theta)). Since it lies on x^2 + y^2 = 1, substituting gives cos^2(theta) + sin^2(theta) = 1.',
 'proof', 10,
 'Must reference the unit circle and the equation x^2+y^2=1. Accept any logically complete proof.'),

-- Unit 14: Sequences and Series (Q28-Q29)
(28,
 'Find the 10th term of the arithmetic sequence: $3, 7, 11, 15, \ldots$',
 '39',
 'numeric', 10,
 'a_1 = 3, d = 4. a_10 = 3 + (10-1)*4 = 3 + 36 = 39.'),

(29,
 'Find the sum of the first 20 terms of the arithmetic sequence: $2, 5, 8, 11, \ldots$',
 '610',
 'numeric', 10,
 'a_1 = 2, d = 3, n = 20. a_20 = 2 + 19*3 = 59. S_20 = 20*(2+59)/2 = 20*61/2 = 610.'),

-- Unit 15: Calculus - Derivatives (Q30-Q31)
(30,
 'Find $\frac{d}{dx}(3x^3 - 2x^2 + x - 5)$.',
 '9x^2 - 4x + 1',
 'simplified', 11,
 'Power rule: d/dx(ax^n) = nax^(n-1). Term by term: 9x^2 - 4x + 1.'),

(31,
 'Find the critical points of $f(x) = x^3 - 3x^2 + 2$.',
 'x = 0, x = 2',
 'numeric', 11,
 'f''(x) = 3x^2 - 6x = 3x(x-2) = 0. Critical points at x = 0 and x = 2.'),

-- Unit 16: Calculus - Integration (Q32-Q33)
(32,
 'Find $\int (4x^3 - 6x + 2)\, dx$.',
 'x^4 - 3x^2 + 2x + C',
 'simplified', 11,
 'Reverse power rule term by term. Must include constant C.'),

(33,
 'Evaluate $\int_0^2 (3x^2 + 1)\, dx$.',
 '10',
 'numeric', 11,
 'Antiderivative: x^3 + x. Evaluate: (8+2) - (0+0) = 10.'),

-- Unit 17: Vectors (Q34-Q35)
(34,
 'Calculate the dot product: $\vec{a} \cdot \vec{b}$ where $\vec{a} = (3, -1, 2)$ and $\vec{b} = (1, 4, -3)$.',
 '-7',
 'numeric', 11,
 'Dot product: 3*1 + (-1)*4 + 2*(-3) = 3 - 4 - 6 = -7.'),

(35,
 'Find the angle between vectors $\vec{a} = (1, 0)$ and $\vec{b} = (1, \sqrt{3})$ in radians.',
 '\frac{\pi}{3}',
 'simplified', 11,
 'cos(theta) = (a . b)/(|a||b|) = 1/(1*2) = 1/2. theta = pi/3. REQUIRES radian measure. Must be in radians.'),

-- Unit 18: Circle Equations (Q36-Q37)
(36,
 'Find the center and radius of the circle: $x^2 + y^2 - 6x + 4y - 12 = 0$.',
 'Center: (3, -2), Radius: 5',
 'numeric', 10,
 'Complete the square: (x-3)^2 + (y+2)^2 = 25. Center (3,-2), radius 5. REQUIRES completing the square.'),

(37,
 'Write the equation of a circle with center $(2, -1)$ and radius $3$.',
 '(x - 2)^2 + (y + 1)^2 = 9',
 'expanded', 10,
 'Standard form: (x-h)^2 + (y-k)^2 = r^2. Substituting: (x-2)^2 + (y+1)^2 = 9.');

SELECT setval('questions_id_seq', (SELECT MAX(id) FROM questions));

-- ==================== QUESTION-UNIT LINKS ====================

INSERT INTO question_units (question_id, unit_id) VALUES
(1, 1), (2, 1),           -- Q1-Q2 -> Unit 1
(3, 2), (4, 2),           -- Q3-Q4 -> Unit 2
(5, 3),                    -- Q5 -> Unit 3
(6, 4),                    -- Q6 -> Unit 4
(7, 5), (8, 5),           -- Q7-Q8 -> Unit 5
(9, 6), (10, 6),          -- Q9-Q10 -> Unit 6
(11, 7), (12, 7),         -- Q11-Q12 -> Unit 7
(13, 8), (14, 8),         -- Q13-Q14 -> Unit 8
(15, 9), (16, 9),         -- Q15-Q16 -> Unit 9
(17, 10), (18, 10), (19, 10), -- Q17-Q19 -> Unit 10
(20, 11), (21, 11),       -- Q20-Q21 -> Unit 11
(22, 12), (23, 12),       -- Q22-Q23 -> Unit 12
(24, 13), (25, 13), (26, 13), (27, 13), -- Q24-Q27 -> Unit 13
(28, 14), (29, 14),       -- Q28-Q29 -> Unit 14
(30, 15), (31, 15),       -- Q30-Q31 -> Unit 15
(32, 16), (33, 16),       -- Q32-Q33 -> Unit 16
(34, 17), (35, 17),       -- Q34-Q35 -> Unit 17
(36, 18), (37, 18);       -- Q36-Q37 -> Unit 18

-- ==================== QUESTION-EVALUATES (what concepts the question tests) ====================

INSERT INTO question_evaluates (question_id, concept_id) VALUES
(1, 2), (1, 13),     -- Q1 tests multiplication_division, distributive_property
(2, 3),               -- Q2 tests order_of_operations
(3, 6),               -- Q3 tests fraction_simplification
(4, 5),               -- Q4 tests fraction_operations
(5, 8),               -- Q5 tests percentage
(6, 9),               -- Q6 tests ratio_proportion
(7, 12),              -- Q7 tests like_terms
(8, 13),              -- Q8 tests distributive_property
(9, 14),              -- Q9 tests linear_equation_solving
(10, 14), (10, 5),   -- Q10 tests linear_equation_solving, fraction_operations
(11, 15),             -- Q11 tests linear_inequality
(12, 29),             -- Q12 tests quadratic_inequality
(13, 17),             -- Q13 tests slope
(14, 18),             -- Q14 tests linear_function
(15, 22),             -- Q15 tests polynomial_multiplication
(16, 23),             -- Q16 tests multiplication_formulas
(17, 25),             -- Q17 tests factoring_quadratic
(18, 23),             -- Q18 tests multiplication_formulas (difference of squares)
(19, 26),             -- Q19 tests completing_the_square
(20, 28),             -- Q20 tests quadratic_equation_solving
(21, 27), (21, 28),  -- Q21 tests quadratic_formula, quadratic_equation_solving
(22, 31),             -- Q22 tests vertex_form
(23, 31), (23, 26),  -- Q23 tests vertex_form, completing_the_square
(24, 35),             -- Q24 tests radian_measure
(25, 36),             -- Q25 tests trigonometric_ratios
(26, 37), (26, 39),  -- Q26 tests trigonometric_functions, trig_equations
(27, 38),             -- Q27 tests trig_identities
(28, 40),             -- Q28 tests sequence_arithmetic
(29, 42),             -- Q29 tests series_sum
(30, 45),             -- Q30 tests derivative_rules
(31, 46),             -- Q31 tests derivative_applications
(32, 48),             -- Q32 tests integral_rules
(33, 47),             -- Q33 tests integral_definition
(34, 51),             -- Q34 tests vector_dot_product
(35, 51),             -- Q35 tests vector_dot_product (with angle)
(36, 52),             -- Q36 tests circle_equation
(37, 52);             -- Q37 tests circle_equation

-- ==================== QUESTION-REQUIRES (prerequisite concepts needed to solve) ====================

INSERT INTO question_requires (question_id, concept_id) VALUES
(1, 2),               -- Q1 requires multiplication_division
(2, 1), (2, 3),      -- Q2 requires addition_subtraction, order_of_operations
(3, 4), (3, 5),      -- Q3 requires fraction_basics, fraction_operations
(4, 4), (4, 5),      -- Q4 requires fraction_basics, fraction_operations
(5, 7), (5, 2),      -- Q5 requires decimal_operations, multiplication_division
(6, 9), (6, 5),      -- Q6 requires ratio_proportion, fraction_operations
(7, 11), (7, 12),    -- Q7 requires variable_expression, like_terms
(8, 13), (8, 12),    -- Q8 requires distributive_property, like_terms
(9, 14),              -- Q9 requires linear_equation_solving
(10, 14), (10, 5),   -- Q10 requires linear_equation_solving, fraction_operations
(11, 14), (11, 15),  -- Q11 requires linear_equation_solving, linear_inequality
(12, 25), (12, 26), (12, 29), -- Q12 requires factoring_quadratic, completing_the_square, quadratic_inequality
(13, 16), (13, 17),  -- Q13 requires coordinate_plane, slope
(14, 17), (14, 18),  -- Q14 requires slope, linear_function
(15, 22), (15, 13),  -- Q15 requires polynomial_multiplication, distributive_property
(16, 23), (16, 22),  -- Q16 requires multiplication_formulas, polynomial_multiplication
(17, 25), (17, 23),  -- Q17 requires factoring_quadratic, multiplication_formulas
(18, 23),             -- Q18 requires multiplication_formulas
(19, 26), (19, 25),  -- Q19 requires completing_the_square, factoring_quadratic
(20, 25), (20, 28),  -- Q20 requires factoring_quadratic, quadratic_equation_solving
(21, 27), (21, 28),  -- Q21 requires quadratic_formula, quadratic_equation_solving
(22, 26), (22, 31),  -- Q22 requires completing_the_square, vertex_form
(23, 26), (23, 30),  -- Q23 requires completing_the_square, quadratic_function
(24, 34), (24, 35),  -- Q24 requires angle_basics, radian_measure
(25, 36),             -- Q25 requires trigonometric_ratios
(26, 35), (26, 37),  -- Q26 requires radian_measure, trigonometric_functions
(27, 36), (27, 38),  -- Q27 requires trigonometric_ratios, trig_identities
(28, 40), (28, 11),  -- Q28 requires sequence_arithmetic, variable_expression
(29, 40), (29, 42),  -- Q29 requires sequence_arithmetic, series_sum
(30, 45), (30, 22),  -- Q30 requires derivative_rules, polynomial_multiplication
(31, 45), (31, 46),  -- Q31 requires derivative_rules, derivative_applications
(32, 48), (32, 47),  -- Q32 requires integral_rules, integral_definition
(33, 47), (33, 48),  -- Q33 requires integral_definition, integral_rules
(34, 51), (34, 50),  -- Q34 requires vector_dot_product, vector_operations
(35, 51), (35, 35),  -- Q35 requires vector_dot_product, radian_measure
(36, 26), (36, 52), (36, 53), -- Q36 requires completing_the_square, circle_equation, distance_formula
(37, 52), (37, 16);  -- Q37 requires circle_equation, coordinate_plane

-- SunMath Seed Data: Units
-- 18 units spanning elementary (grades 3-6), middle school (grades 7-9), high school (grades 10-12)

INSERT INTO units (id, name, description, grade_level) VALUES
-- Elementary (grades 3-6)
(1, 'Basic Arithmetic Operations', 'Addition, subtraction, multiplication, division, and order of operations', 3),
(2, 'Fractions', 'Understanding, comparing, and operating with fractions', 4),
(3, 'Decimals and Percentages', 'Decimal arithmetic, percentage calculations, and conversions', 5),
(4, 'Ratios and Proportions', 'Ratio concepts, proportional reasoning, and cross-multiplication', 6),

-- Middle School (grades 7-9)
(5, 'Algebraic Expressions', 'Variables, like terms, distributive property, and simplification', 7),
(6, 'Linear Equations', 'Solving one-variable and two-variable linear equations', 7),
(7, 'Inequalities', 'Linear and quadratic inequalities with solution sets', 8),
(8, 'Functions and Graphs', 'Function concepts, coordinate plane, slope, and linear functions', 8),
(9, 'Polynomial Operations', 'Polynomial addition, multiplication, and special product formulas', 8),
(10, 'Factoring', 'Common factor extraction, quadratic factoring, and completing the square', 9),
(11, 'Quadratic Equations', 'Solving quadratic equations by factoring, formula, and completing the square', 9),

-- High School (grades 10-12)
(12, 'Quadratic Functions', 'Quadratic function analysis, vertex form, and graph transformations', 10),
(13, 'Trigonometry', 'Angle measurement, trigonometric ratios, identities, and equations', 10),
(14, 'Sequences and Series', 'Arithmetic and geometric sequences, summation formulas', 10),
(15, 'Calculus - Limits and Derivatives', 'Limits, derivative definition, rules, and applications', 11),
(16, 'Calculus - Integration', 'Definite and indefinite integrals, integration rules', 11),
(17, 'Vectors', 'Vector notation, operations, dot product, and angle between vectors', 11),
(18, 'Circle Equations', 'Standard and general forms of circle equations, center and radius', 10);

-- Reset sequence to avoid conflicts with future inserts
SELECT setval('units_id_seq', (SELECT MAX(id) FROM units));

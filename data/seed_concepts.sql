-- SunMath Seed Data: Concepts + Edges
-- 50 concepts, ~70 prerequisites, ~25 lateral associations, unit-concept mappings

-- ==================== CONCEPTS (50) ====================

INSERT INTO concepts (id, name, description, category) VALUES
-- Elementary concepts (1-10)
(1, 'addition_subtraction', 'Basic addition and subtraction of integers', 'arithmetic'),
(2, 'multiplication_division', 'Basic multiplication and division of integers', 'arithmetic'),
(3, 'order_of_operations', 'PEMDAS/BODMAS rules for evaluating expressions', 'arithmetic'),
(4, 'fraction_basics', 'Understanding fractions as parts of a whole, comparing fractions', 'fractions'),
(5, 'fraction_operations', 'Adding, subtracting, multiplying, and dividing fractions', 'fractions'),
(6, 'fraction_simplification', 'Reducing fractions to lowest terms using GCD', 'fractions'),
(7, 'decimal_operations', 'Arithmetic operations with decimal numbers', 'decimals'),
(8, 'percentage', 'Percentage calculations, conversions between fractions/decimals/percents', 'decimals'),
(9, 'ratio_proportion', 'Ratio notation, proportional reasoning, cross-multiplication', 'ratios'),
(10, 'exponent_basics', 'Integer exponents, power rules, and notation', 'arithmetic'),

-- Algebra concepts (11-20)
(11, 'variable_expression', 'Using variables in algebraic expressions', 'algebra'),
(12, 'like_terms', 'Identifying and combining like terms', 'algebra'),
(13, 'distributive_property', 'Applying a(b + c) = ab + ac', 'algebra'),
(14, 'linear_equation_solving', 'Solving one-variable linear equations', 'algebra'),
(15, 'linear_inequality', 'Solving and graphing linear inequalities', 'algebra'),
(16, 'coordinate_plane', 'Plotting points and understanding the x-y coordinate system', 'algebra'),
(17, 'slope', 'Rate of change, rise over run, slope formula', 'algebra'),
(18, 'linear_function', 'y = mx + b, linear function graphs and properties', 'functions'),
(19, 'function_concept', 'Domain, range, function notation, input-output relationship', 'functions'),
(20, 'absolute_value', 'Absolute value definition and equations', 'algebra'),

-- Polynomial concepts (21-27)
(21, 'polynomial_addition', 'Adding and subtracting polynomial expressions', 'polynomials'),
(22, 'polynomial_multiplication', 'Multiplying polynomials using distribution and FOIL', 'polynomials'),
(23, 'multiplication_formulas', 'Special products: (a+b)^2, (a-b)^2, (a+b)(a-b), (a+b)^3', 'polynomials'),
(24, 'factoring_common', 'Extracting greatest common factor from expressions', 'polynomials'),
(25, 'factoring_quadratic', 'Factoring quadratic trinomials ax^2 + bx + c', 'polynomials'),
(26, 'completing_the_square', 'Rewriting quadratic expressions as (x+a)^2 + b', 'polynomials'),
(27, 'quadratic_formula', 'x = (-b +/- sqrt(b^2-4ac)) / 2a', 'polynomials'),

-- Quadratic/function concepts (28-33)
(28, 'quadratic_equation_solving', 'Solving ax^2 + bx + c = 0 by various methods', 'equations'),
(29, 'quadratic_inequality', 'Solving quadratic inequalities using sign analysis', 'equations'),
(30, 'quadratic_function', 'y = ax^2 + bx + c, parabola properties', 'functions'),
(31, 'vertex_form', 'Converting to y = a(x-h)^2 + k, finding vertex', 'functions'),
(32, 'graph_transformation', 'Translations, reflections, stretches of function graphs', 'functions'),
(33, 'discriminant', 'b^2 - 4ac and its role in determining roots', 'equations'),

-- Trigonometry concepts (34-39)
(34, 'angle_basics', 'Angle measurement in degrees, types of angles', 'trigonometry'),
(35, 'radian_measure', 'Radian definition, degree-radian conversion, arc length', 'trigonometry'),
(36, 'trigonometric_ratios', 'sin, cos, tan as ratios in right triangles', 'trigonometry'),
(37, 'trigonometric_functions', 'sin(x), cos(x), tan(x) as functions of real numbers', 'trigonometry'),
(38, 'trig_identities', 'Pythagorean identities, double angle, sum formulas', 'trigonometry'),
(39, 'trig_equations', 'Solving equations involving trigonometric functions', 'trigonometry'),

-- Sequences and series (40-42)
(40, 'sequence_arithmetic', 'Arithmetic sequences: a_n = a_1 + (n-1)d', 'sequences'),
(41, 'sequence_geometric', 'Geometric sequences: a_n = a_1 * r^(n-1)', 'sequences'),
(42, 'series_sum', 'Summation of arithmetic and geometric series', 'sequences'),

-- Calculus concepts (43-47)
(43, 'limit_concept', 'Intuitive and formal definition of limits', 'calculus'),
(44, 'derivative_definition', 'Derivative as limit of difference quotient', 'calculus'),
(45, 'derivative_rules', 'Power rule, product rule, chain rule', 'calculus'),
(46, 'derivative_applications', 'Critical points, optimization, related rates', 'calculus'),
(47, 'integral_definition', 'Definite and indefinite integrals, antiderivatives', 'calculus'),
(48, 'integral_rules', 'Power rule for integrals, substitution, FTC', 'calculus'),

-- Vector and geometry concepts (49-50)
(49, 'vector_basics', 'Vector notation, magnitude, direction, components', 'vectors'),
(50, 'vector_operations', 'Vector addition, scalar multiplication, subtraction', 'vectors'),
(51, 'vector_dot_product', 'Dot product formula, angle between vectors', 'vectors'),
(52, 'circle_equation', 'Standard form (x-h)^2 + (y-k)^2 = r^2 and general form', 'geometry'),
(53, 'distance_formula', 'Distance between two points in coordinate plane', 'geometry');

SELECT setval('concepts_id_seq', (SELECT MAX(id) FROM concepts));

-- ==================== UNIT-CONCEPT MAPPINGS ====================

INSERT INTO unit_concepts (unit_id, concept_id) VALUES
-- Unit 1: Basic Arithmetic Operations
(1, 1), (1, 2), (1, 3), (1, 10),
-- Unit 2: Fractions
(2, 4), (2, 5), (2, 6),
-- Unit 3: Decimals and Percentages
(3, 7), (3, 8),
-- Unit 4: Ratios and Proportions
(4, 9),
-- Unit 5: Algebraic Expressions
(5, 11), (5, 12), (5, 13),
-- Unit 6: Linear Equations
(6, 14), (6, 20),
-- Unit 7: Inequalities
(7, 15), (7, 29),
-- Unit 8: Functions and Graphs
(8, 16), (8, 17), (8, 18), (8, 19),
-- Unit 9: Polynomial Operations
(9, 21), (9, 22), (9, 23),
-- Unit 10: Factoring
(10, 24), (10, 25), (10, 26),
-- Unit 11: Quadratic Equations
(11, 27), (11, 28), (11, 33),
-- Unit 12: Quadratic Functions
(12, 30), (12, 31), (12, 32),
-- Unit 13: Trigonometry
(13, 34), (13, 35), (13, 36), (13, 37), (13, 38), (13, 39),
-- Unit 14: Sequences and Series
(14, 40), (14, 41), (14, 42),
-- Unit 15: Calculus - Limits and Derivatives
(15, 43), (15, 44), (15, 45), (15, 46),
-- Unit 16: Calculus - Integration
(16, 47), (16, 48),
-- Unit 17: Vectors
(17, 49), (17, 50), (17, 51),
-- Unit 18: Circle Equations
(18, 52), (18, 53);

-- ==================== CONCEPT PREREQUISITES (71) ====================
-- Format: (concept_id, prerequisite_concept_id)
-- Read as: concept_id REQUIRES prerequisite_concept_id

INSERT INTO concept_prerequisites (concept_id, prerequisite_concept_id) VALUES
-- Elementary chains
(3, 1),   -- order_of_operations requires addition_subtraction
(3, 2),   -- order_of_operations requires multiplication_division
(4, 2),   -- fraction_basics requires multiplication_division
(5, 4),   -- fraction_operations requires fraction_basics
(6, 5),   -- fraction_simplification requires fraction_operations
(7, 4),   -- decimal_operations requires fraction_basics
(8, 7),   -- percentage requires decimal_operations
(9, 5),   -- ratio_proportion requires fraction_operations
(10, 2),  -- exponent_basics requires multiplication_division

-- Algebra chains
(11, 1),  -- variable_expression requires addition_subtraction
(11, 2),  -- variable_expression requires multiplication_division
(12, 11), -- like_terms requires variable_expression
(13, 2),  -- distributive_property requires multiplication_division
(13, 11), -- distributive_property requires variable_expression
(14, 12), -- linear_equation_solving requires like_terms
(14, 13), -- linear_equation_solving requires distributive_property
(15, 14), -- linear_inequality requires linear_equation_solving
(16, 1),  -- coordinate_plane requires addition_subtraction
(17, 16), -- slope requires coordinate_plane
(18, 17), -- linear_function requires slope
(18, 19), -- linear_function requires function_concept
(19, 11), -- function_concept requires variable_expression
(20, 14), -- absolute_value requires linear_equation_solving

-- Polynomial chains
(21, 11), -- polynomial_addition requires variable_expression
(21, 12), -- polynomial_addition requires like_terms
(22, 13), -- polynomial_multiplication requires distributive_property
(22, 21), -- polynomial_multiplication requires polynomial_addition
(23, 22), -- multiplication_formulas requires polynomial_multiplication
(24, 23), -- factoring_common requires multiplication_formulas
(25, 23), -- factoring_quadratic requires multiplication_formulas
(26, 25), -- completing_the_square requires factoring_quadratic  *** KEY CHAIN ***
(27, 26), -- quadratic_formula requires completing_the_square

-- Quadratic chains
(28, 25), -- quadratic_equation_solving requires factoring_quadratic
(28, 27), -- quadratic_equation_solving requires quadratic_formula
(28, 26), -- quadratic_equation_solving requires completing_the_square
(29, 28), -- quadratic_inequality requires quadratic_equation_solving  *** STUDENT A FAILS ***
(29, 15), -- quadratic_inequality requires linear_inequality
(30, 19), -- quadratic_function requires function_concept
(30, 28), -- quadratic_function requires quadratic_equation_solving
(31, 26), -- vertex_form requires completing_the_square  *** STUDENT A FAILS ***
(31, 30), -- vertex_form requires quadratic_function
(32, 18), -- graph_transformation requires linear_function
(32, 30), -- graph_transformation requires quadratic_function
(33, 27), -- discriminant requires quadratic_formula

-- Trigonometry chains
(35, 34), -- radian_measure requires angle_basics  *** KEY for STUDENT B ***
(35, 5),  -- radian_measure requires fraction_operations
(36, 34), -- trigonometric_ratios requires angle_basics
(37, 35), -- trigonometric_functions requires radian_measure  *** STUDENT B FAILS ***
(37, 36), -- trigonometric_functions requires trigonometric_ratios
(38, 37), -- trig_identities requires trigonometric_functions
(39, 38), -- trig_equations requires trig_identities
(39, 14), -- trig_equations requires linear_equation_solving

-- Sequence chains
(40, 14), -- sequence_arithmetic requires linear_equation_solving
(40, 11), -- sequence_arithmetic requires variable_expression
(41, 40), -- sequence_geometric requires sequence_arithmetic
(41, 10), -- sequence_geometric requires exponent_basics
(42, 40), -- series_sum requires sequence_arithmetic
(42, 41), -- series_sum requires sequence_geometric

-- Calculus chains
(43, 19), -- limit_concept requires function_concept
(43, 22), -- limit_concept requires polynomial_multiplication
(44, 43), -- derivative_definition requires limit_concept
(45, 44), -- derivative_rules requires derivative_definition
(45, 22), -- derivative_rules requires polynomial_multiplication
(46, 45), -- derivative_applications requires derivative_rules
(46, 30), -- derivative_applications requires quadratic_function
(47, 44), -- integral_definition requires derivative_definition
(48, 47), -- integral_rules requires integral_definition
(48, 45), -- integral_rules requires derivative_rules

-- Vector chains
(49, 16), -- vector_basics requires coordinate_plane
(49, 11), -- vector_basics requires variable_expression
(50, 49), -- vector_operations requires vector_basics
(51, 50), -- vector_dot_product requires vector_operations
(51, 35), -- vector_dot_product requires radian_measure  *** STUDENT B FAILS ***
(51, 36), -- vector_dot_product requires trigonometric_ratios

-- Circle equation chains
(52, 26), -- circle_equation requires completing_the_square  *** STUDENT A FAILS ***
(52, 16), -- circle_equation requires coordinate_plane
(52, 53), -- circle_equation requires distance_formula
(53, 16), -- distance_formula requires coordinate_plane
(53, 22); -- distance_formula requires polynomial_multiplication

-- ==================== LATERAL ASSOCIATIONS (25) ====================
-- Cross-unit concept relationships for enriched graph traversal

INSERT INTO concept_relations (concept_id, related_concept_id, relation_type) VALUES
(6, 24, 'analogous_technique'),       -- fraction_simplification <-> factoring_common
(14, 28, 'generalization'),           -- linear_equation <-> quadratic_equation
(15, 29, 'generalization'),           -- linear_inequality <-> quadratic_inequality
(18, 30, 'generalization'),           -- linear_function <-> quadratic_function
(22, 25, 'inverse_operation'),        -- polynomial_multiplication <-> factoring_quadratic
(44, 47, 'inverse_operation'),        -- derivative <-> integral
(45, 48, 'inverse_operation'),        -- derivative_rules <-> integral_rules
(36, 51, 'application'),             -- trigonometric_ratios <-> vector_dot_product
(26, 52, 'application'),             -- completing_the_square <-> circle_equation
(26, 31, 'application'),             -- completing_the_square <-> vertex_form
(17, 44, 'generalization'),           -- slope <-> derivative_definition
(42, 47, 'continuous_analog'),        -- series_sum <-> integral_definition
(40, 18, 'discrete_analog'),          -- sequence_arithmetic <-> linear_function
(41, 9, 'application'),              -- sequence_geometric <-> ratio_proportion
(16, 49, 'shared_foundation'),        -- coordinate_plane <-> vector_basics
(34, 36, 'foundation'),              -- angle_basics <-> trigonometric_ratios
(8, 9, 'equivalent_representation'),  -- percentage <-> ratio_proportion
(32, 39, 'shared_technique'),         -- graph_transformation <-> trig_equations
(53, 50, 'related_concept'),          -- distance_formula <-> vector_operations
(23, 38, 'pattern_similarity'),       -- multiplication_formulas <-> trig_identities
(27, 26, 'derived_from'),            -- quadratic_formula <-> completing_the_square
(35, 52, 'shared_foundation'),        -- radian_measure <-> circle_equation
(24, 25, 'generalization'),           -- factoring_common <-> factoring_quadratic
(46, 32, 'application'),             -- derivative_applications <-> graph_transformation
(43, 42, 'foundation');              -- limit_concept <-> series_sum

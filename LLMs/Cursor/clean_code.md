Guidelines for AI Assistance in Writing Clean Python Code

This guide provides instructions for implementing an AI system to assist developers in writing clean and maintainable Python code. Drawing from Clean Code in Python by Mariano Anaya, these principles focus on readability, consistency, and maintainability.

1. Formatting and Style Compliance
	•	Ensure the code adheres to PEP-8 standards:
	•	Enforce consistent indentation (4 spaces).
	•	Limit line length to 79 characters.
	•	Use snake_case for variable and function names.
	•	Use PascalCase for class names.
	•	Suggest automatic formatting tools like black for consistency.
	•	Ensure spaces around operators and after commas for readability.

AI Action:
	•	Check code against PEP-8 standards and suggest corrections.
	•	Provide an automated option to reformat the code.

2. Commenting and Documentation
	•	Focus on why the code exists rather than what it does:
	•	For functions, explain the purpose and any non-obvious logic.
	•	Avoid stating the obvious, like “this adds two numbers”.
	•	Use docstrings for:
	•	Modules, classes, and functions.
	•	Describing input types, outputs, and exceptions raised.

AI Action:
	•	Automatically generate docstrings using type hints and context from the code.
	•	Highlight missing or outdated comments and docstrings.

3. Type Hints and Annotations
	•	Use Python’s typing module for type hints:
	•	Define inputs and return types explicitly.
	•	Use generic types like List, Dict, and Optional for clarity.

Example:

def process_data(data: List[Dict[str, Any]]) -> List[float]:
    """Processes raw data into numerical results."""
    ...

AI Action:
	•	Suggest adding or refining type hints where missing or ambiguous.

4. Refactoring and Simplification
	•	Follow DRY (Don’t Repeat Yourself) and KISS (Keep It Simple, Stupid) principles:
	•	Identify and consolidate repeated logic.
	•	Break down complex functions into smaller, single-purpose functions.
	•	Highlight functions with too many arguments or excessive complexity.

AI Action:
	•	Suggest refactoring opportunities and provide optimized code snippets.

5. Error Handling
	•	Use try and except judiciously:
	•	Keep try blocks minimal to reduce the risk of swallowing unintended exceptions.
	•	Provide informative error messages and avoid bare except.

Example:

try:
    result = process_data(data)
except ValueError as e:
    logger.error(f"Data processing failed: {e}")
    raise

AI Action:
	•	Identify unhandled exceptions and suggest robust error-handling patterns.

6. Testing and Code Quality
	•	Write unit tests for all critical functionality.
	•	Follow Arrange-Act-Assert structure in tests.
	•	Use mock objects for dependency-heavy code.

AI Action:
	•	Generate test stubs based on function signatures.
	•	Suggest missing edge cases in tests.

7. Code Design Principles
	•	Apply SOLID Principles:
	•	Single Responsibility: Ensure classes and functions serve one purpose.
	•	Open/Closed: Make entities extensible without modifying existing code.
	•	Encourage separation of concerns and modular design.

AI Action:
	•	Analyze classes and methods for adherence to SOLID principles.
	•	Suggest modularization or separation of tightly coupled logic.

8. Advanced Python Features
	•	Recommend using context managers for resource management.
	•	Suggest decorators for reusable functionality like logging or validation.
	•	Identify opportunities to use generators for lazy evaluation.

AI Action:
	•	Propose implementing advanced features where they improve code clarity or efficiency.

9. Performance and Efficiency
	•	Highlight inefficient loops or redundant calculations.
	•	Recommend list comprehensions and built-in functions for concise, efficient operations.

Example:

# Before
result = []
for i in range(10):
    if i % 2 == 0:
        result.append(i)

# After
result = [i for i in range(10) if i % 2 == 0]

AI Action:
	•	Detect and replace inefficient patterns with Pythonic alternatives.

10. Automation and Tooling
	•	Suggest integrating tools for:
	•	Static analysis (pylint, flake8).
	•	Type checking (mypy).
	•	Testing (pytest).

AI Action:
	•	Provide seamless integration with these tools and highlight issues during coding.

This framework will help the AI guide developers in maintaining clean, efficient, and Pythonic code. It complements a developer’s intuition with automated, actionable insights to improve overall code quality.
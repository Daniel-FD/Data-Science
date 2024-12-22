Below is a comprehensive guide intended for integration with AI-assisted Python development environments—such as using Claude 3.5 Sonnet within Cursor—to help produce clean, maintainable, and Pythonic code. Drawing on best practices from Clean Code in Python by Mariano Anaya (and expanded where necessary), these guidelines aim to ensure consistency, readability, and robustness in any Python codebase.

AI-Assisted Clean Code Guidelines for Python

1. Formatting and Style Compliance
	1.	Adhere to PEP 8 Standards
	•	Indent with 4 spaces.
	•	Limit line length to 79 characters for improved readability.
	•	Include spaces around operators (e.g., a + b, not a+b), after commas, and around keywords like if, for, and in.
	2.	Naming Conventions
	•	Use snake_case for variable and function names: process_data, user_count.
	•	Use PascalCase for classes: UserAccount, DataProcessor.
	•	Use uppercase with underscores for constants: MAX_RETRIES.
	3.	Automation Suggestions
	•	Recommend or automatically run code formatters like black or autopep8.
	•	Check style compliance using linters like flake8 or pylint.

AI Action
	•	Check against PEP 8 and suggest formatting fixes.
	•	Provide an automated option to reformat code directly.
	•	Highlight naming inconsistencies and suggest alternatives.

2. Commenting and Documentation
	1.	Explain the “Why” and “How”
	•	Comments should clarify the intent and logic rather than stating the obvious.
	•	For complex algorithms or unusual data flows, explain the reasoning behind decisions.
	2.	Docstrings
	•	Use docstrings (triple quotes) for modules, classes, and functions to describe purpose, parameters, return values, and exceptions.
	•	Keep them concise but informative, focusing on the developer’s or AI’s needs.
	3.	Comment Placement
	•	Use single-line comments for short, contextual notes.
	•	Employ multi-line comments or docstrings for longer explanations and insights.

AI Action
	•	Automatically generate docstrings based on function signatures and inferred context.
	•	Propose clarifying comments or docstrings where missing or outdated.
	•	Warn when comments simply restate code rather than explaining the logic or purpose.

3. Type Hints and Annotations
	1.	Explicit Type Hints
	•	Use Python’s typing module for clarity on data types, such as List[str], Dict[str, Any], Optional[int], etc.
	•	Consistently annotate function parameters and return types.
	2.	Complex Structures
	•	For large or complex data structures, define custom TypedDict or classes to improve clarity and introspection.
	3.	Generics and Protocols
	•	When appropriate, use Generic, Protocol, or advanced typing features to increase code safety and readability.

AI Action
	•	Suggest adding or refining type hints when missing.
	•	Identify ambiguous variables where type hints can provide clarity.
	•	Insert advanced typing features as needed to improve code maintainability.

4. Refactoring and Simplification
	1.	DRY (Don’t Repeat Yourself)
	•	Identify duplicate logic and propose consolidated functions or utilities.
	2.	KISS (Keep It Simple, Stupid)
	•	Limit the size and complexity of functions.
	•	Encourage single-purpose functions and classes.
	3.	Complexity Warnings
	•	Flag methods or classes that exceed a certain cyclomatic complexity threshold (e.g., using tools like radon).
	•	Suggest splitting them into smaller, more manageable parts.

AI Action
	•	Detect repeated code blocks and suggest refactoring them into reusable functions or classes.
	•	Provide optimized code snippets that replace overly complex logic.
	•	Propose splitting large classes or functions into more modular units.

5. Error Handling and Logging
	1.	Explicit try/except Blocks
	•	Keep try blocks small to avoid catching unrelated errors.
	•	Use specific exception types (e.g., ValueError, KeyError) rather than bare except.
	2.	Meaningful Error Messages
	•	When catching an exception, log or re-raise with context that explains what went wrong.
	•	Avoid silent pass statements that hide errors.
	3.	Logging Best Practices
	•	Use Python’s built-in logging module instead of print statements for production systems.
	•	Configure loggers with appropriate levels (DEBUG, INFO, WARNING, ERROR, CRITICAL).

AI Action
	•	Identify unhandled exceptions and suggest robust error-handling patterns.
	•	Advise adding contextual logging messages for troubleshooting.
	•	Flag unused or overly broad exception clauses for refinement.

6. Testing and Code Quality
	1.	Unit Testing
	•	Write unit tests covering core functionality and edge cases.
	•	Follow Arrange-Act-Assert for consistent structure.
	•	Use mocking libraries like unittest.mock or pytest fixtures for external dependencies.
	2.	Coverage Analysis
	•	Aim for high coverage but be mindful that coverage alone does not guarantee quality.
	•	Identify critical paths (like error handling and boundary conditions) and ensure they are thoroughly tested.
	3.	Automated Testing Tools
	•	Integrate pytest for simpler test syntax.
	•	Automate tests via continuous integration (CI) pipelines.

AI Action
	•	Generate test stubs based on function signatures and docstrings.
	•	Suggest additional test cases for uncovered lines or complex logic paths.
	•	Provide guidance on mocking or test fixture usage.

7. Code Design Principles
	1.	SOLID Principles
	•	Single Responsibility: Each function or class handles one concern.
	•	Open/Closed: Make entities extendable without modifying existing code.
	•	Liskov Substitution: Subclasses should be interchangeable with their base class.
	•	Interface Segregation: Avoid forcing classes to implement unnecessary methods.
	•	Dependency Inversion: Rely on abstractions, not concrete implementations.
	2.	Separation of Concerns
	•	Encourage layering: separate data access, business logic, and UI/CLI code.
	•	Modularize functionality to keep code organized and testable.
	3.	Design Patterns
	•	Suggest relevant patterns (e.g., Strategy, Observer) where they can improve maintainability.

AI Action
	•	Analyze classes and functions for SOLID compliance.
	•	Identify tight coupling and recommend design improvements.
	•	Suggest design patterns when they reduce complexity or repetition.

8. Advanced Python Features
	1.	Context Managers
	•	Recommend with statements for resource management (files, network connections).
	•	Propose custom context managers to handle setup/teardown logic.
	2.	Decorators
	•	Suggest reusable decorators for functionality like caching, logging, or authorization.
	•	Encourage using built-in decorators (e.g., functools.lru_cache) for performance gains.
	3.	Generators and Iterators
	•	Highlight places where generator functions or comprehensions can simplify data processing and reduce memory usage.

AI Action
	•	Propose transforming repetitive setup/teardown code into context managers.
	•	Identify repeated logic that can be refactored into decorators.
	•	Replace large in-memory lists with generator expressions if feasible.

9. Performance and Efficiency
	1.	Time Complexity Analysis
	•	Identify nested loops or other O(n^2) patterns that might become bottlenecks.
	•	Recommend data structure changes (e.g., using set instead of list for membership checks).
	2.	Pythonic Patterns
	•	Suggest list comprehensions, built-in functions (map, filter), or vectorized operations with libraries like NumPy.
	•	Encourage zip, enumerate, and other idiomatic constructs for clean iteration.
	3.	Memory Optimization
	•	Replace large in-memory structures with streaming or chunking techniques.
	•	Avoid unnecessary copies of large datasets.

AI Action
	•	Spot potential bottlenecks by analyzing function complexity.
	•	Suggest Pythonic and optimized patterns to replace verbose loops.
	•	Flag memory-heavy operations and propose alternatives.

10. Automation, Tooling, and Environment
	1.	Static Analysis
	•	Integrate tools such as pylint, flake8, or bandit to catch common security issues and style violations early.
	2.	Type Checking
	•	Use mypy to enforce type hints at a deeper level.
	•	Encourage running mypy as part of a CI pipeline.
	3.	Version Control and Packaging
	•	Encourage structured repositories, with setup.py or pyproject.toml for packaging.
	•	Propose Git workflows (e.g., Gitflow, trunk-based) for organized collaboration.
	4.	Environment Management
	•	Recommend using virtual environments (venv, Poetry, Conda) to isolate dependencies.
	•	Provide guidance on pinning dependencies in requirements.txt or pyproject.toml.

AI Action
	•	Automatically invoke static analysis and highlight potential issues.
	•	Provide continuous suggestions for better environment or packaging setups.
	•	Recommend or automatically update dependency specifications as needed.

11. Concurrency and Parallelism (Optional)
	1.	Async/Await
	•	If the project deals with I/O-bound operations, recommend using asyncio for concurrency.
	•	Suggest asynchronous versions of time-consuming operations, such as file I/O or network requests.
	2.	Multiprocessing vs. Threading
	•	Identify CPU-bound tasks that could benefit from multiprocessing to bypass the GIL.
	•	For I/O-bound tasks, consider threads for simpler concurrency handling.
	3.	Synchronization and Race Conditions
	•	Propose thread-safe data structures (Queue, Lock, or Event).
	•	Provide warnings when shared state might lead to race conditions.

AI Action
	•	Detect I/O-intensive sections of code and propose async transformations.
	•	Highlight CPU-intensive loops for potential multiprocessing.
	•	Offer concurrency-safe patterns where data is shared among threads or processes.

How to Use These Guidelines With Claude 3.5 Sonnet in Cursor
	1.	Real-Time Suggestions
	•	As you type, the AI will analyze your code in the background. It will highlight style inconsistencies, untyped function parameters, and potential refactoring opportunities.
	2.	Auto-Refactoring
	•	On demand, Claude can apply transformations to optimize loops, add docstrings, or introduce type hints based on these guidelines.
	•	You can choose to accept, reject, or tweak these suggestions.
	3.	Comment Enhancement
	•	If your code lacks explanations, ask Claude to “Add clarifying comments” or “Generate docstrings.” It will reference function context and usage to produce meaningful documentation.
	4.	Testing Assistance
	•	You can request test stubs (e.g., “Generate unit tests for process_data() function”) and Claude will create a testing skeleton following recommended best practices.
	5.	Continuous Improvement
	•	Periodically, ask Claude to “Review code design” or “Check SOLID principles.” It will analyze classes and modules, suggesting advanced patterns or improvements.

By following these guidelines, you will produce cleaner, more maintainable Python code. The goal is to combine the best practices from Clean Code in Python with intelligent, context-aware assistance—delivering robust, well-documented, and high-performing solutions.
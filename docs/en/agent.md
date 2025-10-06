# Paradox Mod Localization Factory - Agent Development Regulations V1.0

## To All AI Agents Assisting in This Project's Development

Welcome to the **Paradox Mod Localization Factory**. This project is a Python tool that provides an efficient and reliable semi-automatic localization solution for Paradox games' Mods (such as Victoria 3, Stellaris, Hearts of Iron 4, etc.). To ensure the quality, maintainability, and consistency of the project code, all contributors (including you, AI) must strictly adhere to the following development regulations.

These regulations are best practices summarized from extensive practical experience and serve as the highest guiding principles for any code generation, refactoring, or bug fixing work you perform in this project.

## Chapter One: Architectural Principles

### Article 1: Strict Separation of Frontend and Backend
The core philosophy of this project is the complete separation of the **presentation layer (UI) and business logic (core engine)**.

- **UI Layer (ui/ directory)**: Responsible for and only responsible for building user interfaces and user interaction. It should be "dumb," its sole task being to collect user input and then call a single, high-level core function. The UI layer strictly prohibits containing any complex business logic or orchestrating multiple core operations.
- **Core Engine (core/ directory)**: Responsible for all actual work, including file parsing, AI translation, glossary management, file reconstruction, and localization processing. Core functions should be self-contained, high-level services.

### Article 2: Single Entry Point Principle (The "One Button, One Function" Rule)
For any core user operation (e.g., "Start Translation"), the click event of a UI button must only call one high-level function in the core engine (e.g., `initial_translate.start_translation(...)`).

"Procedural" orchestration where the UI calls `file_parser.parse()`, then `api_handler.translate()`, and then `file_builder.build()` is strictly prohibited. All workflow orchestration must be completed within the core engine.

### Article 3: Modularity and Code Reusability
- **New Feature, New Module**: Any new, independent functionality (e.g., "Glossary Management," "Parallel Processing") should be implemented in a brand new module file.
- **Extract General Tools**: Any functionality that might be reused by multiple modules (e.g., text cleaning, punctuation handling, logging) must be extracted into general utility modules (e.g., `utils/text_clean.py`, `utils/punctuation_handler.py`) to follow the **DRY (Don't Repeat Yourself)** principle.

## Chapter Two: CLI-Specific Laws

### Article 4: Command Line Interaction Mode
This project uses the Command Line Interface (CLI) as the primary user interaction method. All functions in the `ui/` directory used to create user interfaces should follow these principles:

- **Clear User Prompts**: All user interactions should have clear, friendly prompt messages.
- **Input Validation**: Strictly validate user input and provide meaningful error messages.
- **Progress Feedback**: For time-consuming operations, clear progress indicators must be provided.

### Article 5: State Management
All data that needs to be persisted between different operations (e.g., selected game, API configuration, translation progress) must be managed using configuration files or state variables. Reliance on temporary file paths is strictly prohibited.

## Chapter Three: Code Quality and Style Codex

### Article 6: Internationalization (i18n) First
All user-facing strings (including prompt messages, error messages, log messages) are strictly prohibited from being hardcoded in Python code.

All strings must be wrapped using the `utils.i18n._()` function, for example, `print(_("messages.translation_started"))`. The corresponding text content must be defined in `en_US.json` and `zh_CN.json` files under the `data/lang/` directory.

### Article 7: "Iceberg" Logging Philosophy
This project pursues the design philosophy of **"simple interface, detailed backend."**

- **User Interface**: Must remain simple and elegant, showing users only the final results and the most necessary status.
- **Backend Processing**: When performing any time-consuming or complex backend operations, detailed, meaningful progress information and prompts must be printed in the command line interface. This is crucial for debugging and understanding program status.

### Article 8: Dependency Management and Stability
- **Dependency Management**: Any new library dependencies must be added to the `requirements.txt` file.
- **Stability First**: Stability takes precedence over everything else. If an external dependency library proves unstable or difficult to integrate, it is permissible and encouraged to replace it with a simpler, internally implemented solution, as long as that solution meets the core needs of the project.

### Article 9: Comments and Documentation
- **Code Comments**: All core functions and complex logic must be accompanied by clear Docstrings or Chinese comments, explaining their functionality, parameters, and return values.
- **Self-Documenting Code**: Code should be self-documenting, but necessary comments can greatly assist future maintenance.

## Chapter Four: Paradox Games Specific Rules

### Article 10: File Format Handling Specification
This project specifically handles localization files for Paradox games and must strictly adhere to the following specifications:

- **YAML File Parsing**: Must correctly handle Paradox's unique YAML format (e.g., `key:0 "value"`), using the project's built-in `file_parser.py` for parsing.
- **Encoding Handling**: All file operations must use UTF-8 encoding to ensure correct display of Chinese characters.
- **File Structure Preservation**: When rebuilding files, the original file's indentation, comments, and complex key formats must be perfectly preserved.

### Article 11: Glossary System Specification
- **Terminology Consistency**: All translations must ensure consistency of game terminology through the glossary system.
- **Glossary Loading**: Must use `glossary_manager.py` to load the glossary file for the corresponding game.
- **Terminology Injection**: Relevant terminology must be injected into AI translation requests as high-priority instructions.

### Article 12: Multi-Language Support Specification
- **Language Configuration**: All supported languages must be defined in the `LANGUAGES` dictionary in `config.py`.
- **File Naming**: Output files must follow Paradox game naming conventions (e.g., `modname_l_chinese.yml`).
- **Folder Structure**: Must create the correct folder structure as required by the game.

## Chapter Five: Resource Management Rules

### Article 13: Memory Management
- **File Handles**: All file operations must use `with` statements to ensure files are properly closed.
- **Large File Handling**: For large localization files, a batch processing mechanism must be used.
- **Temporary Files**: Temporary files must be cleaned up promptly after use.

### Article 14: Error Handling
- **API Calls**: All API calls must include retry mechanisms and error handling.
- **File Operations**: File read/write operations must include exception handling.
- **User Feedback**: All errors must provide meaningful error messages to the user.

---

**Paradox Mod Localization Factory Development Team**  
**Version 1.0.5 | Last Updated: 2025-01-12**
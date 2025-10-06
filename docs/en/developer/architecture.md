# 🏗️ Project Architecture

> System Design Description and Technical Architecture Details

## 🎯 Design Principles

### Modular Design
- **High Cohesion**: Each module has a single responsibility and complete functionality.
- **Low Coupling**: Dependencies between modules are clear and easy to maintain.
- **Extensibility**: Supports rapid integration of new functional modules.

### Layered Architecture
- **Presentation Layer**: User interface and interaction logic.
- **Business Layer**: Core business logic and workflows.
- **Data Layer**: Data storage and access interfaces.
- **Infrastructure Layer**: General tools and third-party services.

## 🏛️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer (UI Layer)          │
├─────────────────────────────────────────────────────────────┤
│  main.py                    # Main program entry point      │
│  └── Menu system, user interaction, process control         │
├─────────────────────────────────────────────────────────────┤
│                    Workflow Layer (Workflow Layer)          │
├─────────────────────────────────────────────────────────────┤
│  workflows/                                                 │
│  ├── initial_translate.py   # Initial translation workflow  │
│  └── ...                    # Other workflows               │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine Layer (Core Engine Layer)    │
├─────────────────────────────────────────────────────────────┤
│  core/                                                      │
│  ├── api_handler.py         # Unified API interface         │
│  ├── glossary_manager.py    # Glossary management system    │
│  ├── file_parser.py         # File parser                   │
│  ├── file_builder.py        # File builder                  │
│  ├── directory_handler.py   # Directory handler             │
│  ├── asset_handler.py       # Asset handler                 │
│  ├── proofreading_tracker.py # Proofreading tracker         │
│  ├── post_processing_manager.py # Post-processing manager   │
│  ├── parallel_processor.py  # Parallel processor            │
│  └── ...                    # Other core modules            │
├─────────────────────────────────────────────────────────────┤
│                    Utility Layer (Utility Layer)            │
├─────────────────────────────────────────────────────────────┤
│  utils/                                                     │
│  ├── i18n.py               # Internationalization support   │
│  ├── logger.py              # Logging system                │
│  ├── text_clean.py          # Text cleaning tool            │
│  ├── post_process_validator.py # Post-processing validator  │
│  ├── punctuation_handler.py # Punctuation handler           │
│  └── ...                    # Other utility modules         │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer (Data Layer)                  │
├─────────────────────────────────────────────────────────────┤
│  data/                                                      │
│  ├── lang/                  # Language files                │
│  │   ├── en_US.json        # English UI                     │
│  │   └── zh_CN.json        # Chinese UI                     │
│  ├── glossary/              # Glossary data                 │
│  │   ├── victoria3/        # V3 specific glossary           │
│  │   ├── stellaris/        # Stellaris specific glossary    │
│  │   └── ...               # Other game glossaries          │
│  └── config/                # Configuration files           │
├─────────────────────────────────────────────────────────────┤
│                    Configuration Layer                      │
├─────────────────────────────────────────────────────────────┤
│  config.py                  # Global configuration          │
│  ├── Game profile configuration                             │
│  ├── API configuration                                      │
│  ├── System parameters                                      │
│  └── Constant definitions                                   │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Module Details

### 1. Main Program Entry (`main.py`)
**Responsibility**: Program startup, user interaction, process coordination.
**Features**:
- Unified entry point.
- Modular menu system.
- Exception handling and error recovery.

### 2. Workflow Engine (`workflows/`)
**Responsibility**: Business process orchestration, task scheduling.
**Features**:
- Configurable workflow definitions.
- Supports conditional branching and looping.
- State management and progress tracking.

### 3. API Handler (`core/api_handler.py`)
**Responsibility**: Unified management of various AI translation APIs.
**Features**:
- Abstracted API interface.
- Supports multiple service providers.
- Error retry and fallback mechanisms.

### 4. Glossary Manager (`core/glossary_manager.py`)
**Responsibility**: Loading, managing, and applying game terminology glossaries.
**Features**:
- Supports multi-game glossaries.
- Fuzzy matching algorithms.
- Dynamic glossary updates.

### 5. File Parser (`core/file_parser.py`)
**Responsibility**: Parsing Paradox's unique file formats.
**Features**:
- Supports various .yml formats.
- Fault-tolerant parsing.
- Preserves original format.

### 6. Parallel Processor (`core/parallel_processor.py`)
**Responsibility**: Implements true multi-file parallel processing, solving file-level blocking issues, and significantly improving translation efficiency.
**Features**:
- **Core Components**: `FileTask` (file task data structure), `BatchTask` (batch task data structure), `ParallelProcessor` (main parallel processor class).
- **Key Features**: Decomposes file tasks into batch tasks, uses a thread pool to process all batches in parallel, intelligent result collection and file reconstruction, fault tolerance and error recovery mechanisms.
- **Performance Improvement**: Achieved significant speedup (e.g., 5.52x speedup in tests) compared to the old architecture, fully utilizing system resources.

### 7. Post-processing Manager (`core/post_processing_manager.py`)
**Responsibility**: Responsible for post-translation text format validation, report generation, and other post-processing tasks.
**Features**:
- Format validation and correction: Ensures translated text complies with Paradox game-specific format requirements.
- Report generation: Provides detailed post-processing reports to help users identify and resolve issues.
- Extensibility: Supports adding new post-processing plugins and rules.

### 8. Post-processing Validator (`utils/post_process_validator.py`)
**Responsibility**: Provides game-specific syntax rule validation to ensure translated text displays correctly in the game.
**Features**:
- Game-specific rules: Validates localization syntax for different Paradox games (e.g., Victoria 3, Stellaris, HOI4).
- Error detection: Identifies and reports format errors, missing placeholders, and other issues.
- Highly configurable: Supports custom validation rules and error levels.

### 9. Punctuation Handler (`utils/punctuation_handler.py`)
**Responsibility**: Handles multi-language punctuation conversion and cleaning, ensuring correct punctuation usage.
**Features**:
- Three-layer architecture: Includes core cleaning function, analysis function, and main interface function, with clear responsibilities.
- Intelligent mapping: Supports target language-specific punctuation mapping, improving accuracy.
- Eliminates redundant code: Follows the DRY principle, centralizing all cleaning logic.

## 🔄 Data Flow

### Translation Process
```
User Input → File Parsing → Glossary Injection → API Translation → Result Validation → File Reconstruction → Output
```

### Data Flow Direction
```
Source File → Parser → Text Extraction → Glossary Matching → AI Translation → Quality Check → File Generation
```

## 🎮 Game Profile System

### Configuration Structure
```python
GAME_PROFILES = {
    "victoria3": {
        "name": "Victoria 3",
        "localization_dir": "localization",
        "metadata_file": ".metadata/metadata.json",
        "supported_languages": [...],
        "file_patterns": [...]
    }
}
```

### Extensibility
- New games only require adding configuration.
- Supports custom file structures.
- Flexible language configuration.

## 🔌 Plugin System

### Hook Mechanism
- File parsing hooks.
- Post-translation processing hooks.
- Custom output format hooks.

### Extension Points
- New AI service providers.
- New file formats.
- New output formats.

## 📊 Performance Optimization

### Parallel Processing
This project, by introducing a new parallel processor architecture, achieves true multi-file parallel processing, significantly improving translation efficiency.
- **Multi-file Parallelism**: Processes multiple Mod files simultaneously, avoiding file-level blocking.
- **Multi-batch Parallelism**: Decomposes each file into multiple batches, processing all batches in parallel.
- **Intelligent Thread Pool**: Optimizes thread resource management, fully utilizing multi-core CPU capabilities.
- **Performance Data**: In tests, achieved a speedup ratio of up to 5.52x and an efficiency increase of 451.7% compared to the old architecture.

### Memory Management
- Stream processing of large files.
- Timely release of resources.
- Cache optimization.

### Network Optimization
- API call batching.
- Retry mechanism.
- Timeout control.

## 🔒 Security Considerations

### Data Security
- API key environment variables.
- Sensitive information not logged.
- Timely cleanup of temporary files.

### Error Handling
- Graceful degradation.
- Detailed error logs.
- User-friendly error messages.

## 🚀 Future Expansion

### Planned Features
- Web interface.
- Database support.
- Cloud deployment.
- Community glossary sharing.

### Technical Upgrades
- Asynchronous programming.
- Microservices architecture.
- Containerized deployment.

---

> 📚 **Related Documentation**:
> - [Parallel Processing Technology](developer/parallel-processing.md)
> - [Implementation Record](developer/parallel-processing-implementation.md)
> - [Glossary System](glossary/overview.md)
# 🏗️ Project Architecture

> System design explanation and technical architecture details

## 🎯 Design Principles

### Modular Design
- **High Cohesion**: Each module has a single responsibility and complete functionality
- **Low Coupling**: Clear dependency relationships between modules, easy to maintain
- **Extensible**: Support rapid integration of new functional modules

### Layered Architecture
- **Presentation Layer**: User interface and interaction logic
- **Business Layer**: Core business logic and workflows
- **Data Layer**: Data storage and access interfaces
- **Infrastructure Layer**: Common tools and third-party services

## 🏛️ System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface Layer (UI Layer)          │
├─────────────────────────────────────────────────────────────┤
│  main.py                    # Main program entry            │
│  └── Menu system, user interaction, process control        │
├─────────────────────────────────────────────────────────────┤
│                    Workflow Layer (Workflow Layer)          │
├─────────────────────────────────────────────────────────────┤
│  workflows/                                                 │
│  ├── initial_translate.py   # Initial translation workflow │
│  ├── generate_workshop_desc.py # Workshop description gen.  │
│  └── ...                    # Other workflows               │
├─────────────────────────────────────────────────────────────┤
│                    Core Engine Layer (Core Engine Layer)    │
├─────────────────────────────────────────────────────────────┤
│  core/                                                      │
│  ├── api_handler.py         # API unified interface        │
│  ├── glossary_manager.py    # Glossary management system   │
│  ├── file_parser.py         # File parser                  │
│  ├── file_builder.py        # File builder                 │
│  ├── directory_handler.py   # Directory handler            │
│  ├── asset_handler.py       # Asset handler                │
│  ├── proofreading_tracker.py # Proofreading tracker        │
│  ├── parallel_processor.py  # Parallel processor           │
│  └── ...                    # Other core modules           │
├─────────────────────────────────────────────────────────────┤
│                    Utility Layer (Utility Layer)            │
├─────────────────────────────────────────────────────────────┤
│  utils/                                                     │
│  ├── i18n.py               # Internationalization support │
│  ├── logger.py              # Logging system               │
│  ├── text_clean.py          # Text cleaning tools          │
│  └── ...                    # Other utility modules        │
├─────────────────────────────────────────────────────────────┤
│                    Data Layer (Data Layer)                  │
├─────────────────────────────────────────────────────────────┤
│  data/                                                      │
│  ├── lang/                  # Language files               │
│  │   ├── en_US.json        # English interface             │
│  │   └── zh_CN.json        # Chinese interface             │
│  ├── glossary/              # Glossary data                │
│  │   ├── victoria3/        # V3 specific glossary         │
│  │   ├── stellaris/        # Stellaris specific glossary   │
│  │   └── ...               # Other game glossaries        │
│  └── config/                # Configuration files          │
├─────────────────────────────────────────────────────────────┤
│                    Configuration Layer (Config Layer)       │
├─────────────────────────────────────────────────────────────┤
│  config.py                  # Global configuration          │
│  ├── Game profile configuration                            │
│  ├── API configuration                                     │
│  ├── System parameters                                     │
│  └── Constant definitions                                  │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Core Module Details

### 1. Main Program Entry (`main.py`)
**Responsibility**: Program startup, user interaction, process coordination
**Features**: 
- Unified entry point
- Modular menu system
- Exception handling and error recovery

### 2. Workflow Engine (`workflows/`)
**Responsibility**: Business process orchestration, task scheduling
**Features**:
- Configurable workflow definitions
- Support for conditional branches and loops
- State management and progress tracking

### 3. API Handler (`core/api_handler.py`)
**Responsibility**: Unified management of various AI translation APIs
**Features**:
- Abstracted API interfaces
- Support for multiple service providers
- Error retry and fallback mechanisms

### 4. Glossary Manager (`core/glossary_manager.py`)
**Responsibility**: Loading, management, and application of game terminology glossaries
**Features**:
- Support for multi-game glossaries
- Fuzzy matching algorithms
- Dynamic glossary updates

### 5. File Parser (`core/file_parser.py`)
**Responsibility**: Parsing PDS-specific file formats
**Features**:
- Support for various .yml formats
- Fault-tolerant parsing
- Preserve original formatting

### 6. Parallel Processor (`core/parallel_processor.py`)
**Responsibility**: Multi-file, multi-batch parallel processing
**Features**:
- Intelligent thread pool management
- Load balancing
- Resource optimization

## 🔄 Data Flow

### Translation Process
```
User Input → File Parsing → Glossary Injection → API Translation → Result Validation → File Reconstruction → Output
```

### Data Flow Direction
```
Source Files → Parser → Text Extraction → Glossary Matching → AI Translation → Quality Check → File Generation
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
- New games only need to add configuration files
- Support for custom file structures
- Flexible language configuration

## 🔌 Plugin System

### Hook Mechanism
- File parsing hooks
- Post-translation processing hooks
- Custom output format hooks

### Extension Points
- New AI service providers
- New file formats
- New output formats

## 📊 Performance Optimization

### Parallel Processing
- Multi-file parallelism
- Multi-batch parallelism
- Intelligent thread pools

### Memory Management
- Stream processing of large files
- Timely resource release
- Cache optimization

### Network Optimization
- API call batching
- Retry mechanisms
- Timeout control

## 🔒 Security Considerations

### Data Security
- API keys in environment variables
- Sensitive information not logged
- Temporary files cleaned up promptly

### Error Handling
- Graceful degradation
- Detailed error logging
- User-friendly error messages

## 🚀 Future Extensions

### Planned Features
- Web interface
- Database support
- Cloud deployment
- Community glossary sharing

### Technical Upgrades
- Asynchronous programming
- Microservice architecture
- Containerized deployment

---

> 📚 **Related Documentation**: 
> - [Parallel Processing Technology](docs/developer/parallel-processing.md)
> - [Implementation Notes](docs/developer/implementation-notes.md)
> - [Glossary System](docs/glossary/overview.md)

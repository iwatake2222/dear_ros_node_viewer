# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Dear RosNodeViewer is a Python GUI tool for visualizing ROS 2 node diagrams. It supports three input sources:
- CARET architecture YAML files (performance analysis framework)
- rosgraph.dot files (from rqt_graph)
- Live ROS 2 runtime graph analysis

## Build and Development Commands

### System Dependencies (Ubuntu/Debian)
```bash
sudo apt install -y graphviz graphviz-dev
```

### Installation
```bash
pip install -e .                    # Development install
pip install -r requirements.txt     # Install dev dependencies
```

### Running the Application
```bash
dear_ros_node_viewer <graph_file>   # Load YAML or DOT file
dear_ros_node_viewer ros            # Live ROS 2 analysis
dear_ros_node_viewer --save-only <file>  # Batch mode without GUI
```

## Testing

```bash
# Run all tests with coverage
pytest --doctest-modules -v --cov=./src/dear_ros_node_viewer

# Run single test file
pytest tests/test_caret2networkx.py -v

# Run single test class
pytest tests/test_caret2networkx.py::TestQuoteName -v

# Run single test method
pytest tests/test_caret2networkx.py::TestQuoteName::test_quote_name_basic -v

# Run tests with short traceback
pytest tests/ -v --tb=short
```

### Test Files
| File | Tests |
|------|-------|
| `test_caret2networkx.py` | CARET YAML parsing |
| `test_dot2networkx.py` | DOT file parsing |
| `test_graph_layout.py` | Node positioning (requires graphviz) |
| `test_graph_manager.py` | Graph loading/filtering (requires graphviz) |
| `test_logger_factory.py` | Logging configuration |
| `test_caret_extend_callback_group.py` | Callback group extraction |
| `test_caret_extend_path.py` | Path extraction |

Note: Some tests require `graphviz` to be installed and will be skipped if not available.

## Linting

```bash
# Flake8 - critical errors only
flake8 . --exclude=.venv --count --select=E9,F63,F7,F82 --show-source --statistics

# Flake8 - full check
flake8 . --exclude=.venv --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

# Pylint
pylint ./src/dear_ros_node_viewer --disable=E0401,W1203,C0301
```

## Architecture

The codebase follows MVVM-style architecture:

```
src/dear_ros_node_viewer/
├── dear_ros_node_viewer.py  # CLI entry point, settings management
├── graph_view.py            # GUI layer (Dear PyGui rendering)
├── graph_viewmodel.py       # State management, coordinates view/manager
├── graph_manager.py         # Graph loading, filtering, NetworkX operations
├── graph_layout.py          # Node positioning algorithms
├── caret2networkx.py        # CARET YAML → NetworkX converter
├── dot2networkx.py          # DOT file → NetworkX converter
├── ros2networkx.py          # Live ROS 2 → NetworkX (requires rclpy)
└── logger_factory.py        # Centralized logging configuration
```

### Data Flow
1. Input parsers (`caret2networkx`, `dot2networkx`, `ros2networkx`) convert sources to NetworkX MultiDiGraph
2. `graph_manager` loads graphs, applies filtering, manages graph state
3. `graph_layout` positions nodes based on group settings
4. `graph_viewmodel` coordinates between manager and view
5. `graph_view` renders using Dear PyGui

### Key Patterns
- ROS dependencies (rclpy, rqt_graph) are optional and wrapped in try-except
- Uses NetworkX MultiDiGraph to handle multiple edges between nodes
- Group-based layout with horizontal/vertical direction support
- Configuration via `setting.json` for GUI settings and node ignore patterns

## Code Style
- 2-space indentation (configured in `.pylintrc`)
- Max line length: 127 characters
- Google-style docstrings
- Apache License 2.0 header on all Python files

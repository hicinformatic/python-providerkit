## Project Structure

This template provides a standard structure for Python libraries. Adapt the module organization to your library's specific needs.

### General Structure

```
project_name/
├── project_name/          # Main package directory
│   ├── __init__.py        # Package exports
│   └── ...                # Your modules
├── tests/                 # Test suite
│   └── ...
├── docs/                  # Documentation (optional)
│   └── ...
├── dev.py                 # Development tooling script
├── pyproject.toml         # Project configuration
├── README.md              # Project documentation
└── ...
```

### Module Organization Principles

- **Single Responsibility**: Each module should have a clear, single purpose
- **Separation of Concerns**: Keep different concerns in separate modules
- **Clear Exports**: Use `__init__.py` to define public API
- **Logical Grouping**: Organize related functionality together

### Package Exports

Define the public API in the main package's `__init__.py` file. Only export what users should directly import.


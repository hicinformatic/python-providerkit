## Project Structure

ProviderKit follows a standard Python package structure with a mixin-based architecture for provider management.

### General Structure

```
python-providerkit/
├── src/
│   └── providerkit/       # Main package directory
│       ├── __init__.py    # Package exports and public API
│       ├── kit/           # Core provider infrastructure
│       │   ├── __init__.py    # ProviderBase class (combines all mixins)
│       │   ├── package.py     # PackageMixin - dependency management
│       │   ├── config.py      # ConfigMixin - configuration management
│       │   ├── service.py     # ServiceMixin - business logic
│       │   └── urls.py        # UrlsMixin - URL routing (if applicable)
│       ├── providers/     # Provider implementations (empty by default)
│       │   └── ...        # Custom providers go here
│       ├── commands/      # Command infrastructure
│       ├── helpers.py     # Utility functions (autodiscovery, loading, etc.)
│       ├── cli.py         # CLI interface
│       └── __main__.py    # Entry point for package execution
├── tests/                 # Test suite
│   └── ...
├── docs/                  # Documentation
│   └── ...
├── service.py             # Main service entry point script
├── pyproject.toml         # Project configuration
└── ...
```

### Module Organization Principles

- **Single Responsibility**: Each module should have a clear, single purpose
- **Separation of Concerns**: Keep different concerns in separate modules
- **Mixin-Based Architecture**: Core functionality is provided through mixins
- **Clear Exports**: Use `__init__.py` to define public API
- **Logical Grouping**: Organize related functionality together

### Kit Organization

The `kit/` directory contains the core provider infrastructure:

- **`__init__.py`**: Defines `ProviderBase` class that combines all mixins
- **`package.py`**: `PackageMixin` - Package dependency management and validation
- **`config.py`**: `ConfigMixin` - Configuration management and validation
- **`service.py`**: `ServiceMixin` - Business logic implementation and service methods
- **`urls.py`**: `UrlsMixin` - URL routing and endpoint management (if applicable)

### Provider Organization

- **`providers/`**: Directory for custom provider implementations
- Providers can be discovered automatically using `autodiscover_providers()`
- Providers can be loaded from JSON configuration or Python modules

### Package Exports

The public API is defined in `src/providerkit/__init__.py`:
- `ProviderBase`: Main base class for all providers
- Mixins: `ConfigMixin`, `PackageMixin`, `UrlsMixin`
- Helper functions: `get_providers()`, `autodiscover_providers()`, `load_providers_from_json()`, etc.
- CLI: `main()` function for command-line interface


# python-providerkit

ProviderKit is a generic provider management library for Python. It provides a standardized way to manage, discover, and interact with multiple service providers in a unified manner.

## Installation

```bash
pip install providerkit
```

For development:

```bash
pip install -e .
pip install -e ".[dev,lint,quality,security,test]"
```

## Usage

ProviderKit provides a mixin-based architecture for creating and managing providers.

### Basic Usage

```python
from providerkit import ProviderBase, get_providers

# Load providers from various sources
providers = get_providers(json="providers.json")
# or
providers = get_providers(dir_path="path/to/providers")
# or
providers = get_providers(config=[{"class": "mypackage.providers.MyProvider", "config": {...}}])

# Use providers
for name, provider in providers.items():
    print(f"{provider.display_name}: {provider.name}")
```

### Creating a Provider

Create a provider by inheriting from `ProviderBase`:

```python
from providerkit import ProviderBase

class EmailProvider(ProviderBase):
    name = "email"
    display_name = "Email Provider"
    description = "Sends emails via SMTP"
    
    def __init__(self, **kwargs):
        super().__init__(
            name="email",
            display_name="Email Provider",
            description="Sends emails via SMTP",
            **kwargs
        )
```

### Provider Discovery

ProviderKit can automatically discover providers from directories:

```python
from providerkit import autodiscover_providers

# Discover providers from a directory
providers = autodiscover_providers("path/to/providers", base_module="mypackage.providers")
```

### Loading from JSON

Create a JSON file with provider configurations:

```json
{
  "providers": [
    {
      "class": "mypackage.providers.EmailProvider",
      "config": {
        "smtp_host": "smtp.example.com",
        "smtp_port": 587
      }
    }
  ]
}
```

Load it:

```python
from providerkit import load_providers_from_json

providers = load_providers_from_json("providers.json")
```

### Loading from Configuration

```python
from providerkit import load_providers_from_config

config = [
    {
        "class": "mypackage.providers.EmailProvider",
        "config": {"smtp_host": "smtp.example.com"},
        "kwargs": {}
    }
]

providers = load_providers_from_config(config)
```

### Provider Mixins

ProviderKit uses a mixin-based architecture. All mixins are automatically included in `ProviderBase`:

- **`PackageMixin`**: Package dependency management and validation
- **`ConfigMixin`**: Configuration management and validation
- **`ServiceMixin`**: Business logic implementation and service methods
- **`UrlsMixin`**: URL routing and endpoint management (if applicable)

## Architecture

ProviderKit uses a mixin-based architecture:

- Each provider inherits from `ProviderBase` which combines all mixins
- Mixins are organized in dedicated files for clear separation of concerns
- Providers can be discovered, queried, and used programmatically
- The system validates dependencies and configuration before allowing provider usage

### Project Structure

```
python-providerkit/
├── src/providerkit/          # Main package
│   ├── kit/                  # Core provider infrastructure
│   │   ├── __init__.py       # ProviderBase class
│   │   ├── package.py        # PackageMixin
│   │   ├── config.py         # ConfigMixin
│   │   ├── service.py        # ServiceMixin
│   │   └── urls.py           # UrlsMixin
│   ├── providers/            # Provider implementations
│   ├── helpers.py            # Utility functions
│   └── cli.py                # CLI interface
├── tests/                    # Test suite
└── docs/                     # Documentation
```

## CLI System

ProviderKit includes a flexible CLI system that discovers commands from:

1. **`commands/` directory**: A directory next to `cli.py` containing command modules
2. **`.commands.json` configuration file**: A JSON file that can specify:
   - `packages`: List of packages to discover commands from
   - `directories`: List of directories to scan for commands
   - `commands`: Direct command definitions

### Creating Commands

Commands can be created in two ways:

#### Method 1: Using the `Command` class

Create a file in the `commands/` directory (e.g., `commands/mycommand.py`):

```python
from .base import Command

def _mycommand_command(args: list[str]) -> bool:
    """Description of what this command does."""
    # Command implementation
    print("Hello from mycommand!")
    return True

mycommand_command = Command(_mycommand_command, "Description of what this command does")
```

#### Method 2: Using functions ending with `_command`

```python
def mycommand_command(args: list[str]) -> bool:
    """Description of what this command does."""
    # Command implementation
    print("Hello from mycommand!")
    return True
```

### Command Structure

Commands receive a list of string arguments and return a boolean indicating success:

```python
def mycommand_command(args: list[str]) -> bool:
    """Command description for help text."""
    if not args:
        print("Usage: mycommand <arg1> <arg2>")
        return False
    
    # Process arguments
    arg1 = args[0]
    # ... command logic ...
    
    return True  # Success
```

## Environment Variables

### `ENVFILE_PATH`

The `ENVFILE_PATH` environment variable allows you to automatically specify the path to a `.env` file to load when starting services.

**Usage:**

```bash
# Absolute path
ENVFILE_PATH=/path/to/.env ./service.py dev install-dev

# Relative path (relative to project root)
ENVFILE_PATH=.env.local ./service.py quality lint
```

**Behavior:**

- If the path is relative, it is resolved relative to the project root
- The `.env` file is automatically loaded before command execution
- Uses `python-dotenv` to parse the file (installed automatically if needed)
- Works with `dev` and `cli` services

### `ENSURE_VIRTUALENV`

The `ENSURE_VIRTUALENV` environment variable allows you to automatically activate the `.venv` virtual environment if it exists, before executing commands.

**Usage:**

```bash
ENSURE_VIRTUALENV=1 ./service.py dev help
ENSURE_VIRTUALENV=1 ./service.py quality lint
```

**Behavior:**

- Must be set to `1` to be active
- Automatically activates the `.venv` virtual environment at the project root
- Modifies `sys.executable`, `PATH`, and `sys.path` to use the venv's Python
- Only works if the `.venv` directory exists
- Compatible with Windows and Unix

**Note:** The `ensure_virtualenv()` function is also automatically called by the main service, but `ENSURE_VIRTUALENV` allows you to force activation even in contexts where it might not be automatic.

## Use Cases

- Multi-provider integrations (email, SMS, payment, etc.)
- Provider fallback mechanisms
- Provider discovery and selection
- Configuration validation across multiple providers
- Unified interface for heterogeneous services

## Development

ProviderKit uses qualitybase for development tooling:

```bash
# Quality checks
./service.py quality lint
./service.py quality security
./service.py quality all

# Development tools
./service.py dev venv
./service.py dev install-dev
./service.py dev clean
```

See `docs/` for project rules and guidelines.


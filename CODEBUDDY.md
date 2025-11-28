# CODEBUDDY.md

This file provides guidance to CodeBuddy Code when working with code in this repository.

## Project Overview

This is **天翼云CLI工具** (CTYUN CLI), a powerful enterprise command-line tool for managing China Telecom Cloud (天翼云) resources through the terminal. It's a Python-based CLI application with 15,000+ lines of code covering 156+ APIs and 136+ commands across 7 major service modules.

## Common Development Commands

### Package Installation and Setup
```bash
# Install the package in development mode
pip install -e .

# Install with development dependencies
pip install -e ".[dev]"

# Install specific dependency groups
pip install -e ".[test]"    # Test dependencies
pip install -e ".[lint]"     # Linting dependencies  
pip install -e ".[build]"    # Build dependencies
```

### Building and Publishing
```bash
# Build the package
python -m build --wheel --no-isolation

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build after cleaning
python -m build

# Publish to test PyPI
python -m twine upload --repository testpypi dist/*

# Publish to production PyPI
python -m twine upload dist/*
```

### Testing
```bash
# Run all tests with coverage
pytest

# Run tests with coverage report
pytest --cov=src --cov-report=term-missing --cov-report=html

# Run specific test file
pytest tests/test_specific.py

# Run tests with verbose output
pytest -v
```

### Code Quality
```bash
# Format code with Black
black src/ tests/

# Check code style with flake8
flake8 src/ tests/

# Run both formatters
black src/ tests/ && flake8 src/ tests/
```

### CLI Usage for Development
```bash
# Test the CLI locally
python -m cli.main --help

# Or after installation
ctyun-cli --help

# Test with debug mode
ctyun-cli --debug ecs list

# Clear cache
ctyun-cli clear-cache

# Configure credentials
ctyun-cli configure --access-key YOUR_KEY --secret-key YOUR_SECRET
```

## Architecture Overview

### Core Architecture Pattern

The project follows a **modular service client architecture**:

```
src/
├── core/           # Base API client and common functionality
├── auth/           # Authentication and signature handling  
├── cli/            # Click-based CLI interface and entry point
├── config/         # Configuration management
├── utils/          # Shared utilities and helpers
├── ecs/            # Cloud Server service module
├── monitor/        # Monitoring service module  
├── redis/          # Distributed cache service module
├── billing/        # Billing and payment module
├── security/       # Security guard service module
├── iam/            # Identity and Access Management
└── ebs/            # Elastic Block Storage
```

### Key Architectural Components

#### 1. **Core Module (`src/core/`)**
- **CTYUNClient**: Base API client class that all service modules inherit from
- **CTYUNAPIError**: Standardized API exception handling
- Provides common HTTP request functionality, authentication, and error handling

#### 2. **Authentication Module (`src/auth/`)**
- **CTYUNAuth**: Handles AK/SK signature-based authentication
- **EOP Signature Implementation**: Enterprise-level signing algorithm
- Secure credential management and request signing

#### 3. **CLI Module (`src/cli/`)**
- **Click Framework**: Declarative CLI interface with nested commands
- **Multi-environment Support**: Profile-based configuration switching
- **Output Formatting**: Table, JSON, and YAML output formats
- **Error Handling**: Consistent error reporting across all commands

#### 4. **Service Modules Pattern**
Each service module (ECS, Monitor, Redis, etc.) follows this pattern:
```
service_name/
├── __init__.py       # Module exports
├── client.py         # Service-specific API client
├── commands.py       # Click command definitions
└── models.py         # Data models and constants
```

### Key Technical Patterns

#### Service Client Pattern
```python
# Each service extends the base CTYUNClient
class ServiceClient:
    def __init__(self, base_client: CTYUNClient):
        self.client = base_client
        
    def api_call(self, endpoint, params=None):
        # Use base client for HTTP requests with authentication
        return self.client.request("GET", endpoint, params=params)
```

#### CLI Command Pattern  
```python
@click.group()
def service_group():
    """Service description"""
    pass

@service_group.command()
@click.option('--region-id', required=True)
@click.pass_context  
def command(ctx, region_id):
    client = ServiceClient(ctx.obj['client'])
    result = client.api_call('/endpoint')
    format_output(result, ctx.obj['output'])
```

#### Configuration Management
- **Multi-profile support**: Different environments (prod, test, dev)
- **Secure credential storage**: File-based with environment variable fallback
- **Output format configuration**: Global and per-command output formatting

## Module Development Guidelines

### Adding New Service Modules

1. **Create module directory**: `src/newservice/`
2. **Implement required files**:
   - `__init__.py`: Module exports with `__all__`
   - `client.py`: Service client extending base functionality
   - `commands.py`: Click command definitions
   - `models.py` (optional): Data models and constants

3. **Register commands** in `src/cli/main.py`:
```python
from newservice.commands import newservice
cli.add_command(newservice)
```

### Import Conventions
```python
# Standard library
import os
from typing import Optional

# Third-party libraries  
import click
import requests

# Local imports - use absolute imports from src root
from core import CTYUNClient
from utils.helpers import OutputFormatter
from auth.signature import CTYUNAuth
```

### Error Handling Pattern
```python
try:
    result = client.api_call('/endpoint')
    if result.get('statusCode') != 800:
        click.echo(f"API Error: {result.get('message')}", err=True)
        return
    # Process successful result
    format_output(result.get('returnObj'), output)
except Exception as e:
    click.echo(f"Error: {e}", err=True)
    if debug:
        import traceback
        traceback.print_exc()
```

## Testing Strategy

### Test Structure
```
tests/
├── test_core/        # Core functionality tests
├── test_auth/        # Authentication tests
├── test_cli/         # CLI command tests  
├── test_services/    # Service module tests
└── fixtures/         # Test data and mocks
```

### Key Testing Patterns

#### Mock API Responses
The project uses mock data for testing when real API endpoints are unavailable:
```python
def test_api_call_with_mock():
    # Mock responses include `_mock: True` flag
    mock_response = {"statusCode": 800, "returnObj": {...}, "_mock": True}
    # Test logic handles both real and mock responses
```

#### CLI Command Testing
```python
def test_cli_command(runner):
    result = runner.invoke(cli, ['ecs', 'list', '--region-id', 'test'])
    assert result.exit_code == 0
    # Verify output format and content
```

## Configuration Files and Their Purpose

### `pyproject.toml`
- **Project metadata**: Name, version, dependencies
- **Build configuration**: setuptools build backend
- **Development tools**: Black, flake8, pytest configurations
- **Optional dependencies**: dev, test, lint, build groups

### `setup.py` 
- **Legacy setup support**: Backward compatibility
- **Dynamic version reading**: From pyproject.toml
- **Entry points**: CLI command registration

### Key Dependencies
- **click** (>=8.1.0): CLI framework
- **requests** (>=2.31.0): HTTP client
- **cryptography** (>=41.0.0): Security and signing
- **colorama** (>=0.4.6): Cross-platform colored terminal output
- **tabulate** (>=0.9.0): Table formatting
- **pyyaml** (>=6.0): YAML output support

## Debugging and Development Tips

### Enabling Debug Mode
```bash
# Global debug mode
ctyun-cli --debug [command]

# Programmatic debug
import logging
logging.getLogger('ctyun_cli').setLevel(logging.DEBUG)
```

### Working with API Responses
- **Successful responses**: `statusCode: 800`
- **Error handling**: Check `statusCode` and `message` fields
- **Mock data detection**: Look for `_mock: True` in responses
- **Pagination**: Most list endpoints support `page` and `page_size` parameters

### Output Formatting
- **Table format** (default): Human-readable with `tabulate`
- **JSON format**: Machine-readable for scripting
- **YAML format**: Configuration management friendly

### Cache Management
- **File-based caching**: API responses cached for performance
- **Cache clearing**: `ctyun-cli clear-cache` command
- **Cache bypass**: `--no-cache` flag where supported

This architecture enables easy extension of new cloud services while maintaining consistent CLI patterns and robust error handling across all modules.
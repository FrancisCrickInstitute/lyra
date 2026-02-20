---
applyTo: "**/*.py"
---

# Python Development Instructions

This file provides Python development guidelines and best practices for this project.

## Environment Setup
To set up the development environment, run the following commands in your terminal:
```bash
if [ ! -d .venv ]; then uv venv .venv; fi
source .venv/bin/activate && uv sync --group dev
```

Run Python commands with:
```bash
source .venv/bin/activate && <COMMAND>
```

## Development Workflow

- Write tests before implementation (TDD approach).
- Run `pytest` after code changes to verify functionality.
## Project Structure

- Python source code: `<project_name>/`
- Python unit tests: `tests/`
- Configuration: `pyproject.toml`

## Code Style

### Formatting
- Follow [PEP 8](https://peps.python.org/pep-0008/) formatting.
- Use double quotes for strings.
- 4 spaces for indentation (no tabs).
- Newline at end of files.
- Line length: 150 characters (configured in `black`).
- Group imports: standard library, third-party, local imports (use `isort`).

### Python 3.13+ Type Hints (PEP 604, PEP 695)
- **Union types**: Use `|` syntax instead of `Union`
  ```python
  # Good
  def process(value: str | int) -> dict[str, Any]: ...
  
  # Avoid
  from typing import Union, Dict, Any
  def process(value: Union[str, int]) -> Dict[str, Any]: ...
  ```

- **Optional types**: Use `X | None` instead of `Optional[X]`
  ```python
  # Good
  def find_user(user_id: int) -> User | None: ...
  
  # Avoid
  from typing import Optional
  def find_user(user_id: int) -> Optional[User]: ...
  ```

- **Built-in generics**: Use built-in types instead of `typing` module
  ```python
  # Good
  def get_names() -> list[str]: ...
  def get_mapping() -> dict[str, int]: ...
  def get_items() -> tuple[str, ...]: ...
  
  # Avoid
  from typing import List, Dict, Tuple
  def get_names() -> List[str]: ...
  ```

- **Type aliases**: Use `type` statement (PEP 695)
  ```python
  # Good
  type UserId = int
  type UserMap = dict[UserId, User]
  
  # Avoid
  UserId = int
  UserMap = dict[int, User]
  ```

- **Generic classes/functions**: Use PEP 695 syntax
  ```python
  # Good
  def first[T](items: list[T]) -> T | None:
      return items[0] if items else None
  
  class Container[T]:
      def __init__(self, value: T) -> None:
          self.value = value
  
  # Avoid
  from typing import TypeVar, Generic
  T = TypeVar('T')
  def first(items: list[T]) -> T | None: ...
  ```

- **Use `collections.abc` for abstract types**
  ```python
  # Good
  from collections.abc import Sequence, Mapping, Callable
  def process(items: Sequence[str]) -> None: ...
  
  # Avoid
  from typing import Sequence, Mapping, Callable
  ```

### Modern Python Features

- **F-strings**: Use for all string interpolation and formatting
  ```python
  # Good
  message = f"User {user.name} has {count} items"
  
  # Avoid
  message = "User {} has {} items".format(user.name, count)
  message = "User %s has %d items" % (user.name, count)
  ```

- **Pathlib**: Use `pathlib.Path` instead of `os.path`
  ```python
  # Good
  from pathlib import Path
  config_file = Path("config") / "settings.toml"
  if config_file.exists():
      content = config_file.read_text()
  
  # Avoid
  import os
  config_file = os.path.join("config", "settings.toml")
  if os.path.exists(config_file):
      with open(config_file) as f:
          content = f.read()
  ```

- **Context managers**: Always use for resource management
  ```python
  # Good
  with open(file_path) as f:
      data = f.read()
  
  # Required for multiple resources
  with (
      open(input_file) as fin,
      open(output_file, "w") as fout,
  ):
      fout.write(process(fin.read()))
  ```

- **Structural pattern matching** (Python 3.10+): Use for complex conditionals
  ```python
  match response.status_code:
      case 200:
          return response.json()
      case 404:
          raise NotFoundError()
      case code if 400 <= code < 500:
          raise ClientError(code)
      case _:
          raise ServerError()
  ```

- **Exception groups** (Python 3.11+): Use for multiple exception handling
  ```python
  try:
      process_batch(items)
  except* ValueError as eg:
      log_value_errors(eg.exceptions)
  except* IOError as eg:
      log_io_errors(eg.exceptions)
  ```

- **Dataclasses/Pydantic**: Use for structured data
  ```python
  from pydantic import BaseModel, Field
  
  class UserProfile(BaseModel):
      user_id: str
      email: str | None = None
      name: str
      score: float = Field(ge=0.0, le=100.0)
  ```

### Code Quality Standards

- **Type checking**: All functions should have complete type annotations
- **Docstrings**: Use Google or NumPy style for all public APIs
  ```python
  def process_data(input_id: str, output_dir: Path) -> dict[str, Any]:
      """Process input data and write results to the output directory.
      
      Args:
          input_id: Unique identifier for the input data
          output_dir: Directory where outputs will be written
          
      Returns:
          Dictionary containing result metadata
          
      Raises:
          ValueError: If input_id is invalid
          FileNotFoundError: If input data cannot be located
      """
      ...
  ```

- **Error handling**: Be specific with exception types
  ```python
  # Good - specific exceptions
  try:
      data = parse_config(path)
  except FileNotFoundError:
      logger.error(f"Config file not found: {path}")
      raise
  except toml.TomlDecodeError as e:
      logger.error(f"Invalid TOML syntax: {e}")
      raise ValueError(f"Invalid config file: {path}") from e
  
  # Avoid - bare except
  try:
      data = parse_config(path)
  except:
      logger.error("Something went wrong")
  ```

- **Immutability**: Prefer immutable data structures where appropriate
  ```python
  # Good - use tuples for fixed collections
  SUPPORTED_FORMATS = ("json", "csv", "parquet")
  
  # Good - frozen dataclasses for immutable objects
  from dataclasses import dataclass
  
  @dataclass(frozen=True)
  class RunConfig:
      platform: str
      output_dir: Path
  ```

## Testing

### Test Organization
- Write tests in `tests/` with filenames starting with `test_`.
- Mirror source structure in test names (e.g., ``<project_name>/utils/parser.py` → `tests/test_parser.py`).
- Organize tests in classes by feature or component.
- Use descriptive test names: `test_<function>_<scenario>_<expected_result>`
  ```python
  class TestDataParser:
      def test_parse_valid_input_returns_result(self): ...
      def test_parse_missing_file_raises_file_not_found(self): ...
      def test_parse_invalid_input_raises_value_error(self): ...
  ```

### Pytest Best Practices
- **Fixtures**: Use for setup/teardown and shared test data
  ```python
  import pytest
  from pathlib import Path
  
  @pytest.fixture
  def sample_data_file() -> Path:
      return Path(__file__).parent / "data" / "sample_input.json"
  
  def test_parse_data(sample_data_file: Path):
      result = parse_data(sample_data_file)
      assert result.id == "expected_id"
  ```

- **Parametrize**: Test multiple scenarios efficiently
  ```python
  @pytest.mark.parametrize("input,expected", [
      ("ATCG", True),
      ("ATCN", False),
      ("", False),
      ("atcg", True),
  ])
  def test_is_valid_sequence(input: str, expected: bool):
      assert is_valid_sequence(input) == expected
  ```

- **Assertpy**: Use for readable assertions
  ```python
  from assertpy import assert_that
  
  def test_get_samples_returns_correct_count():
      samples = get_samples(run_id="test_run")
      assert_that(samples).is_not_empty()
      assert_that(samples).is_length(5)
      assert_that(samples[0]).has_sample_id("sample_001")
  ```

### Test Isolation
- **Mock external dependencies**: Use `unittest.mock` or `pytest-mock`
  ```python
  from unittest.mock import Mock, patch
  
  def test_fetch_record_calls_api(mock_api_client: Mock):
      with patch("mypackage.api.client.ApiClient") as mock_client:
          mock_client.return_value.get_record.return_value = {"id": "123"}
          result = fetch_record("record_001")
          mock_client.return_value.get_record.assert_called_once_with("record_001")
  ```

- **Avoid testing external services**: Mock HTTP calls, database connections, file I/O
- **Temporary files**: Use `pytest.tmp_path` fixture
  ```python
  def test_write_config_creates_file(tmp_path: Path):
      config_file = tmp_path / "config.toml"
      write_config(config_file, {"key": "value"})
      assert config_file.exists()
      assert "key" in config_file.read_text()
  ```

### Coverage Expectations
- Aim for >80% coverage on new code
- Focus on testing business logic and edge cases
- Don't test trivial getters/setters
- Don't test third-party library code
- Use `pytest --cov=src --cov-report=html` to generate coverage reports

## Code Quality

### Pre-commit Checklist
Before committing code, ensure:
1. **Tests pass**: Run `pytest`
2. **Type checking**: Run `mypy <project_name>/` (if configured)
3. **Format code**: 
   - `black `<project_name>/ tests/` for code formatting
   - `isort <project_name>/ tests/` for import sorting
4. **Lint**: Run `ruff check .`
5. **Additional linting**: Run `pylint <project_name>/` for deeper static analysis
6. **Coverage**: Aim for >80% test coverage on new code

### Tool Configuration
- **Black**: Line length 150, Python 3.13+ target
- **isort**: Black-compatible profile, line length 150
- **Ruff**: Fast linter replacing flake8, pycodestyle, pyflakes
- **Pylint**: Additional static analysis for code quality
- **pytest**: Test framework with `assertpy` for assertions

### Type Checking Best Practices
- Enable strict mode in mypy if possible
- Annotate all function signatures (params + return type)
- Use `reveal_type()` during development to debug type inference
- Avoid `Any` unless absolutely necessary; use protocols or generics instead
- Use `typing.assert_never()` for exhaustiveness checking in match statements

### Code Review Focus Areas
- Type safety: All functions properly annotated
- Error handling: Specific exceptions with proper context
- Resource management: Context managers for files, connections, etc.
- Testing: All new code has corresponding tests
- Documentation: Public APIs have complete docstrings
- Performance: No obvious inefficiencies (N+1 queries, redundant I/O)
- Security: No hardcoded credentials, proper input validation

## Conventions

- Write clear, minimal code (KISS principle).
- Avoid code duplication (DRY principle).
- Add docstrings to all public functions and classes.
- Comment complex logic, but avoid obvious comments.
- Use descriptive names for functions, variables, and classes.

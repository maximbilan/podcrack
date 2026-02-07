# Test Suite

Unit tests for podcrack using pytest.

## Running Tests

```bash
# Install dependencies (if not already installed)
pip install -r requirements.txt

# Run all tests
pytest

# Run with coverage
pytest --cov=podcrack --cov-report=html

# Run specific test file
pytest tests/test_parser.py

# Run specific test
pytest tests/test_parser.py::TestParseTimestamp::test_hours_minutes_seconds
```

## Test Coverage

The test suite covers:

- **Parser** (`test_parser.py`): TTML parsing, timestamp conversion, text extraction
- **Models** (`test_models.py`): Data model properties and methods
- **Scanner** (`test_scanner.py`): File discovery and database checks
- **Metadata** (`test_metadata.py`): Transcript identifier extraction
- **Export** (`test_export.py`): Filename sanitization and file saving

## Test Structure

Tests are organized by module with descriptive class and method names:
- `TestClassName` classes group related tests
- `test_method_name` methods test specific functionality
- Fixtures and mocks are used for isolation

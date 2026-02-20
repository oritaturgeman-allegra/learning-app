# Code Quality Agent

Review code for quality issues and apply fixes following project best practices. Operates in two modes: **Review** (identify issues) and **Fix** (apply improvements).

## When to Use

- Code review before merge
- Refactoring existing code
- Improving code quality (type hints, exceptions, logging)
- Eliminating code duplication
- Modernizing patterns (sync → async, dict → dataclass)

---

## Modes

### Review Mode
Analyze code and report issues without making changes.

### Fix Mode
Apply improvements incrementally while preserving behavior.

---

## Quality Checklist

| Area | Check For |
|------|-----------|
| **Type Hints** | All functions have type hints |
| **Exceptions** | Custom exceptions, not generic `Exception` |
| **Logging** | Uses `logging`, not `print()` |
| **Async** | I/O operations use `async/await` |
| **Data Models** | Dataclasses for structured data, not dicts |
| **DRY Principle** | No repeated code blocks; extract reusable utilities |
| **Functions** | Small, focused functions (single responsibility) |
| **Security** | No OWASP top 10 vulnerabilities |
| **Tests** | Tests included/updated for changes |

---

## Review Mode Process

1. Read the files or changes provided
2. Check against project conventions
3. Categorize issues by severity
4. Report findings

### Review Output

```markdown
## Code Review: [File/Feature]

### Summary
Brief overview of what was reviewed.

### Issues Found

**Critical** (must fix before merge):
- [ ] Issue 1: [description] (line X)

**Warning** (should fix):
- [ ] Issue 2: [description] (line X)

**Suggestion** (nice to have):
- [ ] Issue 3: [description] (line X)

### Quality Checklist
- [ ] Type hints complete
- [ ] Custom exceptions used
- [ ] No security vulnerabilities
- [ ] Tests included/updated
- [ ] Logging properly used
- [ ] Follows project conventions
```

---

## Fix Mode Process

1. Identify what needs improvement
2. Make changes incrementally (one at a time)
3. Preserve existing behavior
4. Run tests after each change

### Common Fixes

**Missing Type Hints**
```python
# Before
def process(data):
    return data.upper()

# After
def process(data: str) -> str:
    return data.upper()
```

**Generic Exception → Custom Exception**
```python
# Before
raise Exception("Feed fetch failed")

# After
raise FeedFetchError(url, "Connection timeout")
```

**Print → Logging**
```python
# Before
print(f"Processing {url}")

# After
logger.info(f"Processing {url}")
```

**Sync → Async for I/O**
```python
# Before
def fetch_data(url: str) -> dict:
    response = requests.get(url)
    return response.json()

# After
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
```

**Dict → Dataclass**
```python
# Before
result = {"name": "test", "count": 42, "active": True}

# After
@dataclass
class Result:
    name: str
    count: int
    active: bool

result = Result(name="test", count=42, active=True)
```

**Long Function → Smaller Functions**
```python
# Before: One 50-line function doing multiple things

# After: Multiple focused functions
def fetch_articles() -> list[Article]: ...
def filter_by_date(articles: list[Article]) -> list[Article]: ...
def sort_by_relevance(articles: list[Article]) -> list[Article]: ...
```

**Duplicated Code → Reusable Utility (DRY)**
```python
# Before: Same logic repeated in multiple places
def process_us_market(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    return format_output(transformed)

def process_israel_market(data):
    validated = validate_data(data)
    transformed = transform_data(validated)
    return format_output(transformed)

# After: Extract common pipeline
def process_market(data: MarketData, market_type: str) -> FormattedOutput:
    """Generic market processing pipeline."""
    validated = validate_data(data)
    transformed = transform_data(validated)
    return format_output(transformed)
```

### Fix Constraints

- Do NOT change external APIs or interfaces
- Do NOT add new features
- Do NOT over-engineer
- Keep backwards compatibility
- Run tests after each change

### Fix Output

```markdown
## Refactoring: [File/Feature]

### Changes Made
1. Added type hints to X functions
2. Replaced generic exceptions with custom FeedFetchError
3. Converted print statements to logging

### Before/After

**Type hints added:**
```python
# Before
def process(data):

# After
def process(data: str) -> str:
```

### Test Command
```bash
.venv/bin/pytest tests/unit/test_xxx.py -v
```
```

---

## Project Conventions

Reference: `CLAUDE.md` and `docs/architecture/overview.md`

- Type hints on ALL functions
- Custom exceptions in `backend/exceptions.py`
- Dataclasses for data models
- Logging with structured request IDs
- Async for I/O operations
- Pydantic for API validation
- Tests required for new features

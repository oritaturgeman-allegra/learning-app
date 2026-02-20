# API Endpoint Agent

Create a new API endpoint following project patterns.

## Instructions

1. Check existing patterns in `backend/routes/`
2. **Apply DRY Principle**: Before creating new code, check if similar functionality exists. Reuse existing services, utilities, and patterns. Extract common logic into shared modules.
3. Follow FastAPI conventions:
   - Use Pydantic models for request/response validation
   - Add proper type hints
   - Use async for I/O operations
   - Return appropriate status codes (200, 201, 202 for async, 4xx, 5xx)
   - Add OpenAPI documentation (docstrings)

3. Structure:
   - Route in `backend/routes/`
   - Business logic in `backend/services/`
   - Data models in `backend/models/`

## Template

```python
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

router = APIRouter()

class RequestModel(BaseModel):
    """Request schema."""
    field: str

class ResponseModel(BaseModel):
    """Response schema."""
    result: str

@router.post("/endpoint", response_model=ResponseModel, status_code=status.HTTP_201_CREATED)
async def endpoint_name(request: RequestModel) -> ResponseModel:
    """
    Endpoint description for OpenAPI docs.

    - **field**: Description of field
    """
    # Implementation
    return ResponseModel(result="value")
```

## Output

Provide complete implementation with:
- Route definition
- Service layer (if needed)
- Pydantic models
- Tests

# Database Agent

Handle database schema changes, migrations, and queries.

## Instructions

1. Check existing models in `backend/models/`
2. Follow SQLAlchemy patterns used in the project
3. For schema changes:
   - Update model in `backend/models/`
   - Consider data migration if needed
   - Update related services in `backend/services/db_service.py`

## Model Template

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from backend.models.base import Base
from datetime import datetime

class ModelName(Base):
    """Description of the model."""

    __tablename__ = "table_name"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    parent_id = Column(Integer, ForeignKey("parent_table.id"))
    parent = relationship("ParentModel", back_populates="children")
```

## Output

- Model definition
- Service methods for CRUD operations
- Migration steps (if applicable)
- Tests for new functionality

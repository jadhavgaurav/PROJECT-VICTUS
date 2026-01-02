from pydantic import BaseModel, Field
from typing import Optional

class RememberFactSchema(BaseModel):
    key: str = Field(..., description="The label or key for the fact (e.g., 'wife's name').")
    value: str = Field(..., description="The value of the fact (e.g., 'Jane').")
    user_id: Optional[str] = Field(default=None, description="Optional user ID. Defaults to current user if omitted.")

class RecallFactSchema(BaseModel):
    key: str = Field(..., description="The label or key of the fact to recall.")
    user_id: Optional[str] = Field(default=None, description="Optional user ID. Defaults to current user if omitted.")

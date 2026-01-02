from pydantic import BaseModel, Field

class QueryUploadedDocumentsSchema(BaseModel):
    query: str = Field(..., description="The question or query to ask about the uploaded documents.")

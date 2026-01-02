from pydantic import BaseModel, Field
from typing import Optional

class ListFilesSchema(BaseModel):
    directory: str = Field(..., description="The directory path or shortcut (e.g., 'desktop', 'documents') to list files from.")

class OpenAppSchema(BaseModel):
    application_name: str = Field(..., description="The name of the application to open (e.g., 'chrome', 'calculator').")

class GetClipboardContentSchema(BaseModel):
    pass

class TakeScreenshotSchema(BaseModel):
    path: str = Field(default="desktop", description="The path or shortcut where the screenshot should be saved.")

class TypeTextSchema(BaseModel):
    text: str = Field(..., description="The text to type using the keyboard.")

class GetActiveWindowTitleSchema(BaseModel):
    pass

class GetSystemInfoSchema(BaseModel):
    pass

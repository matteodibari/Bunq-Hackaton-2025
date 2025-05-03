from pydantic import BaseModel, Field
import requests
from bs4 import BeautifulSoup


class InputDocument(BaseModel):
    """
    Represents raw document data before processing.
    """
    content: str = Field(..., description="The text content of the document chunk")
    metadata: dict = Field(default_factory=dict, description="Metadata about the document chunk")


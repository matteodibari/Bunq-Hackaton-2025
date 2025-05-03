from typing import List, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    """
    Represents a chat message in the conversation.
    """
    role: str = Field(..., description="The role of the message sender (user or assistant)")
    content: str = Field(..., description="The content of the message")


class ChatRequest(BaseModel):
    """
    Request model for chat interactions.
    """
    messages: List[Message] = Field(..., description="List of previous messages in the conversation")
    temperature: Optional[float] = Field(0.7, description="Temperature for response generation")
    max_tokens: Optional[int] = Field(500, description="Maximum number of tokens in the response")


class ChatResponse(BaseModel):
    """
    Response model for chat interactions.
    """
    response: str = Field(..., description="The assistant's response")


class InputDocument(BaseModel):
    """
    Represents raw document data before processing.
    """
    content: str = Field(..., description="The text content of the document chunk")
    metadata: dict = Field(default_factory=dict, description="Metadata about the document chunk")

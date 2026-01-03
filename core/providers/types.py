from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from datetime import datetime

class Role(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class Message(BaseModel):
    role: Role
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class ModelCapability(str, Enum):
    CHAT = "chat"
    VISION = "vision"
    EMBEDDING = "embedding"

class ModelInfo(BaseModel):
    id: str
    name: str
    provider: str
    capabilities: List[ModelCapability] = [ModelCapability.CHAT]
    context_window: Optional[int] = None
    max_tokens: Optional[int] = None
    provider_id: Optional[str] = None

class ProviderConfig(BaseModel):
    name: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    enabled: bool = True
    init_error: Optional[str] = None  # Speichert Fehler wie "API Key missing"
    status: Optional[str] = "unknown" # 'active', 'error' (synced from Manager)

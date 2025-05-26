from typing import Optional
from pydantic import BaseModel

class AuthAgencyDTO(BaseModel):
    accessKey: Optional[str] = None
    nonce: Optional[str] = None
    timestamp: Optional[str] = None

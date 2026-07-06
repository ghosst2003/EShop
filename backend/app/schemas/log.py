from datetime import datetime
from typing import Optional

from pydantic import BaseModel


# ---- Operation Log ----
class OperationLogOut(BaseModel):
    id: int
    user_id: int
    action: str
    entity_type: str
    entity_id: Optional[int] = None
    details: Optional[dict] = None
    ip_address: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}

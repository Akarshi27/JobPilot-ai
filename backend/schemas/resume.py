from datetime import datetime

from pydantic import BaseModel


class ResumeResponse(BaseModel):
    id: int
    user_id: int
    original_filename: str
    file_type: str
    extracted_text: str | None
    analysis_status: str = "PENDING"
    analysis_error: str | None = None
    is_current: bool = True
    created_at: datetime

    class Config:
        from_attributes = True
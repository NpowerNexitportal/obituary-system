from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class ObituaryResponse(BaseModel):
    id: str = Field(alias="_id")
    name: str
    title: str
    slug: str
    content: str
    meta_description: str
    date_of_death: Optional[str] = None
    location: Optional[str] = None
    source_url: str
    created_at: datetime
    
    class Config:
        populate_by_name = True

class PaginatedObituaries(BaseModel):
    total: int
    page: int
    size: int
    data: List[ObituaryResponse]

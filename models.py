from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, HttpUrl, Field

class Event(BaseModel):
    """
    Pydantic model for a single event.
    """
    title: str = Field(..., description="The main title of the event.")
    link: HttpUrl = Field(..., description="The direct URL to the event page.")
    description: Optional[str] = Field(None, description="A summary of the event.")
    source: str = Field(..., description="The source website (e.g., 'I Amsterdam Official').")
    date_text: List[str] = Field(..., description="A list of scraped text representing the event dates.")
    price_text: str = Field(..., description="The scraped text representing the event price.")
    pub_date: datetime = Field(..., description="The publication date of the event in the feed.")
    tags: List[str] = Field(default_factory=list, description="A list of tags or categories.")
    location: str = Field("Amsterdam", description="The general location of the event.")
    image: Optional[HttpUrl] = Field(None, description="A URL for the main event image.")

    class Config:
        """Pydantic config."""
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            HttpUrl: lambda v: str(v),
        }
        validate_assignment = True 
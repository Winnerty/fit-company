from pydantic import BaseModel, Field
from datetime import datetime

class BillingInfoSchema(BaseModel):
    credit_card_number: str = Field(..., min_length=16, max_length=16)
    expiration_date: datetime
    cvv: str = Field(..., min_length=3, max_length=3)
    card_holder_name: str
    email: str

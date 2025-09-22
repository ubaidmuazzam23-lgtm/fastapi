# from beanie import Document
# from pydantic import Field
# from typing import Optional
# from datetime import datetime

# class Debt(Document):
#     clerk_user_id: str = Field(..., index=True)
#     name: str = Field(..., min_length=1, max_length=100)
#     total_amount: float = Field(..., ge=0)
#     interest_rate: float = Field(..., ge=0, le=100)
    
#     created_at: datetime = Field(default_factory=datetime.utcnow)
#     updated_at: datetime = Field(default_factory=datetime.utcnow)
#     is_active: bool = Field(default=True)
    
#     class Settings:
#         name = "debts"
#         indexes = [
#             "clerk_user_id",
#             "created_at"
#         ]

#     def to_dict(self):
#         data = self.model_dump()
#         data['id'] = str(self.id)
#         return data

#     def calculate_monthly_interest(self):
#         return self.total_amount * (self.interest_rate / 100 / 12)


from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime

class Debt(Document):
    clerk_user_id: str = Field(..., index=True)
    name: str = Field(..., min_length=1, max_length=100)
    total_amount: float = Field(..., ge=0)
    interest_rate: float = Field(..., ge=0, le=100)
    min_payment: float = Field(default=0.0, ge=0)  # Add this field
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True)
    
    class Settings:
        name = "debts"
        indexes = [
            "clerk_user_id",
            "created_at"
        ]

    def to_dict(self):
        data = self.model_dump()
        data['id'] = str(self.id)
        return data

    def calculate_monthly_interest(self):
        return self.total_amount * (self.interest_rate / 100 / 12)
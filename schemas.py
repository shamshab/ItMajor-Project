from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

#UserBase
class UserBase(BaseModel):
    username: str
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

#Bucketlist

class BucketListItemBase(BaseModel):
    title: str
    description: Optional[str] = None

class BucketListItemCreate(BucketListItemBase):
    pass

class BucketListItem(BucketListItemBase):
    id: int

    class Config:
        from_attributes = True

class BucketListUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None

#reminder
class ReminderBase(BaseModel):
    user_id: int  # Add this line
    bucketlist_item_id: int
    reminder_date: datetime
    message: Optional[str] = None


class ReminderCreate(ReminderBase):
    pass

class Reminder(ReminderBase):
    id: int

    class Config:
        orm_mode = True


#budget
# Base schema for Budget
class BudgetBase(BaseModel):
    bucketlist_item_id: int
    budget_amount: float
    spent_amount: Optional[float] = 0.0

class BudgetCreate(BudgetBase):
    user_id: int

class BudgetUpdate(BudgetBase):
    pass

class Budget(BudgetBase):
    id: int

    class Config:
        orm_mode = True
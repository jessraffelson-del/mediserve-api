from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum


class Role(str, Enum):
    ADMIN = "admin"
    DOCTOR = "doctor"
    PATIENT = "patient"
    INSURANCE = "insurance"


class User(BaseModel):
    username: str
    email: EmailStr
    role: Role
    disabled: Optional[bool] = False


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[Role] = None


class PatientRecord(BaseModel):
    patient_id: str
    name: str
    diagnosis: str
    prescription: Optional[str] = None
    insurance_id: Optional[str] = None


class PatientRecordResponse(BaseModel):
    patient_id: str
    name: str
    diagnosis: Optional[str] = None
    prescription: Optional[str] = None
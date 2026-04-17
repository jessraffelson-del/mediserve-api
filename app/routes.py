from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import List
from app.auth import (
    authenticate_user,
    create_access_token,
    decode_token,
    oauth2_scheme
)
from app.models import (
    Token,
    User,
    PatientRecord,
    PatientRecordResponse,
    Role
)
from datetime import timedelta

router = APIRouter()

# Fake patient records database
PATIENT_RECORDS = {
    "P001": PatientRecord(
        patient_id="P001",
        name="John Doe",
        diagnosis="Hypertension",
        prescription="Lisinopril 10mg",
        insurance_id="INS-123"
    ),
    "P002": PatientRecord(
        patient_id="P002",
        name="Jane Smith",
        diagnosis="Type 2 Diabetes",
        prescription="Metformin 500mg",
        insurance_id="INS-456"
    ),
    "P003": PatientRecord(
        patient_id="P003",
        name="Bob Johnson",
        diagnosis="Asthma",
        prescription="Albuterol inhaler",
        insurance_id="INS-789"
    )
}


# Dependency — get current user from token
async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token_data = decode_token(token)
    if token_data is None:
        raise credentials_exception
    from app.auth import get_user
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
    return user


# Dependency — require specific roles
def require_role(*roles: Role):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required roles: {[r.value for r in roles]}"
            )
        return current_user
    return role_checker


# Public endpoint
@router.get("/health", tags=["Public"])
async def health_check():
    return {
        "status": "healthy",
        "service": "MediServe API",
        "version": "1.0.0"
    }


# Authentication endpoint
@router.post("/token", response_model=Token, tags=["Authentication"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=30)
    )
    return Token(access_token=access_token, token_type="bearer")


# Doctor and Admin only - full patient record
@router.get(
    "/patients/{patient_id}",
    response_model=PatientRecord,
    tags=["Patient Records"]
)
async def get_patient_record(
    patient_id: str,
    current_user: User = Depends(require_role(Role.DOCTOR, Role.ADMIN))
):
    record = PATIENT_RECORDS.get(patient_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return record


# Insurance - limited view, no diagnosis or prescription
@router.get(
    "/patients/{patient_id}/insurance",
    response_model=PatientRecordResponse,
    tags=["Patient Records"]
)
async def get_patient_insurance_view(
    patient_id: str,
    current_user: User = Depends(require_role(Role.INSURANCE, Role.ADMIN))
):
    record = PATIENT_RECORDS.get(patient_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Patient {patient_id} not found"
        )
    return PatientRecordResponse(
        patient_id=record.patient_id,
        name=record.name
    )


# Admin only - list all patients
@router.get(
    "/patients",
    response_model=List[PatientRecord],
    tags=["Patient Records"]
)
async def list_all_patients(
    current_user: User = Depends(require_role(Role.ADMIN))
):
    return list(PATIENT_RECORDS.values())


# Any authenticated user - their own profile
@router.get("/me", response_model=User, tags=["Users"])
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
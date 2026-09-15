from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.database import get_db
from app import models, schemas
from app.email_utils import generate_otp, send_otp_email

router = APIRouter(
    prefix="/otp",
    tags=["OTP Verification"]
)

# ---------------------------------------------------------
# 1. VERIFY OTP ENDPOINT (URL: POST /otp/verify)
# ---------------------------------------------------------
@router.post("/verify")
def verify_otp(data: schemas.VerifyOTP, db: Session = Depends(get_db)):
    """Verifies the OTP sent to user email"""
    user = db.query(models.User).filter(models.User.email == data.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    if user.is_verified:
        return {"message": "Account is already verified. You can log in."}

    if user.otp_code != data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid OTP code"
        )

    user.is_verified = True
    user.otp_code = None 
    db.commit()

    return {"message": "Account verified successfully! You can now log in."}


# ---------------------------------------------------------
# 2. RESEND OTP ENDPOINT (URL: POST /otp/resend)
# ---------------------------------------------------------
class ResendOTPRequest(BaseModel):
    email: str

# 2. URL  "/resend-otp"  

@router.post("/resend-otp")
def resend_otp(request: ResendOTPRequest, db: Session = Depends(get_db)):
    """Resends a new OTP to the user's email if needed"""
    user = db.query(models.User).filter(models.User.email == request.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User not found"
        )
        
    if user.is_verified:
        return {"message": "Account is already verified."}

    # Generate a new OTP and update DB
    new_otp = generate_otp()
    user.otp_code = new_otp
    db.commit()

    # Send email
    send_otp_email(email_to=user.email, otp_code=new_otp)

    return {"message": "A new OTP code has been sent to your email."}
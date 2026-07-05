"""Auth endpoints — paths/shapes frozen by contract_reference.json."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import (
    ForgotPasswordRequest,
    LoginRequest,
    RefreshRequest,
    ResetPasswordRequest,
    SignupRequest,
    TokenResponse,
    VerifyEmailRequest,
)
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED
)
def signup(payload: SignupRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.signup(
        db,
        organization_name=payload.organization_name,
        email=payload.email,
        password=payload.password,
        sector=payload.sector,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.login(db, email=payload.email, password=payload.password)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    return auth_service.refresh(db, refresh_token=payload.refresh_token)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def logout(payload: RefreshRequest, db: Session = Depends(get_db)) -> Response:
    auth_service.logout(db, refresh_token=payload.refresh_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/verify-email", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def verify_email(
    payload: VerifyEmailRequest, db: Session = Depends(get_db)
) -> Response:
    auth_service.verify_email(db, token=payload.token)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/forgot-password", status_code=status.HTTP_202_ACCEPTED, response_class=Response
)
def forgot_password(
    payload: ForgotPasswordRequest, db: Session = Depends(get_db)
) -> Response:
    auth_service.forgot_password(db, email=payload.email)
    return Response(status_code=status.HTTP_202_ACCEPTED)


@router.post(
    "/reset-password", status_code=status.HTTP_204_NO_CONTENT, response_class=Response
)
def reset_password(
    payload: ResetPasswordRequest, db: Session = Depends(get_db)
) -> Response:
    auth_service.reset_password(
        db, token=payload.token, new_password=payload.new_password
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)

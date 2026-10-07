import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from urllib.parse import quote
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from fastapi import Depends, FastAPI, File, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, EmailStr, Field, field_validator
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import engine, get_db
from app.email import EmailDeliveryError, SmtpEmailSender, TransactionalEmail
from app.models import Base, ChefVerification, EmailVerificationToken, User, UserSession
from app.storage import S3Storage, StorageBucket, StorageError, StorageValidationError

settings = get_settings()
logger = logging.getLogger(__name__)
password_hasher = PasswordHasher(time_cost=2, memory_cost=19_456, parallelism=1)
bearer_scheme = HTTPBearer(auto_error=False)
EMAIL_VERIFICATION_TTL = timedelta(hours=24)


class VerificationTokenAccessLogFilter(logging.Filter):
    """Remove verification query strings from Uvicorn access-log request targets."""

    def filter(self, record: logging.LogRecord) -> bool:
        # Uvicorn 0.30 logs access records as (client, method, full_path,
        # http_version, status). Keep the path while omitting every query value
        # for the one endpoint whose query contains a bearer credential.
        args = record.args
        if (
            not isinstance(args, tuple)
            or len(args) < 3
            or args[1] != "GET"
            or not isinstance(args[2], str)
        ):
            return True

        request_path = args[2].partition("?")[0]
        if request_path.rstrip("/") == "/api/auth/verify-email":
            sanitized_args = list(args)
            sanitized_args[2] = "/api/auth/verify-email"
            record.args = tuple(sanitized_args)
        return True


logging.getLogger("uvicorn.access").addFilter(VerificationTokenAccessLogFilter())


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: Literal["regular"] = "regular"
    display_name: Optional[str] = Field(default=None, min_length=1, max_length=255)

    @field_validator("display_name")
    @classmethod
    def normalize_display_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        normalized = value.strip()
        if not normalized:
            raise ValueError("Display name must not be blank")
        return normalized


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class ChefVerificationDecisionRequest(BaseModel):
    decision: Literal["approve", "reject"]
    rationale: Optional[str] = Field(default=None, max_length=2000)

    @field_validator("rationale")
    @classmethod
    def normalize_rationale(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        normalized = value.strip()
        return normalized or None


def get_email_sender() -> SmtpEmailSender:
    return SmtpEmailSender()


def get_storage() -> S3Storage:
    return S3Storage()


app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(password: str, stored_hash: str) -> bool:
    if not stored_hash.startswith("$argon2id$"):
        return False
    try:
        return password_hasher.verify(stored_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_current_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> UserSession:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    session = db.query(UserSession).filter(UserSession.token_hash == token_digest(credentials.credentials)).first()
    if session is None or session.revoked_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= datetime.now(timezone.utc):
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")

    if db.query(User.id).filter(User.id == session.user_id, User.is_system_account.is_(False)).first() is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return session


def get_current_user(
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> User:
    user = db.query(User).filter(User.id == current_session.user_id).first()
    if user is None or user.is_system_account:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired session")
    return user


def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Administrator access required")
    return current_user


@app.on_event("startup")
def startup() -> None:
    if settings.database_url.startswith("sqlite"):
        Base.metadata.create_all(bind=engine)


@app.get("/health")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "service": settings.app_name, "environment": settings.app_env}


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome to the Recipe App API", "status": "ready"}


@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> dict:
    email = str(payload.email).lower()
    user = User(
        email=email,
        display_name=payload.display_name or email.partition("@")[0],
        password_hash=hash_password(payload.password),
        role="regular",
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with that email already exists") from None
    db.refresh(user)
    return {
        "message": "User registered successfully",
        "user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role},
    }


@app.post("/api/auth/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> dict:
    email = str(payload.email).lower()
    user = db.query(User).filter(User.email == email).first()
    if not user or user.is_system_account or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    token = secrets.token_urlsafe(32)
    session = UserSession(
        user_id=user.id,
        token_hash=token_digest(token),
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.auth_session_ttl_seconds),
    )
    db.add(session)
    db.commit()
    return {
        "token": token,
        "user": {"id": user.id, "email": user.email, "display_name": user.display_name, "role": user.role},
        "expires_at": session.expires_at.isoformat(),
    }


@app.post("/api/auth/logout")
def logout(
    current_session: UserSession = Depends(get_current_session),
    db: Session = Depends(get_db),
) -> dict:
    current_session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    return {"message": "Logged out successfully"}


@app.get("/api/auth/me")
def me(current_user: User = Depends(get_current_user)) -> dict:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "display_name": current_user.display_name,
        "role": current_user.role,
    }


@app.get("/api/admin/chef-verifications")
def list_pending_chef_verifications(
    status_filter: Literal["pending"] = Query(default="pending", alias="status"),
    _admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    storage: S3Storage = Depends(get_storage),
) -> dict:
    applications = (
        db.query(ChefVerification, User)
        .join(User, User.id == ChefVerification.user_id)
        .filter(ChefVerification.status == "pending_review")
        .order_by(ChefVerification.created_at, ChefVerification.id)
        .all()
    )
    result = []
    bucket_prefix = f"{StorageBucket.CHEF_CERTIFICATES.value}/"
    for application, applicant in applications:
        if not application.certificate_ref.startswith(bucket_prefix):
            logger.error("Chef application %s has an invalid certificate reference", application.id)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not load Chef applications",
            )
        object_key = application.certificate_ref[len(bucket_prefix):]
        try:
            certificate_url = storage.generate_presigned_download_url(
                StorageBucket.CHEF_CERTIFICATES,
                object_key,
                private_access_authorized=True,
            )
        except StorageError:
            logger.exception("Could not create a certificate review link for application %s", application.id)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Certificate storage is unavailable",
            ) from None
        result.append(
            {
                "id": application.id,
                "status": application.status,
                "created_at": application.created_at.isoformat(),
                "applicant": {
                    "id": applicant.id,
                    "email": applicant.email,
                    "display_name": applicant.display_name,
                },
                "certificate_url": certificate_url,
            }
        )
    return {"items": result, "status": status_filter}


@app.post("/api/admin/chef-verifications/{verification_id}/decision")
def decide_chef_verification(
    verification_id: int,
    payload: ChefVerificationDecisionRequest,
    admin_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db),
    email_sender: SmtpEmailSender = Depends(get_email_sender),
) -> dict:
    application = (
        db.query(ChefVerification)
        .filter(ChefVerification.id == verification_id)
        .with_for_update()
        .first()
    )
    if application is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chef application not found")
    if application.status != "pending_review":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Chef application has already been decided")

    applicant = db.query(User).filter(User.id == application.user_id).first()
    if applicant is None or applicant.role != "regular" or applicant.chef_status != "pending_review":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Chef application is not in a reviewable state")

    now = datetime.now(timezone.utc)
    outcome = "active" if payload.decision == "approve" else "rejected"
    try:
        application_updated = (
            db.query(ChefVerification)
            .filter(
                ChefVerification.id == verification_id,
                ChefVerification.status == "pending_review",
            )
            .update(
                {
                    ChefVerification.status: outcome,
                    ChefVerification.reviewed_by_user_id: admin_user.id,
                    ChefVerification.reviewed_at: now,
                    ChefVerification.rationale: payload.rationale,
                },
                synchronize_session=False,
            )
        )
        if application_updated != 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chef application has already been decided",
            )

        applicant_updates = {User.chef_status: outcome}
        if payload.decision == "approve":
            applicant_updates[User.role] = "chef"
        user_updated = (
            db.query(User)
            .filter(
                User.id == applicant.id,
                User.role == "regular",
                User.chef_status == "pending_review",
            )
            .update(applicant_updates, synchronize_session=False)
        )
        if user_updated != 1:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Chef application is not in a reviewable state",
            )
        db.commit()
    except HTTPException:
        db.rollback()
        raise
    except Exception:
        db.rollback()
        logger.exception("Could not save decision for Chef application %s", verification_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not save Chef application decision",
        ) from None

    approved = payload.decision == "approve"
    try:
        email_sender.send(
            TransactionalEmail(
                recipient=applicant.email,
                subject=(
                    "Your Chef application was approved"
                    if approved
                    else "Your Chef application was not approved"
                ),
                text_body=(
                    f"Hello {applicant.display_name},\n\n"
                    + (
                        "Your Chef application has been approved. Your account is now an active Chef account, "
                        "and you can publish recipes."
                        if approved
                        else "Your Chef application has not been approved. Your account remains a regular user "
                        "and does not have Chef publishing privileges."
                    )
                    + "\n"
                ),
            )
        )
    except EmailDeliveryError:
        logger.warning(
            "Applicant decision notification delivery failed for Chef application %s",
            verification_id,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Chef application decision was recorded, but applicant notification delivery failed"
            ),
        ) from None

    return {
        "id": verification_id,
        "decision": payload.decision,
        "status": outcome,
        "reviewed_by_user_id": admin_user.id,
        "reviewed_at": now.isoformat(),
        "rationale": payload.rationale,
        "notification_status": "sent",
    }


@app.post("/api/chefs/me/email-verification", status_code=status.HTTP_202_ACCEPTED)
def request_chef_email_verification(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    email_sender: SmtpEmailSender = Depends(get_email_sender),
) -> dict:
    if current_user.role != "regular":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only regular users can apply for Chef status")
    if current_user.email_verified:
        return {"message": "Email address is already verified", "email_verified": True}

    token = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    token_record = db.query(EmailVerificationToken).filter(EmailVerificationToken.user_id == current_user.id).first()
    if token_record is None:
        token_record = EmailVerificationToken(
            user_id=current_user.id,
            token_hash=token_digest(token),
            expires_at=now + EMAIL_VERIFICATION_TTL,
        )
        db.add(token_record)
    else:
        token_record.token_hash = token_digest(token)
        token_record.expires_at = now + EMAIL_VERIFICATION_TTL
        token_record.consumed_at = None

    current_user.chef_status = "unverified"
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not issue verification email") from None

    verification_link = (
        f"{settings.frontend_url.rstrip('/')}/verify-email?token={quote(token, safe='')}"
    )
    try:
        email_sender.send(
            TransactionalEmail(
                recipient=current_user.email,
                subject="Verify your email for Chef application",
                text_body=(
                    "Verify your email to continue your Chef application by opening this link:\n"
                    f"{verification_link}\n\n"
                    "The verification endpoint is GET /api/auth/verify-email?token=..."
                ),
            )
        )
    except EmailDeliveryError:
        token_record.consumed_at = datetime.now(timezone.utc)
        db.commit()
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Verification email could not be delivered") from None

    return {"message": "Verification email sent", "email_verified": False}


@app.get("/api/auth/verify-email")
def verify_email(token: str = "", db: Session = Depends(get_db)) -> dict:
    now = datetime.now(timezone.utc)
    token_record = (
        db.query(EmailVerificationToken)
        .filter(EmailVerificationToken.token_hash == token_digest(token))
        .with_for_update()
        .first()
    )
    expires_at = token_record.expires_at if token_record is not None else None
    if expires_at is not None and expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if (
        token_record is None
        or token_record.consumed_at is not None
        or expires_at is None
        or expires_at <= now
    ):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid or expired")

    consumed = (
        db.query(EmailVerificationToken)
        .filter(
            EmailVerificationToken.id == token_record.id,
            EmailVerificationToken.consumed_at.is_(None),
            EmailVerificationToken.expires_at > now,
        )
        .update({EmailVerificationToken.consumed_at: now}, synchronize_session=False)
    )
    if consumed != 1:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid or expired")

    user = db.query(User).filter(User.id == token_record.user_id).first()
    if user is None or user.is_system_account or user.role != "regular":
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is invalid or expired")
    user.email_verified = True
    user.chef_status = "email_verified"
    db.commit()
    return {"message": "Email address verified", "email_verified": True, "role": user.role}


@app.post("/api/chefs/certificate", status_code=status.HTTP_201_CREATED)
def submit_chef_certificate(
    certificate: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    storage: S3Storage = Depends(get_storage),
) -> dict:
    if current_user.role != "regular":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only regular users can apply for Chef status")
    if not current_user.email_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verify your email before uploading a certificate")
    if db.query(ChefVerification.id).filter(ChefVerification.user_id == current_user.id).first() is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A Chef application already exists")

    object_key = f"applications/{current_user.id}/{uuid4().hex}"
    try:
        storage.upload(
            StorageBucket.CHEF_CERTIFICATES,
            object_key,
            certificate.file,
            certificate.content_type or "",
        )
    except StorageValidationError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from None
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from None
    except StorageError:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Certificate storage is unavailable") from None
    finally:
        certificate.file.close()

    verification = ChefVerification(
        user_id=current_user.id,
        certificate_ref=f"{StorageBucket.CHEF_CERTIFICATES.value}/{object_key}",
        status="pending_review",
    )
    db.add(verification)
    current_user.chef_status = "pending_review"
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        try:
            storage.delete(StorageBucket.CHEF_CERTIFICATES, object_key)
        except StorageError:
            logger.error("Certificate cleanup failed after application conflict")
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A Chef application already exists") from None
    except Exception:
        db.rollback()
        try:
            storage.delete(StorageBucket.CHEF_CERTIFICATES, object_key)
        except StorageError:
            logger.error("Certificate cleanup failed after application persistence failure")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not save Chef application") from None

    return {"id": verification.id, "status": verification.status}


@app.get("/api/chefs/me/status")
def chef_application_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    application = db.query(ChefVerification).filter(ChefVerification.user_id == current_user.id).first()
    status_value = (
        application.status
        if application is not None
        else current_user.chef_status or ("email_verified" if current_user.email_verified else "unverified")
    )
    return {
        "email_verified": current_user.email_verified,
        "application_status": status_value,
        "role": current_user.role,
    }

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func
from ..database import get_session
from ..models.user import User
from ..schemas.auth import SignupRequest, SigninRequest, AuthResponse
from ..schemas.user import UserPublic
from ..auth.password import hash_password, verify_password, validate_password_strength
from ..auth.jwt import create_access_token
from ..auth.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(
    signup_data: SignupRequest,
    session: Session = Depends(get_session)
):
    """
    Create new user account.

    Args:
        signup_data: User signup information (email and password)
        session: Database session

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException: 400 if password weak, 409 if email exists
    """
    # Validate password strength
    is_valid, error_message = validate_password_strength(signup_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_message
        )

    # Check for duplicate email (case-insensitive)
    statement = select(User).where(
        func.lower(User.email) == signup_data.email.lower()
    )
    existing_user = session.exec(statement).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already exists"
        )

    # Hash password
    password_hash = hash_password(signup_data.password)

    # Create user
    user = User(
        email=signup_data.email.lower(),
        password_hash=password_hash
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    # Generate JWT token
    token = create_access_token(user.user_id, user.email)

    # Return response
    return AuthResponse(
        token=token,
        user=UserPublic.model_validate(user, from_attributes=True)
    )

@router.post("/signin", response_model=AuthResponse)
async def signin(
    signin_data: SigninRequest,
    session: Session = Depends(get_session)
):
    """
    Authenticate existing user.

    Args:
        signin_data: User signin information (email and password)
        session: Database session

    Returns:
        AuthResponse: JWT token and user information

    Raises:
        HTTPException: 401 if credentials invalid
    """
    # Query user by email (case-insensitive)
    statement = select(User).where(
        func.lower(User.email) == signin_data.email.lower()
    )
    user = session.exec(statement).first()

    # Always verify password even if user not found (timing attack prevention)
    if not user:
        # Use dummy hash to maintain constant time - proper bcrypt format
        verify_password(signin_data.password, "$2b$12$5aZqCkedUxLpC6Pn3ozRhO.76rrhbOm48WCpdXljFlk7YUAB7Nw5K")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Verify password
    if not verify_password(signin_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    # Generate JWT token
    token = create_access_token(user.user_id, user.email)

    # Return response
    return AuthResponse(
        token=token,
        user=UserPublic.model_validate(user, from_attributes=True)
    )

@router.get("/me", response_model=UserPublic)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information.

    Args:
        current_user: Authenticated user from JWT token

    Returns:
        UserPublic: Current user information
    """
    return UserPublic(
        user_id=current_user.user_id,
        email=current_user.email,
        created_at=current_user.created_at
    )

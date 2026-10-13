from datetime import datetime, timezone
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError, ConflictError
from app.core.security import hash_password, verify_dummy_password, verify_password
from app.models.user import User, UserPreferences
from app.schemas.auth import UserLogin
from app.schemas.user import UserCreate


async def register_user(db: AsyncSession, user_in: UserCreate) -> User:
    """Registers a new User with password hashing and default preferences.
    
    Enforces case-insensitive uniqueness on username and email.
    """
    clean_username = user_in.username.strip().lower()
    clean_email = user_in.email.strip().lower()

    # Check for existing username
    username_check = await db.execute(
        select(User).where(func.lower(User.username) == clean_username)
    )
    if username_check.scalar_one_or_none() is not None:
        raise ConflictError("Username is already taken")

    # Check for existing email
    email_check = await db.execute(
        select(User).where(func.lower(User.email) == clean_email)
    )
    if email_check.scalar_one_or_none() is not None:
        raise ConflictError("Email address is already registered")

    # Hash password with bcrypt cost 12
    hashed_pw = hash_password(user_in.password)

    import uuid
    now = datetime.now(timezone.utc)
    user = User(
        id=uuid.uuid4(),
        username=user_in.username.strip(),
        email=user_in.email.strip().lower(),
        display_name=user_in.display_name.strip(),
        password_hash=hashed_pw,
        email_verified=False,
        created_at=now,
    )
    db.add(user)
    await db.flush()

    # Provision default user preferences
    prefs = UserPreferences(
        user_id=user.id,
        theme="backlund_dark",
        preferred_deck_style="victorian_anime",
        default_spread="three_card",
    )
    db.add(prefs)

    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, login_in: UserLogin) -> User:
    """Authenticates a user by username or email.
    
    Mitigates user enumeration and timing attacks using dummy bcrypt verification.
    """
    identifier = login_in.username_or_email.strip().lower()
    stmt = select(User).where(
        or_(
            func.lower(User.username) == identifier,
            func.lower(User.email) == identifier,
        )
    )
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()

    if user is None:
        verify_dummy_password(login_in.password)
        raise AuthenticationError("Invalid username or password")

    if not verify_password(login_in.password, user.password_hash):
        raise AuthenticationError("Invalid username or password")

    # Update last login timestamp
    user.last_login = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(user)
    return user

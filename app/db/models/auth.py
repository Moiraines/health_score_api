"""Authentication and session management models."""
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Type, TypeVar, cast
import uuid

from sqlalchemy import (
    Column, Integer, String, Boolean, DateTime, ForeignKey, Text, 
    Index, func, event, DDL
)
from sqlalchemy.dialects.postgresql import INET, UUID as PG_UUID, JSONB
from sqlalchemy.orm import relationship, Session
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.ext.mutable import MutableDict

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_refresh_token
from ..base import Base
from sqlalchemy import PrimaryKeyConstraint

# Type variable for generic model operations
ModelType = TypeVar("ModelType", bound=Base)

class UserSession(Base):
    """Tracks user sessions for authentication and security."""
    
    __tablename__ = 'user_sessions'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'user_id', name='pk_user_sessions'),
        Index('ix_user_sessions_user_id', 'user_id'),
        Index('ix_user_sessions_session_id', 'session_id', 'user_id', unique=True),
        Index('ix_user_sessions_refresh_token', 'refresh_token', 'user_id', unique=True),
        {
            'comment': 'Tracks active user sessions for authentication',
            'postgresql_partition_by': 'HASH (user_id)'  # For potential partitioning
        }
    )
    
    # ===== Core Fields =====
    id = Column(
        Integer, 
        primary_key=False,
        index=True,
        comment='Primary key',
        autoincrement=True
    )
    
    # ===== Authentication =====
    user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Reference to the user this session belongs to'
    )
    session_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment='Unique session identifier (JTI claim)'
    )
    refresh_token = Column(
        String(255),
        nullable=True,
        index=True,
        comment='Hashed refresh token (for refresh token rotation)'
    )
    
    # ===== Session Info =====
    user_agent = Column(
        Text,
        nullable=True,
        comment='User agent string from the client'
    )
    ip_address = Column(
        String(45),
        nullable=True,
        comment='IP address of the client'
    )
    location = Column(
        JSONB,
        nullable=True,
        comment='Geolocation data derived from IP address'
    )
    device_info = Column(
        JSONB,
        nullable=True,
        comment='Device information (OS, browser, etc.)'
    )
    
    # ===== Security =====
    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        server_default='false',
        comment='Whether the session has been revoked'
    )
    last_used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='When the session was last used'
    )
    
    # ===== Expiration =====
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment='When the session was created'
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='When the session expires'
    )
    refresh_expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment='When the refresh token expires'
    )
    
    # ===== Relationships =====
    user = relationship("User", back_populates="sessions")
    
    # ===== Properties =====
    @property
    def is_active(self) -> bool:
        """Check if the session is still active."""
        return not self.is_revoked and self.expires_at > datetime.utcnow()
    
    @property
    def can_refresh(self) -> bool:
        """Check if the session can be refreshed."""
        return (self.refresh_token is not None and 
                self.refresh_expires_at is not None and
                self.refresh_expires_at > datetime.utcnow())
    
    # ===== Methods =====
    def revoke(self, db: Session) -> None:
        """Revoke this session."""
        self.is_revoked = True
        self.refresh_token = None
        db.add(self)
        db.commit()
    
    def update_last_used(self, db: Session) -> None:
        """Update the last used timestamp."""
        self.last_used_at = func.now()
        db.add(self)
        db.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'session_id': self.session_id,
            'user_id': self.user_id,
            'user_agent': self.user_agent,
            'ip_address': self.ip_address,
            'location': self.location,
            'device_info': self.device_info,
            'is_revoked': self.is_revoked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'refresh_expires_at': self.refresh_expires_at.isoformat() if self.refresh_expires_at else None,
            'is_active': self.is_active,
            'can_refresh': self.can_refresh
        }
    
    # ===== Class Methods =====
    @classmethod
    def create(
        cls,
        db: Session,
        user_id: int,
        session_id: str,
        refresh_token: str,
        user_agent: Optional[str] = None,
        ip_address: Optional[str] = None,
        location: Optional[Dict[str, Any]] = None,
        device_info: Optional[Dict[str, Any]] = None,
        expires_in: int = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_expires_in: int = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    ) -> 'UserSession':
        """Create a new user session."""
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=expires_in)
        refresh_expires_at = now + timedelta(seconds=refresh_expires_in)
        
        session = cls(
            user_id=user_id,
            session_id=session_id,
            refresh_token=create_refresh_token({"token": refresh_token}),
            user_agent=user_agent,
            ip_address=ip_address,
            location=location,
            device_info=device_info,
            expires_at=expires_at,
            refresh_expires_at=refresh_expires_at,
            last_used_at=now
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @classmethod
    def get_active_by_session_id(
        cls, 
        db: Session, 
        session_id: str
    ) -> Optional['UserSession']:
        """Get an active session by session ID."""
        return db.query(cls).filter(
            cls.session_id == session_id,
            cls.is_revoked == False,
            cls.expires_at > func.now()
        ).first()

    @classmethod
    def get_by_refresh_token(
            cls,
            db: Session,
            refresh_token: str,
    ) -> Optional["UserSession"]:
        """Find session that owns this refresh token."""
        incoming_payload = verify_refresh_token(refresh_token)
        if not incoming_payload:
            return None

        sessions = (
            db.query(cls)
            .filter(
                cls.refresh_token.isnot(None),
                cls.is_revoked.is_(False),
                cls.refresh_expires_at > func.now(),
            )
            .all()
        )

        incoming_token_claim = incoming_payload.get("token")

        for session in sessions:
            stored_payload = verify_refresh_token(session.refresh_token)
            if stored_payload and stored_payload.get("token") == incoming_token_claim:
                return session

        return None

    @classmethod
    def revoke_all_for_user(
        cls,
        db: Session,
        user_id: int,
        exclude_session_id: Optional[str] = None
    ) -> int:
        """Revoke all sessions for a user, optionally excluding one."""
        query = db.query(cls).filter(
            cls.user_id == user_id,
            cls.is_revoked == False
        )
        
        if exclude_session_id:
            query = query.filter(cls.session_id != exclude_session_id)
        
        sessions = query.all()
        count = len(sessions)
        
        for session in sessions:
            session.is_revoked = True
            session.refresh_token = None
            db.add(session)
        
        if count > 0:
            db.commit()
            
        return count
    
    @classmethod
    def cleanup_expired(cls, db: Session) -> int:
        """Clean up expired sessions."""
        # Revoke sessions where both access and refresh tokens have expired
        result = db.query(cls).filter(
            (cls.expires_at <= func.now()) | 
            ((cls.refresh_expires_at.isnot(None)) & (cls.refresh_expires_at <= func.now()))
        ).delete(synchronize_session=False)
        
        db.commit()
        return result


class RefreshToken(Base):
    """Tracks refresh tokens for token rotation and revocation."""
    
    __tablename__ = 'refresh_tokens'
    __table_args__ = (
        PrimaryKeyConstraint('id', 'user_id'),
        Index('ix_refresh_tokens_user_id', 'user_id'),
        Index('ix_refresh_tokens_token', 'token', 'user_id', unique=True),
        Index('ix_refresh_tokens_parent_token', 'parent_token'),
        {
            'comment': 'Tracks refresh tokens for token rotation',
            'postgresql_partition_by': 'HASH (user_id)'  # For potential partitioning
        }
    )
    
    # ===== Core Fields =====
    id = Column(
        Integer, 
        nullable=False,
        index=True,
        comment='Primary key',
        autoincrement=True
    )
    
    # ===== Token Info =====
    token = Column(
        String(255),
        nullable=False,
        index=True,
        comment='Hashed refresh token'
    )
    parent_token = Column(
        String(255),
        nullable=True,
        index=True,
        comment='Hashed parent token (for token rotation)'
    )
    token_family = Column(
        String(64),
        nullable=False,
        index=True,
        comment='Token family identifier (for token family rotation)'
    )
    
    # ===== User Info =====
    user_id = Column(
        Integer, 
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        index=True,
        comment='Reference to the user this token belongs to'
    )
    
    # ===== Security =====
    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        server_default='false',
        comment='Whether the token has been revoked'
    )
    
    # ===== Expiration =====
    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        comment='When the token was created'
    )
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        comment='When the token expires'
    )
    
    # ===== Relationships =====
    user = relationship("User", back_populates="refresh_tokens")
    
    # ===== Properties =====
    @property
    def is_active(self) -> bool:
        """Check if the token is still active."""
        return not self.is_revoked and self.expires_at > datetime.utcnow()
    
    # ===== Methods =====
    def revoke(self, db: Session) -> None:
        """Revoke this token."""
        self.is_revoked = True
        db.add(self)
        db.commit()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert token to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'token_family': self.token_family,
            'is_revoked': self.is_revoked,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_active': self.is_active
        }
    
    # ===== Class Methods =====
    @classmethod
    def create(
        cls,
        db: Session,
        user_id: int,
        token: str,
        parent_token: Optional[str] = None,
        expires_in: int = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
    ) -> 'RefreshToken':
        """Create a new refresh token."""
        now = datetime.utcnow()
        expires_at = now + timedelta(seconds=expires_in)
        
        # Generate a token family ID (first token in the family)
        token_family = str(uuid.uuid4())
        
        # If this is a child token, get the family from the parent
        if parent_token:
            parent = cls.get_by_token(db, parent_token)
            if parent and not parent.is_revoked:
                token_family = parent.token_family
                parent.revoke(db)  # Revoke the parent token
        
        # Create the new token
        refresh_token = cls(
            token=create_refresh_token({"token": token}),
            parent_token=create_refresh_token({"parent_token": parent_token}) if parent_token else None,
            token_family=token_family,
            user_id=user_id,
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        db.commit()
        db.refresh(refresh_token)
        return refresh_token

    @classmethod
    def get_by_token(
            cls,
            db: Session,
            token: str
    ) -> Optional["RefreshToken"]:
        incoming_payload = verify_refresh_token(token)
        if not incoming_payload:
            return None
        incoming_claim = incoming_payload.get("token")

        tokens = (
            db.query(cls)
            .filter(
                cls.is_revoked.is_(False),
                cls.expires_at > func.now(),
            )
            .all()
        )

        for t in tokens:
            stored_payload = verify_refresh_token(t.token)
            if stored_payload and stored_payload.get("token") == incoming_claim:
                return t

        return None

    @classmethod
    def revoke_family(
        cls,
        db: Session,
        token_family: str
    ) -> int:
        """Revoke all tokens in a token family."""
        tokens = db.query(cls).filter(
            cls.token_family == token_family,
            cls.is_revoked == False
        ).all()
        
        count = len(tokens)
        for token in tokens:
            token.is_revoked = True
            db.add(token)
        
        if count > 0:
            db.commit()
            
        return count
    
    @classmethod
    def cleanup_expired(cls, db: Session) -> int:
        """Clean up expired refresh tokens."""
        result = db.query(cls).filter(
            cls.expires_at <= func.now()
        ).delete(synchronize_session=False)
        
        db.commit()
        return result


# Create a function to clean up expired sessions and tokens
def cleanup_auth_tables() -> None:
    """Clean up expired sessions and tokens."""
    from ..session import SessionLocal
    
    db = SessionLocal()
    try:
        # Clean up expired sessions
        expired_sessions = UserSession.cleanup_expired(db)
        
        # Clean up expired refresh tokens
        expired_tokens = RefreshToken.cleanup_expired(db)
        
        print(f"Cleaned up {expired_sessions} expired sessions and {expired_tokens} expired tokens")
    except Exception as e:
        print(f"Error cleaning up auth tables: {e}")
        db.rollback()
    finally:
        db.close()


# Set up a periodic task to clean up expired sessions and tokens
# This would typically be set up in your task queue (e.g., Celery)
# Example for Celery:
# @app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # ⬇ коментираш един ред и IDE млъква
    # sender.add_periodic_task(3600.0, cleanup_auth_tasks.s(), name="cleanup-auth-tables")
    pass

# Example Celery task
# @app.task
# def cleanup_auth_tasks():
#     cleanup_auth_tables()

# For testing, you can manually trigger the cleanup
if __name__ == "__main__":
    cleanup_auth_tables()

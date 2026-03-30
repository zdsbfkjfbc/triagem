import bcrypt
import jwt
import os
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from ..database.models import User
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "fallback_secret_for_dev_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 8

class AuthManager:
    """Gerenciador de autenticação, hashing de senhas e tokens JWT."""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Gera um hash seguro da senha."""
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password: str, password_hash: str) -> bool:
        """Verifica se a senha coincide com o hash armazenado."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Gera um Token JWT para a sessão do usuário."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> Optional[dict]:
        """Decodifica e valida um Token JWT."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.PyJWTError:
            return None

    @staticmethod
    def authenticate_user(session: Session, username: str, password: str) -> Optional[User]:
        """Autentica o usuário e retorna o objeto User se bem-sucedido."""
        user = session.query(User).filter(User.username == username).first() # type: ignore
        if user and AuthManager.verify_password(password, user.password_hash):
            return user
        return None

    @staticmethod
    def create_user(session: Session, username: str, password: str, role: str = 'recruiter') -> User:
        """Cria um novo usuário com senha hashed."""
        password_hash = AuthManager.hash_password(password)
        new_user = User(username=username, password_hash=password_hash, role=role)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

from passlib.context import CryptContext

# Passlib  Bcrypt Hashing Algorithm  Config 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """ලබාදෙන plain password එක hash කර ආපසු ලබාදෙයි."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """User ලබාදෙන password එක සහ Database එකේ ඇති hashed password එක ගැලපේදැයි බලයි."""
    return pwd_context.verify(plain_password, hashed_password)
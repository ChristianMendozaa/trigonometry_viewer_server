from fastapi import Header
from fastapi import APIRouter, HTTPException, status
from app.services.auth_service import AuthService
from app.schemas.user_schema import RegisterRequest, UserResponse
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: RegisterRequest):
    new_user = AuthService.create_user(user.email, user.password, user.name, user.role)
    return new_user

@router.get("/me", response_model=UserResponse)
async def get_me(authorization: str = Header(None)):
    print()
    """
    Obtiene la información del usuario autenticado a partir del token JWT de Firebase.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado",
        )

    token = authorization.split(" ")[1]  # Extraer solo el token JWT
    user: User = AuthService.verify_token(token)
    return user
from fastapi import APIRouter, HTTPException, Header, status
from app.services.auth_service import AuthService
from app.services.series_service import SeriesService
from app.schemas.series_schema import SeriesRequest, SeriesResponseh
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/series", tags=["Series"])

@router.post("/save", response_model=SeriesResponseh)
async def save_series(series: SeriesRequest, authorization: str = Header(None)):
    """
    Guarda una serie trigonométrica generada por un usuario en Firestore.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)
    logger.info(f"🔹 Usuario autenticado: {user.id}")

    saved_series = SeriesService.save_series(user.id, series)
    return saved_series

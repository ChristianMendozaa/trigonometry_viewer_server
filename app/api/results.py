from fastapi import APIRouter, HTTPException, Header, status
from app.services.auth_service import AuthService
from app.services.results_service import ResultsService
from app.schemas.series_schema import SaveResultsRequest, SeriesResponse
from app.core.firebase import db
from datetime import datetime

router = APIRouter(prefix="/results", tags=["Results"])

@router.get("/saved")
async def get_saved_results(authorization: str = Header(None)):
    """
    Obtiene los resultados guardados del usuario autenticado,
    incluyendo la información de la serie asociada.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)

    try:
        # 🔹 Obtener los resultados guardados del usuario
        results_ref = db.collection("series_results").where("uid", "==", user.id).stream()
        results = [doc.to_dict() for doc in results_ref]

        if not results:
            return []

        saved_series = []

        # 🔹 Obtener información completa de cada serie desde `series_history`
        for result in results:
            series_id = result.get("seriesId")

            if not series_id:
                continue  # Si no hay un ID válido, omitir este resultado

            series_doc = db.collection("series_history").document(series_id).get()

            if not series_doc.exists:
                continue  # Si la serie no existe, omitirla

            series_data = series_doc.to_dict()

            # 🔹 Construir la respuesta combinando resultado guardado y la serie
            saved_series.append({
                "resultId": result.get("id"),
                "seriesId": series_id,
                "dateSaved": result.get("date"),
                "userId": result.get("uid"),
                "series": {
                    "id": series_id,
                    **series_data
                }
            })

        return saved_series
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener resultados guardados: {str(e)}")

@router.post("/save")
async def save_results(request: SaveResultsRequest):
    """
    Guarda la referencia de una serie generada por el usuario en `series_results`
    """
    try:
        results_data = {
            "uid": request.uid,  # 🔹 Guardar UID desde el body
            "seriesId": request.seriesId,
            "date": datetime.utcnow(),
        }

        # 🔥 Guardar solo `uid` y `seriesId`
        doc_ref = db.collection("series_results").add(results_data)

        # Obtener el ID generado por Firestore
        result_id = doc_ref[1].id
        results_data["id"] = result_id

        # Actualizar el documento con el ID generado
        db.collection("series_results").document(result_id).update({"id": result_id})

        return {"message": "Resultados guardados", "id": result_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al guardar los resultados: {str(e)}")

@router.delete("/delete/{result_id}")
async def delete_result(result_id: str, authorization: str = Header(None)):
    """
    Elimina un resultado guardado por el usuario autenticado.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)

    try:
        result_ref = db.collection("series_results").document(result_id)
        result = result_ref.get()

        if not result.exists:
            raise HTTPException(status_code=404, detail="Resultado no encontrado")

        result_data = result.to_dict()
        if result_data["uid"] != user.id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar este resultado")

        result_ref.delete()
        return {"message": "Resultado eliminado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar resultado: {str(e)}")
    
@router.get("/history")
async def get_history(authorization: str = Header(None)):
    """
    Obtiene el historial de series trigonométricas del usuario autenticado.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)

    try:
        history_ref = db.collection("series_history").where("uid", "==", user.id).stream()
        history = [
            {
                "id": doc.id,
                **doc.to_dict()
            }
            for doc in history_ref
        ]
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener historial: {str(e)}")
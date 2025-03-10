from firebase_admin import firestore
from fastapi import HTTPException
from app.core.firebase import db
from app.schemas.series_schema import SeriesRequest, SeriesResponseh
from datetime import datetime

class SeriesService:

    @staticmethod
    def save_series(uid: str, series: SeriesRequest) -> SeriesResponseh:
        """
        Guarda una serie trigonométrica generada por un usuario en `series_history`,
        permitiendo que Firestore asigne automáticamente el ID del documento.
        """
        try:
            series_data = {
                "uid": uid,
                "date": datetime.utcnow(),
                "type": series.type,
                "points": series.points,
                "avgError": series.avgError,
                "maxError": series.maxError,
                "data": series.data.dict()
            }

            # 🔥 Agregar documento sin ID manual, Firestore generará el ID automáticamente
            doc_ref = db.collection("series_history").add(series_data)

            # Obtener el ID generado por Firestore
            series_id = doc_ref[1].id
            db.collection("series_history").document(series_id).update({"id": series_id})

            # 🔹 Retornar correctamente la respuesta incluyendo el ID
            return SeriesResponseh(
                id=series_id,  # ✅ Solo se pasa aquí para evitar conflictos
                uid=uid,
                date=series_data["date"],
                type=series_data["type"],
                points=series_data["points"],
                avgError=series_data["avgError"],
                maxError=series_data["maxError"],
                data=series_data["data"]
            )

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al guardar la serie: {str(e)}")

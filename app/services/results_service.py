from firebase_admin import firestore
from fastapi import HTTPException
from app.core.firebase import db
from datetime import datetime

class ResultsService:

    @staticmethod
    def save_results(uid: str, series_id: str):
        """
        Guarda la referencia de los resultados en `series_results`, 
        solo almacenando el ID del usuario y el ID de la serie generada.
        """
        try:
            results_data = {
                "uid": uid,
                "seriesId": series_id,
                "date": datetime.utcnow(),
            }

            # 🔥 Agregar el documento sin ID manual, Firestore generará el ID automáticamente
            doc_ref = db.collection("series_results").add(results_data)

            # Obtener el ID generado por Firestore
            result_id = doc_ref[1].id
            results_data["id"] = result_id

            # Actualizar el documento con el ID generado
            db.collection("series_results").document(result_id).update({"id": result_id})

            return results_data
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al guardar los resultados: {str(e)}")

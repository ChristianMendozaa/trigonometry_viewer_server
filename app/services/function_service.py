from fastapi import HTTPException
from app.core.firebase import db
from datetime import datetime

class FunctionsService:

    @staticmethod
    def save_function(uid: str, name: str, expression: str):
        """
        Guarda una función personalizada en Firestore.
        """
        try:
            function_data = {
                "uid": uid,
                "name": name,
                "expression": expression,
                "date": datetime.utcnow().isoformat(),  # 🔹 Convertir datetime a string
            }

            # 🔥 Agregar el documento sin ID manual, Firestore generará el ID automáticamente
            doc_ref = db.collection("custom_functions").add(function_data)

            # Obtener el ID generado por Firestore
            function_id = doc_ref[1].id
            function_data["id"] = function_id

            # Actualizar el documento con el ID generado
            db.collection("custom_functions").document(function_id).update({"id": function_id})

            return function_data  # 🔹 Ahora `date` está en formato string
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error al guardar la función: {str(e)}")

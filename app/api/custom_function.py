from fastapi import APIRouter, HTTPException, Header, status
from datetime import datetime
from app.core.firebase import db
from app.services.auth_service import AuthService
from app.schemas.custom_function_schema import CustomFunctionRequest, CustomFunctionResponse

router = APIRouter(prefix="/functions", tags=["Custom Functions"])

@router.post("/save", response_model=CustomFunctionResponse)
async def save_function(request: CustomFunctionRequest, authorization: str = Header(None)):
    """
    Guarda una función personalizada en Firestore.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)

    try:
        function_data = {
            "uid": user.id,
            "name": request.name,
            "expression": request.expression,
            "date": datetime.utcnow().isoformat(),
        }

        # 🔥 Guardar la función personalizada en Firestore
        doc_ref = db.collection("custom_functions").add(function_data)
        function_id = doc_ref[1].id

        # Actualizar el documento con el ID generado
        db.collection("custom_functions").document(function_id).update({"id": function_id})

        return {**function_data, "id": function_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error al guardar la función: {str(e)}")


@router.get("/saved")
async def get_saved_functions(authorization: str = Header(None)):
    """
    Obtiene las funciones personalizadas guardadas por el usuario autenticado.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)

    try:
        functions_ref = db.collection("custom_functions").where("uid", "==", user.id).stream()
        functions = [
            {
                "id": doc.id,
                "name": doc.to_dict().get("name", ""),
                "expression": doc.to_dict().get("expression", ""),
                "createdAt": doc.to_dict().get("date", "").isoformat() 
                if isinstance(doc.to_dict().get("date"), datetime) 
                else doc.to_dict().get("date", ""),
            }
            for doc in functions_ref
        ]
        return functions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener funciones personalizadas: {str(e)}")


@router.delete("/delete/{function_id}")
async def delete_function(function_id: str, authorization: str = Header(None)):
    """
    Elimina una función personalizada guardada por el usuario autenticado.
    """
    if not authorization or "Bearer " not in authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización faltante o mal formateado"
        )

    token = authorization.split(" ")[1]
    user = AuthService.verify_token(token)

    try:
        function_ref = db.collection("custom_functions").document(function_id)
        function = function_ref.get()

        if not function.exists:
            raise HTTPException(status_code=404, detail="Función no encontrada")

        function_data = function.to_dict()
        if function_data["uid"] != user.id:
            raise HTTPException(status_code=403, detail="No tienes permiso para eliminar esta función")

        function_ref.delete()
        return {"message": "Función eliminada correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al eliminar función: {str(e)}")
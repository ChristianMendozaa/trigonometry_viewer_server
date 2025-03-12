from firebase_admin import auth as firebase_auth, firestore
from firebase_admin.auth import UserRecord
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.core.firebase import db  # 🔥 Importa Firestore
import traceback
import time
import firebase_admin
from google.cloud.firestore import Increment, ArrayUnion
from datetime import datetime, timedelta

class AuthService:

    @staticmethod
    def verify_token(token: str) -> User:
        """
        Verifica el token JWT de Firebase y maneja el error "Token used too early" con tolerancia de tiempo.
        """
        max_retries = 2  # Número de intentos en caso de fallo
        retry_delay = 1   # Segundos de espera antes de reintentar
        clock_skew_seconds = 10  # Ajuste de tolerancia de tiempo

        for attempt in range(max_retries):
            try:
                # 🔹 Ajustar la tolerancia de tiempo al verificar el token
                decoded_token = firebase_auth.verify_id_token(token, clock_skew_seconds=clock_skew_seconds)
                uid = decoded_token["uid"]

                # Obtiene información básica del usuario desde Firebase Authentication
                user_record: UserRecord = firebase_auth.get_user(uid)

                # 🔥 Obtiene el documento del usuario en Firestore
                doc_ref = db.collection("users").document(uid).get()
                
                if not doc_ref.exists:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No se encontró información de usuario en Firestore. UID: {uid}"
                    )

                # Convertimos el documento a dict para extraer la info
                user_data = doc_ref.to_dict()
                role = user_data.get("role", "user")

                # Retornamos un objeto de tipo User
                return User(
                    id=user_record.uid,
                    name=user_record.display_name or "Unknown",
                    email=user_record.email,
                    role=UserRole(role)
                )

            except firebase_admin._auth_utils.InvalidIdTokenError as e:
                error_message = str(e)
                if "Token used too early" in error_message:
                    print(f"⚠️ Token usado demasiado temprano, intento {attempt + 1}/{max_retries}")
                    traceback.print_exc()

                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)  # Espera antes de reintentar
                        continue

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Error de autenticación: {error_message}"
                )

            except Exception as e:
                print(f"❌ Error desconocido al verificar el token: {str(e)}")
                traceback.print_exc()
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Error al verificar el token: {str(e)}"
                )

    @staticmethod
    def create_user(email: str, password: str, name: str, role: str = "user") -> User:
        """
        Crea un usuario en Firebase Authentication y lo guarda en Firestore.
        Además, actualiza el contador total de usuarios y agrega el usuario al array "users" en `dashboard/stats`.
        """
        try:
            # 🔥 Crear usuario en Firebase Authentication
            user_record = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            
            # 🔥 Asignar rol (opcional)
            firebase_auth.set_custom_user_claims(user_record.uid, {"role": role})

            # 🔥 Obtener la fecha y hora actual
            current_time = datetime.utcnow()
               
            # 🔥 Datos del usuario para Firestore
            user_data = {
                "id": user_record.uid,
                "name": name,
                "email": email,
                "role": role,
                "total_series_generated": 0,
                "avg_error": 0.0,
                "last_activity": datetime.utcnow()
            }
            db.collection("users").document(user_record.uid).set(user_data)
            
            # 🔥 Referencia al documento `dashboard/stats`
            dashboard_ref = db.collection("dashboard").document("stats")
            dashboard_snapshot = dashboard_ref.get()

            if dashboard_snapshot.exists:
                dashboard_data = dashboard_snapshot.to_dict()
                
                # Obtener el total de usuarios anterior (si existe)
                last_users_count = dashboard_data.get("total_users", 0)
                previous_users_count = dashboard_data.get("users_yesterday", last_users_count)
                daily_growth = last_users_count + 1 - previous_users_count  # Diferencia con el día anterior

                # 🔥 Actualizar `dashboard/stats`
                dashboard_ref.update({
                    "total_users": Increment(1),
                    "users": ArrayUnion([user_data]),
                    "users_yesterday": last_users_count,  # Guardar total de ayer
                    "total_users_growth": daily_growth  # Agregar campo de crecimiento diario
                })
            else:
                # Si no existe, crearlo con valores iniciales
                dashboard_ref.set({
                    "total_users": 1,
                    "users": [user_data],
                    "users_yesterday": 0,  # Inicializar el total de ayer
                    "total_users_growth": 1
                })

            return User(
                id=user_record.uid,
                name=name,
                email=email,
                role=UserRole(role)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error al crear usuario en Firebase: {str(e)}"
            )
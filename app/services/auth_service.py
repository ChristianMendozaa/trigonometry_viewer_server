from firebase_admin import auth as firebase_auth, firestore
from firebase_admin.auth import UserRecord
from fastapi import HTTPException, status
from app.models.user import User, UserRole
from app.core.firebase import db  # 🔥 Importa Firestore

class AuthService:

    @staticmethod
    def verify_token(token: str) -> User:
        """
        Verifica el token JWT de Firebase y devuelve los datos del usuario autenticado.
        """
        try:
            decoded_token = firebase_auth.verify_id_token(token)
            user_record: UserRecord = firebase_auth.get_user(decoded_token['uid'])

            role = user_record.custom_claims.get("role", "user")  # Obtener rol (si existe)

            return User(
                id=user_record.uid,
                name=user_record.display_name or "Unknown",
                email=user_record.email,
                role=UserRole(role)
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado."
            )

    @staticmethod
    def create_user(email: str, password: str, name: str, role: str = "user") -> User:
        """
        Crea un usuario en Firebase Authentication y lo guarda en Firestore.
        """
        try:
            # 🔥 Crear usuario en Firebase Authentication
            user_record: UserRecord = firebase_auth.create_user(
                email=email,
                password=password,
                display_name=name
            )
            firebase_auth.set_custom_user_claims(user_record.uid, {"role": role})

            # 🔥 Guardar en Firestore en la colección "users"
            user_data = {
                "id": user_record.uid,
                "name": name,
                "email": email,
                "role": role,
                "created_at": firestore.SERVER_TIMESTAMP
            }
            db.collection("users").document(user_record.uid).set(user_data)

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

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
        Obteniendo el rol desde la colección "users" en Firestore.
        """
        try:
            # Verifica el token en Firebase
            decoded_token = firebase_auth.verify_id_token(token)
            uid = decoded_token["uid"]

            # Obtiene información básica del usuario desde Firebase Authentication
            user_record: UserRecord = firebase_auth.get_user(uid)

            # 🔥 Obtiene el documento del usuario en la colección "users"
            doc_ref = db.collection("users").document(uid).get()
            
            if not doc_ref.exists:
                # Si no existe el documento en Firestore, 
                # se puede usar un rol por defecto o lanzar error según tus necesidades
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontró información de usuario en Firestore."
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
            
            # Opcional: si no usarás el custom_claim para nada, puedes omitirlo
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

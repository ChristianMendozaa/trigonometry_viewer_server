from firebase_admin import firestore
from fastapi import HTTPException
from app.core.firebase import db
from app.schemas.series_schema import SeriesRequest, SeriesResponseh
from datetime import datetime, timedelta
from google.cloud.firestore import Increment
import math

class SeriesService:

    @staticmethod
    def save_series(uid: str, series: SeriesRequest) -> SeriesResponseh:
        """
        Guarda una serie trigonométrica generada por un usuario en `series_history`,
        actualiza toda la información necesaria en `users` y `dashboard/stats`:
          - avg_error, total_series_generated, last_activity del usuario
          - total_series_generated, global_avg_error, series_yesterday, error_yesterday, 
            series_growth, error_change en el dashboard
          - series_stats (estadísticas por tipo de serie)
          - top_performing_users (3 usuarios con menor avg_error)
          - high_error_series (3 tipos de series con mayor avg_error)
          - array de users en dashboard con la info actualizada del usuario
        """
        try:
            current_time = datetime.utcnow()  # Obtener la fecha/hora actual

            # 1) Guardar la nueva serie en `series_history`
            series_data = {
                "uid": uid,
                "date": current_time,
                "type": series.type,
                "points": series.points,
                "avgError": series.avgError,
                "maxError": series.maxError,
                "data": series.data.dict()
            }
            doc_ref = db.collection("series_history").add(series_data)

            # Obtener el ID generado por Firestore
            series_id = doc_ref[1].id
            db.collection("series_history").document(series_id).update({"id": series_id})

            # 2) Actualizar info del usuario en la colección `users`
            user_ref = db.collection("users").document(uid)
            user_snapshot = user_ref.get()

            new_user_total_series = 0
            new_user_avg_error = series.avgError  # valor por defecto si no existía user

            if user_snapshot.exists:
                user_data = user_snapshot.to_dict()
                user_total_series = user_data.get("total_series_generated", 0)
                user_avg_error = user_data.get("avg_error", 0.0)

                new_user_total_series = user_total_series + 1
                new_user_avg_error = (
                    (user_avg_error * user_total_series) + series.avgError
                ) / new_user_total_series

                # Actualizar el documento del usuario
                user_ref.update({
                    "total_series_generated": Increment(1),
                    "avg_error": new_user_avg_error,
                    "last_activity": current_time
                })
            else:
                # Si no existía, se crea el documento del usuario (caso muy raro)
                new_user_total_series = 1
                user_data = {
                    "id": uid,
                    "total_series_generated": 1,
                    "avg_error": series.avgError,
                    "last_activity": current_time
                }
                user_ref.set(user_data)

            # 3) Actualizar `dashboard/stats`
            dashboard_ref = db.collection("dashboard").document("stats")
            dashboard_snapshot = dashboard_ref.get()

            if dashboard_snapshot.exists:
                dashboard_data = dashboard_snapshot.to_dict()

                # --- A) Actualizar métricas globales de series ---
                total_series = dashboard_data.get("total_series_generated", 0)
                current_avg_error = dashboard_data.get("global_avg_error", 0.0)
                series_yesterday = dashboard_data.get("series_yesterday", total_series)
                error_yesterday = dashboard_data.get("error_yesterday", current_avg_error)
                last_updated = dashboard_data.get("last_update", current_time - timedelta(days=1))

                # Verificar si cambió el día para actualizar 'series_yesterday' y 'error_yesterday'
                if isinstance(last_updated, datetime) and last_updated.date() < current_time.date():
                    series_yesterday = total_series
                    error_yesterday = current_avg_error
                    last_updated = current_time

                new_total_series = total_series + 1
                new_avg_error = (
                    (current_avg_error * total_series) + series.avgError
                ) / new_total_series

                # Crecimiento diario
                series_growth = new_total_series - series_yesterday
                error_change = new_avg_error - error_yesterday

                # --- B) Actualizar estadística por tipo de serie ---
                series_stats = dashboard_data.get("series_stats", {})
                if series.type not in series_stats:
                    # Inicializar stats si no existen para este tipo
                    series_stats[series.type] = {
                        "count": 0,
                        "avg_error": 0.0,
                        "max_error": 0.0
                    }

                st = series_stats[series.type]
                count_before = st["count"]
                avg_err_before = st["avg_error"]
                max_err_before = st["max_error"]

                new_count = count_before + 1
                new_avg_series_error = (
                    (avg_err_before * count_before) + series.avgError
                ) / new_count
                new_max_error = max(max_err_before, series.maxError)

                series_stats[series.type] = {
                    "count": new_count,
                    "avg_error": new_avg_series_error,
                    "max_error": new_max_error
                }

                # --- C) Actualizar el usuario en el array `users` ---
                users_list = dashboard_data.get("users", [])
                for i, usr in enumerate(users_list):
                    if usr["id"] == uid:
                        users_list[i]["total_series_generated"] = new_user_total_series
                        users_list[i]["avg_error"] = new_user_avg_error
                        users_list[i]["last_activity"] = current_time
                        break

                # --- D) Calcular "Usuarios con Mejor Desempeño" (top 3 por menor avg_error) ---
                # 1. Filtra para ignorar usuarios con avg_error <= 0
                valid_users = [u for u in users_list if u.get("avg_error", 0.0) > 0.0]

                # 2. Ordena la lista resultante por avg_error ascendente
                sorted_users = sorted(
                    valid_users,
                    key=lambda u: u.get("avg_error", float("inf"))
                )[:3]

                # 3. Construye la lista final
                top_performing_users = [
                    {
                        "name": u.get("name", ""),
                        "email": u.get("email", ""),
                        "avg_error": u.get("avg_error", 0.0)
                    }
                    for u in sorted_users
                ]

                # --- E) Calcular "Series con Mayor Tasa de Error" (top 3 por mayor avg_error) ---
                sorted_series = sorted(
                    series_stats.items(), 
                    key=lambda s: s[1]["avg_error"],
                    reverse=True
                )[:3]
                high_error_series = [
                    {
                        "type": s[0],
                        "count": s[1]["count"],
                        "avg_error": s[1]["avg_error"]
                    } for s in sorted_series
                ]

                # --- F) Finalmente, actualizar Firestore de una sola vez ---
                dashboard_ref.update({
                    "total_series_generated": Increment(1),
                    "global_avg_error": new_avg_error,
                    "series_yesterday": series_yesterday,
                    "error_yesterday": error_yesterday,
                    "series_growth": series_growth,
                    "error_change": error_change,
                    "last_update": last_updated,

                    "series_stats": series_stats,
                    "users": users_list,  # array de usuarios actualizado
                    "top_performing_users": top_performing_users,
                    "high_error_series": high_error_series
                })

            else:
                # El documento no existe, crearlo con valores iniciales
                dashboard_ref.set({
                    "total_series_generated": 1,
                    "global_avg_error": series.avgError,
                    "series_yesterday": 0,
                    "error_yesterday": series.avgError,
                    "series_growth": 1,
                    "error_change": 0.0,
                    "last_update": current_time,
                    "series_stats": {
                        series.type: {
                            "count": 1,
                            "avg_error": series.avgError,
                            "max_error": series.maxError
                        }
                    },
                    # Creamos un 'users' mínimo por si no existía
                    "users": [{
                        "id": uid,
                        "total_series_generated": 1,
                        "avg_error": series.avgError,
                        "last_activity": current_time
                    }],
                    "top_performing_users": [{
                        "name": "",  # Reemplaza con el nombre si lo tienes
                        "email": "", # Reemplaza con el email si lo tienes
                        "avg_error": series.avgError
                    }],
                    "high_error_series": [{
                        "type": series.type,
                        "count": 1,
                        "avg_error": series.avgError
                    }]
                })

            # 4) Retornar la respuesta
            return SeriesResponseh(
                id=series_id,
                uid=uid,
                date=series_data["date"],
                type=series_data["type"],
                points=series_data["points"],
                avgError=series_data["avgError"],
                maxError=series_data["maxError"],
                data=series_data["data"]
            )

        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Error al guardar la serie: {str(e)}"
            )

from app.core.firebase import initialize_firebase
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.auth import router as auth_router
from app.api.series import router as series_router
from app.api.results import router as results_router

app = FastAPI()

# Inicializar Firebase inmediatamente
initialize_firebase()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir los routers de autenticación y series trigonométricas
app.include_router(auth_router)
app.include_router(series_router)
app.include_router(results_router)


@app.get("/")
def read_root():
    return {"message": "FastAPI Authentication Backend with Firebase"}

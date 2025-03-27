# FastAPI + Uvicorn Backend

Este proyecto es un servidor backend construido con **FastAPI** y **Uvicorn**. Actualmente, el backend está **en producción** y conectado a **Firebase** como base de datos.

Sigue las instrucciones a continuación para configurarlo y ejecutarlo localmente.

## 🛠️ Prerrequisitos
Asegúrate de tener instalado lo siguiente en tu máquina:

- **Python** (v3.10 o superior)
- **pip** (v22 o superior)
- **Git**
- **Firebase CLI** (para gestionar Firebase si es necesario)

## 🚀 Instalación
1. **Clona el repositorio:**
```bash
git clone https://github.com/usuario/nombre-del-repo-backend.git
cd nombre-del-repo-backend
```

2. **Crea un entorno virtual:**
```bash
python -m venv env
source env/bin/activate  # En macOS/Linux
# o
env\Scripts\activate    # En Windows
```

3. **Instala las dependencias:**
```bash
pip install -r requirements.txt
```

## 📦 Configuración
1. Crea un archivo `.env` en la raíz del proyecto y configura las variables de entorno necesarias. Ejemplo:
```env
FIREBASE_CREDENTIALS=path/to/firebase-credentials.json
API_KEY=your-api-key
DATABASE_URL=https://your-database.firebaseio.com
```

2. Asegúrate de que el archivo JSON de credenciales de Firebase esté en la ubicación correcta.

3. Configura tu base de datos en Firebase y verifica que las reglas de seguridad sean adecuadas.

## 🚀 Ejecución
Para iniciar el servidor en modo de desarrollo, ejecuta el siguiente comando:
```bash
uvicorn main:app --reload
```

- `main` es el nombre del archivo principal (sin la extensión `.py`).
- `app` es la instancia de FastAPI.
- `--reload` habilita la recarga automática para desarrollo.

Por defecto, el servidor estará disponible en `http://localhost:8000`

## 🧪 Scripts Disponibles
- **`uvicorn main:app --reload`**: Ejecuta el proyecto en modo desarrollo.
- **`pytest`**: Ejecuta las pruebas.
- **`flake8`**: Ejecuta el linter para comprobar el estilo del código.

## 📚 Estructura del Proyecto
```bash
/src
  ├── controllers      # Controladores para manejar las rutas
  ├── models           # Modelos de datos
  ├── repositories     # Consultas y operaciones en Firebase
  ├── services         # Lógica de negocio
  ├── utils            # Funciones utilitarias
  ├── main.py          # Punto de entrada del servidor
  └── config.py        # Configuración de variables de entorno
```

## ✅ Contribuciones
Si deseas contribuir a este proyecto, por favor sigue los siguientes pasos:
1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -m 'Añadir nueva funcionalidad'`).
4. Sube los cambios (`git push origin feature/nueva-funcionalidad`).
5. Abre un Pull Request.

## 📝 Licencia
Este proyecto está bajo la licencia [MIT](LICENSE).

---

¡Gracias por contribuir y usar este proyecto! 😊


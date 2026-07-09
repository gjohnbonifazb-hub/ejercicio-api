# Tasks API — FastAPI + SQLite

API REST para gestión de tareas. Crea, consulta, lista y actualiza el estado de tareas con persistencia en SQLite.

Hecho con Python + FastAPI como parte del proceso de selección para Ingeniero de Software Jr en I+D (Telconet).

## Stack

| Capa        | Tecnología              |
|-------------|-------------------------|
| Framework   | FastAPI                 |
| Validación  | Pydantic v2             |
| Base datos  | SQLite 3                |
| Contenedor  | Docker (multi-stage)    |
| Tests       | pytest + httpx          |

## Cómo ejecutar

### Local (sin Docker)

```bash
# 1. Clonar el repo
git clone <url-del-repo>
cd ejercicio-api

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
.venv\Scripts\activate       # Windows
pip install -r requirements.txt

# 3. Iniciar servidor
uvicorn main:app --reload
```

La API queda en `http://localhost:8000`. La documentación interactiva (Swagger) en `http://localhost:8000/docs`.

### Con Docker

```bash
docker build -t tasks-api .
docker run -p 8000:8000 tasks-api
```

## Endpoints

| Método | Ruta            | Códigos        | Descripción                |
|--------|-----------------|----------------|----------------------------|
| GET    | `/`             | 200            | Health check               |
| GET    | `/items`        | 200            | Lista tareas (paginado)    |
| GET    | `/items/{id}`   | 200, 404       | Tarea por ID               |
| POST   | `/items`        | 201, 400       | Crear tarea                |
| PATCH  | `/items/{id}`   | 200, 404, 400  | Actualizar estado          |

> Los errores de validación devuelven **400** (Bad Request). FastAPI por defecto usa 422 (Unprocessable Entity), que es semánticamente más preciso cuando el JSON se recibió bien pero no valida contra el esquema. Sin embargo, el ejercicio pide explícitamente 400, así que se agregó un `exception_handler` que intercepta los errores de validación de Pydantic y los responde como 400. La diferencia es sutil y ambos son aceptables en APIs REST; frameworks como Flask, Express o NestJS también usan 400 por defecto.

La paginación se controla con `?page=1&limit=10` (default) hasta 100 items por página.

## Tests

```bash
pytest -v
```

15 tests cubriendo casos felices,validaciones, paginación y errores 404/422.

## Estructura del proyecto

```
ejercicio-api/
├── main.py           # Lógica de la API (rutas, BD, modelos)
├── test_main.py      # Tests unitarios
├── requirements.txt  # Dependencias
├── Dockerfile        # Imagen Docker
├── tareas.db         # Base de datos (se crea sola)
└── README.md         # Este archivo
```

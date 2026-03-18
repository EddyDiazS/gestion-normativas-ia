# Gestión y Consulta de Normativas con IA

Sistema de chatbot institucional basado en RAG (Retrieval-Augmented Generation) para consultar el reglamento académico y normativas de la Fundación Universitaria Konrad Lorenz mediante lenguaje natural.

> **Versión:** 1.0 — Prototipo  
> **Desarrollador:** Eddy Andres Diaz Santos  
> **Director:** Andres Ramirez Gaita  
> **Institución:** Fundación Universitaria Konrad Lorenz

## ¿Qué hace el software?

El usuario escribe una pregunta por ejemplo *"¿Cuántas materias puedo cancelar por semestre?"* — y el sistema busca los fragmentos más relevantes del reglamento académico usando búsqueda semántica, luego genera una respuesta citando los artículos correspondientes con ayuda de la API KEY de Google Gemini.


## Tecnologias usadas


Frontend = Next.js 16, React 19, Tailwind CSS
Backend = FastAPI, Python 3.10+ 
IA / RAG = Google Gemini, FAISS, SentenceTransformers
Base de datos = Oracle DB 
Autenticación = JWT con roles 

## Requisitos previos

Antes de instalar toca tener estas tecnologias:

- Python 3.10 o superior
- Node.js 18 o superior
- Oracle Database instalado y corriendo
- Google API Key con acceso a Gemini → https://aistudio.google.com/app/apikey
- Oracle Instant Client instalado


## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/PrototipoChatNextJs.git
cd PrototipoChatNextJs
```

### 2. Configurar el Backend

```bash
cd rag_normativas_api
```

Crear y activar el entorno virtual:

```powershell
python -m venv venv
venv\Scripts\activate
```

Se debe crear la carpeta `(venv)` al inicio de la línea antes de continuar.

Instalar dependencias y configurar variables de entorno:

```bash
pip install -r requirements.txt
cp .env.example .env.local
```

Abrir el `.env.local` que se creo y rellenar con tus valores:

```env
APP_ENV=local

GOOGLE_API_KEY=tu_clave_aqui
DATA_PATH=data/normativas

DB_USER=system
DB_PASSWORD=tu_contraseña_oracle
DB_HOST=localhost
DB_PORT=1521
DB_SERVICE=tu_servicio_oracle
ORACLE_CLIENT_PATH=ruta/al/instant_client
```

### 3. Iniciar el Backend

```bash
uvicorn app.main:app --reload
```

Al iniciar, el sistema automáticamente:
- Crea las tablas en Oracle si no existen
- Crea el usuario administrador y usuarios de prueba
- Indexa los documentos normativos

Backend disponible en: http://localhost:8000  
Documentación API: http://localhost:8000/docs

### 4. Configurar e iniciar el Frontend

Abre una segunda terminal:

```bash
cd front-next
npm install
npm run dev
```

Frontend disponible en: http://localhost:3000


## Usuarios iniciales

El sistema crea estos usuarios automáticamente al primer arranque:

| Rol | Usuario | Contraseña |
|-----|---------|------------|
| ADMINISTRADOR | admin | Admin2025* |
| RECTOR | prueba_rector | Prueba2025* |
| DECANO | prueba_decano | Prueba2025* |
| DIRECTOR | prueba_director | Prueba2025* |
| DOCENTE | prueba_docente | Prueba2025* |
| ESTUDIANTE | prueba_estudiante | Prueba2025* |


## Roles y permisos

| Rol           | Chat |     Reportes     | Usuarios |
|---------------|------|------------------|----------|
| ESTUDIANTE    | ✓    | —                | —        |
| DOCENTE       | ✓    | —                | —        |
| DIRECTOR      | ✓    | Solo su facultad | —        |
| DECANO        | ✓    | Solo su facultad | —        |
| RECTOR        | ✓    |       Todo       | CRUD completo |
| ADMINISTRADOR | ✓    |       Todo       | CRUD completo |

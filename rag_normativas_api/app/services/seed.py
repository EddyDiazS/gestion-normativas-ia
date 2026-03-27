from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USUARIOS_INICIALES = [
    # Admin permanente — nunca borrar
    {
        "username": "admin",
        "email":    "admin@konradlorenz.edu.co",
        "password": "Admin2025*",
        "role":     "ADMINISTRADOR",
        "faculty":  None,
        "program":  None,
        "cedula":   "1032938114",
    },
    {
        "username": "prueba_rector",
        "email":    "prueba.rector@konradlorenz.edu.co",
        "password": "Prueba2025*",
        "role":     "RECTOR",
        "faculty":  None,
        "program":  None,
        "cedula":   "1000000002",
    },
    {
        "username": "prueba_decano",
        "email":    "prueba.decano@konradlorenz.edu.co",
        "password": "Prueba2025*",
        "role":     "DECANO",
        "faculty":  "Facultad de Matemáticas e Ingenierías",
        "program":  None,
        "cedula":   "1000000003",
    },
    {
        "username": "prueba_director",
        "email":    "prueba.director@konradlorenz.edu.co",
        "password": "Prueba2025*",
        "role":     "DIRECTOR",
        "faculty":  "Facultad de Matemáticas e Ingenierías",
        "program":  "Ingeniería de Sistemas",
        "cedula":   "1000000004",
    },
    {
        "username": "prueba_docente",
        "email":    "prueba.docente@konradlorenz.edu.co",
        "password": "Prueba2025*",
        "role":     "DOCENTE",
        "faculty":  "Facultad de Matemáticas e Ingenierías",
        "program":  "Ingeniería de Sistemas",
        "cedula":   "1000000005",
    },
    {
        "username": "prueba_estudiante",
        "email":    "prueba.estudiante@konradlorenz.edu.co",
        "password": "Prueba2025*",
        "role":     "ESTUDIANTE",
        "faculty":  "Facultad de Matemáticas e Ingenierías",
        "program":  "Ingeniería de Sistemas",
        "cedula":   "1000000006",
    },
]

def run_seed():
    db: Session = SessionLocal()
    try:
        for datos in USUARIOS_INICIALES:
            existe = db.query(User).filter(
                (User.username == datos["username"]) |
                (User.email    == datos["email"])
            ).first()

            if not existe:
                db.add(User(
                    username        = datos["username"],
                    email           = datos["email"],
                    hashed_password = pwd_context.hash(datos["password"]),
                    role            = datos["role"],
                    faculty         = datos["faculty"],
                    program         = datos["program"],
                    cedula          = datos["cedula"],
                    is_active       = True,
                ))
            else: 
                if not existe.cedula:
                        existe.cedula = datos["cedula"]
                        
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"⚠️  Error en seed: {e}")
    finally:
        db.close()
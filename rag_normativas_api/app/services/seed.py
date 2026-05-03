from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app.database import SessionLocal
from app.models.user import User
from sqlalchemy import text

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
    {
    "username": "admin2",
    "email":    "admin2@konradlorenz.edu.co",
    "password": "Admin2025*",
    "role":     "ADMINISTRADOR",
    "faculty":  None,
    "program":  None,
    "cedula":   "1032938115",
},
]

def sync_estudiantes(db: Session):
    PROGRAMA_FACULTAD = {
        "Administración de negocios internacionales": "Escuela de Negocios",
        "Ingeniería de Sistemas":                     "Facultad de Matemáticas e Ingenierías",
        "Ingeniería Industrial":                      "Facultad de Matemáticas e Ingenierías",
        "Marketing":                                  "Escuela de Negocios",
        "Matemáticas":                                "Facultad de Matemáticas e Ingenierías",
        "Psicología":                                 "Facultad de Psicología",
    }
    try:
        resultado = db.execute(text("""
            SELECT e.CODIGO_ESTUDIANTE, p.NOMBRE_PROGRAMA 
            FROM estudiantes e
            LEFT JOIN programas p ON e.ID_PROGRAMA = p.ID_PROGRAMA
        """)).fetchall()

        nuevos = 0
        actualizados = 0
        for row in resultado:
            codigo  = str(row[0])
            program = row[1] if row[1] else None
            faculty = PROGRAMA_FACULTAD.get(program) if program else None

            existe = db.query(User).filter(
                (User.username == codigo) | (User.email == f"{codigo}@konradlorenz.edu.co")
            ).first()

            if not existe:
                db.add(User(
                    username        = codigo,
                    email           = f"{codigo}@konradlorenz.edu.co",
                    hashed_password = pwd_context.hash(codigo),
                    role            = "ESTUDIANTE",
                    faculty         = faculty,
                    program         = program,
                    cedula          = codigo,
                    is_active       = True,
                ))
                nuevos += 1
            else:
                if program and (existe.program != program or existe.faculty != faculty):
                        existe.program = program
                        existe.faculty = faculty
                        actualizados += 1    

        db.commit()
        print(f"✅ Estudiantes sincronizados: {nuevos} nuevos | {actualizados} actualizados")
    except Exception as e:
        db.rollback()
        print(f"⚠️  Error sincronizando estudiantes: {e}")

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

    db2: Session = SessionLocal()
    sync_estudiantes(db2)
    db2.close()
from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database import get_db
from app.core.roles import require_roles, UserRole
from app.models.user import User
from passlib.context import CryptContext
import pandas as pd
import io

router = APIRouter(prefix="/admin", tags=["Admin"])
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PROGRAMA_MAP = {
    "administración de negocios internacionales": 1,
    "administracion de negocios internacionales": 1,
    "ingeniería de sistemas": 2,
    "ingenieria de sistemas": 2,
    "ingeniería industrial": 3,
    "ingenieria industrial": 3,
    "marketing": 4,
    "matemáticas": 5,
    "matematicas": 5,
    "psicología": 6,
    "psicologia": 6,
}

JORNADA_MAP = {
    "diurna": 1,
    "nocturna": 2,
}

PROGRAMA_FACULTAD = {
    1: "Escuela de Negocios",
    2: "Facultad de Matemáticas e Ingenierías",
    3: "Facultad de Matemáticas e Ingenierías",
    4: "Escuela de Negocios",
    5: "Facultad de Matemáticas e Ingenierías",
    6: "Facultad de Psicología",
}

PROGRAMA_NOMBRE = {
    1: "Administración de negocios internacionales",
    2: "Ingeniería de Sistemas",
    3: "Ingeniería Industrial",
    4: "Marketing",
    5: "Matemáticas",
    6: "Psicología",
}

@router.post("/import-estudiantes")
def import_estudiantes(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(UserRole.ADMINISTRADOR, UserRole.RECTOR))
):
    contents = file.file.read()
    df = pd.read_excel(io.BytesIO(contents))
    df.columns = [c.strip() for c in df.columns]

    insertados = 0
    omitidos = 0
    usuarios_creados = 0
    errores = []

    for _, row in df.iterrows():
        codigo = int(row["Codigo_Estudiante"])

        existe_estudiante = db.execute(
            text("SELECT COUNT(*) FROM estudiantes WHERE Codigo_Estudiante = :c"),
            {"c": codigo}
        ).scalar()

        if existe_estudiante:
            # Si ya está en estudiantes, solo crear usuario si falta
            existe_user = db.query(User).filter(User.username == str(codigo)).first()
            if not existe_user:
                nombre_programa = str(row["NOMBRE_PROGRAMA"]).strip()
                id_programa = PROGRAMA_MAP.get(nombre_programa.lower())
                db.add(User(
                    username        = str(codigo),
                    email           = f"{codigo}@konradlorenz.edu.co",
                    hashed_password = pwd_context.hash(str(codigo)),
                    role            = "ESTUDIANTE",
                    faculty         = PROGRAMA_FACULTAD.get(id_programa),
                    program         = PROGRAMA_NOMBRE.get(id_programa),
                    cedula          = str(codigo),
                    is_active       = True,
                ))
                db.commit()
                usuarios_creados += 1
            omitidos += 1
            continue

        try:
            nombre_programa = str(row["NOMBRE_PROGRAMA"]).strip()
            nombre_jornada  = str(row["NOMBRE_JORNADA"]).strip() if "NOMBRE_JORNADA" in df.columns else "Diurna"

            id_programa = PROGRAMA_MAP.get(nombre_programa.lower())
            id_jornada  = JORNADA_MAP.get(nombre_jornada.lower(), 1)
            sin_jornada = 1 if id_jornada is None else 0

            if not id_programa:
                errores.append(f"Código {codigo}: programa '{nombre_programa}' no reconocido")
                continue

            fecha = pd.to_datetime(row["FECHA_NACIMIENTO"]).strftime("%Y-%m-%d")

            db.execute(text("""
                INSERT INTO estudiantes 
                (Codigo_Estudiante, EDAD, FECHA_NACIMIENTO, CODIGO_GENERO,
                 SEMESTRES_TRANSCURRIDOS, SEMESTRE_ACTUAL, PERIODO_INGRESO,
                 SIN_JORNADA, ID_PROGRAMA, ID_JORNADA)
                VALUES (:cod, :edad, TO_DATE(:fnac,'YYYY-MM-DD'), :gen,
                        :sem_trans, :sem_act, :per_ing, :sin_jor, :id_prog, :id_jor)
            """), {
                "cod": codigo, "edad": int(row["EDAD"]),
                "fnac": fecha, "gen": str(row["CODIGO_GENERO"]),
                "sem_trans": int(row["SEMESTRES_TRANSCURRIDOS"]),
                "sem_act": int(row["SEMESTRE_ACTUAL"]),
                "per_ing": int(row["PERIODO_INGRESO"]),
                "sin_jor": sin_jornada,
                "id_prog": id_programa, "id_jor": id_jornada
            })

            db.execute(text("""
                INSERT INTO rendimiento_academico
                (ID_RENDIMIENTO, Codigo_Estudiante, PROMEDIO_PERIODO, PROMEDIO_40_DEF,
                CALIFICACION_MATEMATICAS, ENGLISH_SCORE, TOTAL_COMP_LECTORA,
                EXAMEN_ORAL, CALIFICACION_40, CONOCIMIENTO_PROCEDIMENTAL,
                TOTAL_HABILIDADES_METACOGNITIVAS, PERIODO)
                VALUES (seq_rendimiento.NEXTVAL, :cod, :prom, :p40, :mat, :eng, :lec,
                        :oral, :c40, :proc, :hab, :per)
            """), {
                "cod": codigo,
                "prom": float(row["PROMEDIO_PERIODO"]),
                "p40":  int(row["PROMEDIO_40_DEF"]),
                "mat":  float(row["CALIFICACION_MATEMATICAS"]),
                "eng":  int(row["ENGLISH_SCORE"]),
                "lec":  int(row["TOTAL_COMP_LECTORA"]),
                "oral": int(row["EXAMEN_ORAL"]),
                "c40":  int(row["CALIFICACION_40"]),
                "proc": float(row["CONOCIMIENTO_PROCEDIMENTAL"]),
                "hab":  float(row["TOTAL_HABILIDADES_METACOGNITIVAS"]),
                "per":  int(row["PERIODO"])
            })

            db.execute(text("""
                INSERT INTO informacion_financiera
                (ID_FINANCIERA, Codigo_Estudiante, CODIGO_ESTRATO, FINANCIACION_INTERNA,
                FINANCIACION_INTERNA_SI, PROMEDIO_DIAS_PAGO, CANTIDAD_MORA,
                PORCENTAJE_BECA, CANTIDAD_CUOTAS, DEUDA,
                FINANCIAMIENTO, PROMEDIO_ENTIDAD_FINANCIACION)
                VALUES (seq_financiera.NEXTVAL, :cod, :est, :fin, :fin_si, :dias, :mora,
                        :beca, :cuotas, :deuda, :finan, :entidad)
            """), {
                "cod":    codigo,
                "est":    int(row["CODIGO_ESTRATO"]),
                "fin":    str(row["FINANCIACION_INTERNA"]),
                "fin_si": int(row["FINANCIACION_INTERNA_SI"]),
                "dias":   float(row["PROMEDIO_DIAS_PAGO"]),
                "mora":   int(row["CANTIDAD_MORA"]),
                "beca":   int(row["PORCENTAJE_BECA"]),
                "cuotas": int(row["CANTIDAD_CUOTAS"]),
                "deuda":  float(row["DEUDA"]),
                "finan":  float(row["FINANCIAMIENTO"]),
                "entidad":int(row["PROMEDIO_ENTIDAD_FINANCIACION"])
            })

            db.execute(text("""
                INSERT INTO ausencias
                (ID_AUSENCIA, Codigo_Estudiante, AUSENCIA_INTERSEMESTRAL, CANT_AUSENCIA_ANTERIOR)
                VALUES (seq_ausencias.NEXTVAL, :cod, :aus, :cant)
            """), {
                "cod": codigo,
                "aus": int(row["AUSENCIA_INTERSEMESTRAL"]),
                "cant": int(row["CANT_AUSENCIA_ANTERIOR"])
            })

            db.execute(text("""
                INSERT INTO riesgo_desercion
                (ID_RIESGO, Codigo_Estudiante, RIESGO, PROBABILIDAD_DESERCION)
                VALUES (seq_riesgo.NEXTVAL, :cod, :riesgo, :prob)
            """), {
                "cod":    codigo,
                "riesgo": str(row["RIESGO"]),
                "prob":   float(row["PROBABILIDAD_DESERCION"])
            })

            existe_user = db.query(User).filter(User.username == str(codigo)).first()
            if not existe_user:
                db.add(User(
                    username        = str(codigo),
                    email           = f"{codigo}@konradlorenz.edu.co",
                    hashed_password = pwd_context.hash(str(codigo)),
                    role            = "ESTUDIANTE",
                    faculty         = PROGRAMA_FACULTAD.get(id_programa),
                    program         = PROGRAMA_NOMBRE.get(id_programa),
                    cedula          = str(codigo),
                    is_active       = True,
                ))
                usuarios_creados += 1

            db.commit()
            insertados += 1

        except Exception as e:
            db.rollback()
            errores.append(f"Código {codigo}: {str(e)[:300]}")

    return {
        "insertados": insertados,
        "omitidos": omitidos,
        "usuarios_creados": usuarios_creados,
        "errores": errores
    }
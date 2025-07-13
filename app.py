import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
import os

st.set_page_config(page_title="📚 Calendario Escolar", layout="wide")

# 🧠 Simulación de base de datos de profesoras
profesoras = {
    "profe_ana": {"nombre": "Ana Martínez", "clave": "ingles123", "materia": "Inglés"},
    "profe_juan": {"nombre": "Juan López", "clave": "mate456", "materia": "Matemáticas"},
    "profe_luisa": {"nombre": "Luisa Rodríguez", "clave": "sociales789", "materia": "Sociales"},
    "profe_carla": {"nombre": "Carla Gómez", "clave": "espanol000", "materia": "Español"},
    "profe_omar": {"nombre": "Omar Reyes", "clave": "ciencias321", "materia": "Ciencias Naturales"},
}

# 📁 Archivo base
archivo = "tareas.csv"
columnas = ["Fecha de entrega", "Curso", "Materia", "Profesora", "Tipo de tarea", "Duración (min)", "Descripción"]

# Crear si no existe
if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
    df = pd.DataFrame(columns=columnas)
    df.to_csv(archivo, index=False)
else:
    df = pd.read_csv(archivo, parse_dates=["Fecha de entrega"])

# 🎨 Colores por materia
colores = {
    "Inglés": "#91D1C2",
    "Sociales": "#F9B872",
    "Ciencias Naturales": "#A7D129",
    "Matemáticas": "#C492F2",
    "Español": "#FF8D8D"
}

# 📚 Cursos y materias
cursos = [f"{grado} {letra}" for grado in ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto"] for letra in ["A", "B"]]
materias = list(colores.keys())

# 👤 Autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Ingreso para profesoras")
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    if st.button("Iniciar sesión"):
        if usuario in profesoras and profesoras[usuario]["clave"] == clave:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.nombre = profesoras[usuario]["nombre"]
            st.session_state.materia = profesoras[usuario]["materia"]
            st.success(f"¡Bienvenida/o, {st.session_state.nombre}!")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos")
    st.stop()

# Menú principal
st.title("🎓 Calendario Escolar Interactivo")

col1, col2 = st.columns(2)
if col1.button("📝 Ingresar nueva actividad"):
    st.session_state.vista = "registro"
if col2.button("📅 Ver calendario de tareas"):
    st.session_state.vista = "calendario"

if "vista" not in st.session_state:
    st.session_state.vista = "inicio"

# -------------------
# REGISTRO DE ACTIVIDAD
# -------------------
if st.session_state.vista == "registro":
    st.header("📝 Registrar Nueva Actividad")
    with st.form("formulario"):
        col1, col2 = st.columns(2)
        with col1:
            curso = st.selectbox("Curso", cursos)
            fecha = st.date_input("Fecha de entrega", value=datetime.today())
            profe = st.session_state.nombre
            duracion = st.slider("Duración estimada (min)", 5, 180, 30)
        with col2:
            materia = st.session_state.materia
            tipo = st.selectbox("Tipo de tarea", ["Lectura", "Ejercicio", "Proyecto", "Examen", "Presentación"])
            descripcion = st.text_area("Descripción")

        revisar = df[(df["Curso"] == curso) & (df["Fecha de entrega"] == pd.to_datetime(fecha))]
        tareas_dia = revisar.shape[0]
        puede_guardar = tareas_dia < 3

        if not puede_guardar:
            st.error(f"🚫 Ya hay {tareas_dia} tareas para {curso} el {fecha}.")
        submit = st.form_submit_button("✅ Registrar")

        if submit and puede_guardar:
            nueva = pd.DataFrame([{
                "Fecha de entrega": fecha,
                "Curso": curso,
                "Materia": materia,
                "Profesora": profe,
                "Tipo de tarea": tipo,
                "Duración (min)": duracion,
                "Descripción": descripcion
            }])
            df = pd.concat([df, nueva], ignore_index=True)
            df.to_csv(archivo, index=False)
            st.success("✅ Actividad registrada")

# -------------------
# VISTA DE CALENDARIO
# -------------------
elif st.session_state.vista == "calendario":
    st.header("📅 Calendario Semanal de Tareas")
    curso_sel = st.selectbox("Selecciona un curso", cursos)
    df_curso = df[df["Curso"] == curso_sel].copy()

    if df_curso.empty:
        st.info("No hay tareas aún.")
    else:
        eventos = []
        for i, row in df_curso.iterrows():
            eventos.append({
                "id": i,
                "title": f"{row['Materia']} ({row['Tipo de tarea']})",
                "start": row["Fecha de entrega"].strftime("%Y-%m-%d"),
                "end": row["Fecha de entrega"].strftime("%Y-%m-%d"),
                "color": colores.get(row["Materia"], "#ccc"),
                "extendedProps": {
                    "Curso": row["Curso"],
                    "Profesora": row["Profesora"],
                    "Descripción": row["Descripción"],
                    "Materia": row["Materia"]
                }
            })

        opciones = {
            "initialView": "timeGridWeek",
            "locale": "es",
            "editable": False,
            "eventClick": True,
            "headerToolbar": {
                "left": "prev,next today",
                "center": "title",
                "right": "dayGridMonth,timeGridWeek,listWeek"
            }
        }

        respuesta = calendar(events=eventos, options=opciones)

        if respuesta and "event" in respuesta:
            evento = respuesta["event"]
            idx = evento["id"]
            st.subheader("📌 Detalle de la actividad:")
            tarea = df.iloc[int(idx)]
            st.write(f"📘 **Materia:** {tarea['Materia']}")
            st.write(f"👩‍🏫 **Profesora:** {tarea['Profesora']}")
            st.write(f"📅 **Fecha de entrega:** {tarea['Fecha de entrega'].date()}")
            st.write(f"🕒 **Duración:** {tarea['Duración (min)']} min")
            st.write(f"🧾 **Descripción:** {tarea['Descripción']}")

            # ✅ Validación de eliminación segura
            if (
                tarea["Materia"] == st.session_state.materia
                and tarea["Profesora"].strip().lower() == st.session_state.nombre.strip().lower()
            ):
                if st.button("🗑️ Eliminar esta tarea"):
                    df.drop(index=int(idx), inplace=True)
                    df.to_csv(archivo, index=False)
                    st.success("✅ Tarea eliminada")
                    st.rerun()
            else:
                st.warning("⚠️ Solo puedes eliminar tareas de tu propia materia registradas por ti.")

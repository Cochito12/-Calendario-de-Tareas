# 📚 Streamlit App Escolar Interactiva con Login y Calendario Visual

import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar
import os

# Configuración inicial
st.set_page_config(page_title="📚 Calendario Escolar", layout="wide")

# Base de datos de profesoras (puedes moverlo a un JSON luego)
profesoras = {
    "profe_ana": {"nombre": "Ana Martínez", "clave": "ingles123", "materia": "Inglés"},
    "profe_juan": {"nombre": "Juan López", "clave": "mate456", "materia": "Matemáticas"},
    "profe_luisa": {"nombre": "Luisa Rodríguez", "clave": "sociales789", "materia": "Sociales"},
    "profe_carla": {"nombre": "Carla Gómez", "clave": "espanol000", "materia": "Español"},
    "profe_omar": {"nombre": "Omar Reyes", "clave": "ciencias321", "materia": "Ciencias Naturales"},
}

# Colores por materia
colores = {
    "Inglés": "#91D1C2",
    "Sociales": "#F9B872",
    "Ciencias Naturales": "#A7D129",
    "Matemáticas": "#C492F2",
    "Español": "#FF8D8D"
}

# Cursos disponibles
cursos = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto"]

# Archivo CSV base
archivo = "tareas.csv"
columnas = ["Fecha de entrega", "Curso", "Materia", "Profesora", "Tipo de tarea", "Duración (min)", "Descripción"]

if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
    df = pd.DataFrame(columns=columnas)
    df.to_csv(archivo, index=False)
else:
    df = pd.read_csv(archivo, parse_dates=["Fecha de entrega"])

# Autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.image("https://img.freepik.com/vector-gratis/aula-dibujos-animados_23-2147502621.jpg", width=600)
    st.title("🔐 Bienvenida Profe")
    usuario = st.text_input("👩‍🏫 Usuario")
    clave = st.text_input("🔑 Contraseña", type="password")
    if st.button("🎒 Iniciar sesión"):
        if usuario in profesoras and profesoras[usuario]["clave"] == clave:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.nombre = profesoras[usuario]["nombre"]
            st.session_state.materia = profesoras[usuario]["materia"]
            st.success(f"Bienvenida, {st.session_state.nombre} ✨")
            st.experimental_rerun()
        else:
            st.error("Usuario o contraseña incorrectos")
    st.stop()

# Sidebar con info de sesión
with st.sidebar:
    st.markdown("### 👤 Sesión activa")
    st.write(f"**Nombre:** {st.session_state.nombre}")
    st.write(f"**Materia:** {st.session_state.materia}")
    if st.button("🚪 Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Sesión cerrada.")
        st.experimental_rerun()

# Página principal con selección
st.title("🎓 Calendario Escolar Interactivo")
st.subheader("Hola profe 👩‍🏫 ¿Qué deseas hacer hoy?")
col1, col2 = st.columns(2)
if col1.button("📝 Ingresar nueva actividad"):
    st.session_state.vista = "registro"
if col2.button("📅 Consultar calendario"):
    st.session_state.vista = "calendario"

if "vista" not in st.session_state:
    st.session_state.vista = "inicio"

# REGISTRO DE ACTIVIDAD
if st.session_state.vista == "registro":
    st.header("📝 Registrar Nueva Actividad")
    with st.form("formulario"):
        curso = st.selectbox("Curso", cursos)
        fecha = st.date_input("Fecha de entrega", value=datetime.today())
        tipo = st.selectbox("Tipo de tarea", ["Lectura", "Ejercicio", "Proyecto", "Examen", "Presentación"])
        duracion = st.slider("Duración estimada (min)", 5, 180, 30)
        descripcion = st.text_area("Descripción")
        revisar = df[(df["Curso"] == curso) & (df["Fecha de entrega"] == pd.to_datetime(fecha))]
        puede_guardar = revisar.shape[0] < 3
        if not puede_guardar:
            st.error("⚠️ Ya hay 3 tareas ese día para ese curso.")
        submit = st.form_submit_button("✅ Registrar")
        if submit and puede_guardar:
            nueva = pd.DataFrame([{
                "Fecha de entrega": fecha,
                "Curso": curso,
                "Materia": st.session_state.materia,
                "Profesora": st.session_state.nombre,
                "Tipo de tarea": tipo,
                "Duración (min)": duracion,
                "Descripción": descripcion
            }])
            df = pd.concat([df, nueva], ignore_index=True)
            df.to_csv(archivo, index=False)
            st.success("✅ Actividad registrada")

# CALENDARIO VISUAL
elif st.session_state.vista == "calendario":
    st.header("📅 Vista Semanal del Calendario Escolar")
    curso_sel = st.selectbox("Selecciona un curso", cursos)
    df_curso = df[df["Curso"] == curso_sel].copy()

    if df_curso.empty:
        st.info("No hay tareas aún para este curso.")
    else:
        eventos = []
        for i, row in df_curso.iterrows():
            eventos.append({
                "id": i,
                "title": f"{row['Materia']} ({row['Tipo de tarea']})",
                "start": row["Fecha de entrega"].strftime("%Y-%m-%d"),
                "end": row["Fecha de entrega"].strftime("%Y-%m-%d"),
                "color": colores.get(row["Materia"], "#ccc"),
                "extendedProps": row.to_dict()
            })

        config = {
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

        respuesta = calendar(events=eventos, options=config)

        if respuesta and "event" in respuesta:
            evento = respuesta["event"]
            idx = evento["id"]
            tarea = df.iloc[int(idx)]
            st.subheader("📌 Detalles de la tarea seleccionada")
            st.write(f"📘 **Materia:** {tarea['Materia']}")
            st.write(f"👩‍🏫 **Profesora:** {tarea['Profesora']}")
            st.write(f"📅 **Fecha de entrega:** {tarea['Fecha de entrega'].date()}")
            st.write(f"🕒 **Duración:** {tarea['Duración (min)']} minutos")
            st.write(f"🧾 **Descripción:** {tarea['Descripción']}")

            if (
                tarea["Materia"] == st.session_state.materia and
                tarea["Profesora"].strip().lower() == st.session_state.nombre.strip().lower()
            ):
                if st.button("🗑️ Eliminar esta tarea"):
                    df.drop(index=int(idx), inplace=True)
                    df.to_csv(archivo, index=False)
                    st.success("✅ Tarea eliminada")
                    st.rerun()
            else:
                st.warning("⚠️ Solo puedes eliminar tus propias tareas en tu área.")

# 📚 Streamlit App Escolar Interactiva con Login, Calendario Visual y Coordinador Académico

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import os

# Configuración inicial
st.set_page_config(page_title="📚 Calendario Escolar", layout="wide")

# Base de datos de profesoras actualizada
profesoras = {
    "profe_heidy": {"nombre": "Heidy Rodríguez", "clave": "ingles123", "materia": "Inglés"},
    "profe_marisol": {"nombre": "Marisol Cifuentes", "clave": "mate456", "materia": "Matemáticas"},
    "profe_paola": {"nombre": "Paola Riveros", "clave": "sociales789", "materia": "Sociales"},
    "profe_carol": {"nombre": "Carol Galán Rojas", "clave": "espanol000", "materia": "Español"},
    "profe_janeth": {"nombre": "Janeth Bernal", "clave": "ciencias321", "materia": "Ciencias Naturales"},
    "coordinacion": {"nombre": "Coordinadora Académica", "clave": "admin2024", "materia": "TODAS"}
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
columnas = ["Fecha de entrega", "Curso", "Materia", "Profesora", "Tipo de tarea", "Hora de asignación", "Descripción"]

if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
    df = pd.DataFrame(columns=columnas)
    df.to_csv(archivo, index=False)
else:
    df = pd.read_csv(archivo)
    df["Fecha de entrega"] = pd.to_datetime(df["Fecha de entrega"], errors="coerce")

# Autenticación
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown(
        """
        <div style='text-align: center; padding: 60px 0;'>
            <h1 style='font-size: 42px;'>🗓️ Calendario de Tareas Escolares</h1>
            <p style='font-size: 18px; color: gray;'>Para evitar sobrecarga de actividades por curso — solo 3 tareas por día.</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    usuario = st.text_input("👩‍🏫 Usuario")
    clave = st.text_input("🔑 Contraseña", type="password")
    if st.button("🎒 Iniciar sesión"):
        if usuario in profesoras and profesoras[usuario]["clave"] == clave:
            st.session_state.autenticado = True
            st.session_state.usuario = usuario
            st.session_state.nombre = profesoras[usuario]["nombre"]
            st.session_state.materia = profesoras[usuario]["materia"]
            st.success(f"Bienvenida, {st.session_state.nombre} ✨")
            st.rerun()
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
        st.rerun()

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

# Coordinador puede subir Excel
if st.session_state.usuario == "coordinacion":
    st.markdown("### 📂 Cargar tareas desde Excel")
    archivo_excel = st.file_uploader("Sube tu archivo Excel con tareas", type=[".xlsx"])
    if archivo_excel:
        try:
            tareas_excel = pd.read_excel(archivo_excel)
            tareas_excel["Fecha de entrega"] = pd.to_datetime(tareas_excel["Fecha de entrega"], errors="coerce")
            df = pd.concat([df, tareas_excel], ignore_index=True)
            df.to_csv(archivo, index=False)
            st.success("Tareas importadas correctamente")
        except Exception as e:
            st.error(f"Error al leer archivo: {e}")

# REGISTRO
if st.session_state.vista == "registro":
    st.header("📝 Registrar Nueva Actividad")
    with st.form("formulario"):
        curso = st.selectbox("Curso", cursos)
        fecha = st.date_input("Fecha de entrega", value=datetime.today())
        hora = st.time_input("Hora en que se dejó la tarea", value=datetime.strptime("12:00", "%H:%M").time())
        tipo = st.selectbox("Tipo de tarea", ["Lectura", "Ejercicio", "Proyecto", "Examen", "Presentación"])
        descripcion = st.text_area("Descripción")

        fecha_entrega = datetime.combine(fecha, hora)
        df["Fecha de entrega"] = pd.to_datetime(df["Fecha de entrega"], errors="coerce")
        revisar = df[(df["Curso"] == curso) & (df["Fecha de entrega"].dt.date == fecha)]
        puede_guardar = revisar.shape[0] < 3 or st.session_state.usuario == "coordinacion"

        if not puede_guardar:
            st.error("⚠️ Ya hay 3 tareas ese día para ese curso.")

        submit = st.form_submit_button("✅ Registrar")
        if submit and puede_guardar:
            nueva = pd.DataFrame([{
                "Fecha de entrega": fecha_entrega,
                "Curso": curso,
                "Materia": st.session_state.materia,
                "Profesora": st.session_state.nombre,
                "Tipo de tarea": tipo,
                "Hora de asignación": hora.strftime("%H:%M"),
                "Descripción": descripcion
            }])
            df = pd.concat([df, nueva], ignore_index=True)
            df.to_csv(archivo, index=False)
            st.success("✅ Actividad registrada")

# CALENDARIO
elif st.session_state.vista == "calendario":
    st.header("📅 Vista Semanal del Calendario Escolar")
    curso_sel = st.selectbox("Selecciona un curso", cursos)
    df_curso = df[df["Curso"] == curso_sel].copy()
    df_curso["Fecha de entrega"] = pd.to_datetime(df_curso["Fecha de entrega"], errors="coerce")

    if df_curso.empty:
        st.info("No hay tareas aún para este curso.")
    else:
        eventos = []
        for i, row in df_curso.iterrows():
            fecha_entrega = pd.to_datetime(row["Fecha de entrega"])
            if pd.notnull(fecha_entrega):
                props = row.to_dict()
                eventos.append({
                    "id": i,
                    "title": f"{row['Materia']} ({row['Tipo de tarea']})",
                    "start": fecha_entrega.isoformat(),
                    "end": (fecha_entrega + timedelta(minutes=60)).isoformat(),
                    "color": colores.get(row["Materia"], "#ccc"),
                    "extendedProps": props
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
            st.write(f"📅 **Fecha de entrega:** {tarea['Fecha de entrega']}")
            st.write(f"🕓 **Hora asignada:** {tarea['Hora de asignación']}")
            st.write(f"🧾 **Descripción:** {tarea['Descripción']}")

            puede_borrar = (
                tarea["Materia"] == st.session_state.materia and
                tarea["Profesora"].strip().lower() == st.session_state.nombre.strip().lower()
            ) or st.session_state.usuario == "coordinacion"

            if puede_borrar:
                if st.button("🗑️ Eliminar esta tarea"):
                    df.drop(index=int(idx), inplace=True)
                    df.to_csv(archivo, index=False)
                    st.success("✅ Tarea eliminada")
                    st.rerun()
            else:
                st.warning("⚠️ Solo puedes eliminar tus propias tareas en tu área.")

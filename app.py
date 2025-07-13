# 📚 Streamlit App Escolar Conectada a Google Sheets (Versión Final)

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from streamlit_calendar import calendar
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 📁 Ruta del Secret File en Render
SERVICE_ACCOUNT_FILE = "/etc/secrets/credentials.json"

# 🔐 Autenticación con scopes correctos
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

credentials = ServiceAccountCredentials.from_json_keyfile_name(SERVICE_ACCOUNT_FILE, scope)
client = gspread.authorize(credentials)
sheet = client.open("Calendario_Actividades").worksheet("Tareas")

# Configuración de página
st.set_page_config(page_title="📚 Calendario Escolar", layout="wide")

# Profes y Coordinación
profesoras = {
    "profe_heidy": {"nombre": "Heidy Rodríguez", "clave": "ingles123", "materia": "Inglés"},
    "profe_marisol": {"nombre": "Marisol Cifuentes", "clave": "mate456", "materia": "Matemáticas"},
    "profe_paola": {"nombre": "Paola Riveros", "clave": "sociales789", "materia": "Sociales"},
    "profe_carol": {"nombre": "Carol Galán Rojas", "clave": "espanol000", "materia": "Español"},
    "profe_janeth": {"nombre": "Janeth Bernal", "clave": "ciencias321", "materia": "Ciencias Naturales"},
    "coordinacion": {"nombre": "Coordinadora Académica", "clave": "admin2024", "materia": "TODAS"}
}

colores = {
    "Inglés": "#91D1C2",
    "Sociales": "#F9B872",
    "Ciencias Naturales": "#A7D129",
    "Matemáticas": "#C492F2",
    "Español": "#FF8D8D"
}

cursos = ["Primero", "Segundo", "Tercero", "Cuarto", "Quinto"]

# 🔄 Cargar tareas desde Google Sheets
def cargar_datos():
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    df["Fecha"] = pd.to_datetime(df["Fecha"], errors="coerce")
    return df

# 💾 Guardar nueva fila en Google Sheets
def guardar_tarea(nueva_fila):
    sheet.append_row(nueva_fila)

# Autenticación de sesión
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.markdown("""
    <div style='text-align: center; padding: 60px 0;'>
        <h1 style='font-size: 42px;'>🗓️ Calendario de Tareas Escolares</h1>
        <p style='font-size: 18px; color: gray;'>Para evitar sobrecarga de actividades por curso — solo 3 tareas por día.</p>
    </div>
    """, unsafe_allow_html=True)
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

# Sidebar
with st.sidebar:
    st.markdown("### 👤 Sesión activa")
    st.write(f"**Nombre:** {st.session_state.nombre}")
    st.write(f"**Materia:** {st.session_state.materia}")
    if st.button("🚪 Cerrar sesión"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.success("Sesión cerrada.")
        st.rerun()

# Página principal
st.title("🎓 Calendario Escolar Interactivo")
st.subheader("Hola profe 👩‍🏫 ¿Qué deseas hacer hoy?")
col1, col2 = st.columns(2)
if col1.button("📝 Ingresar nueva actividad"):
    st.session_state.vista = "registro"
if col2.button("📅 Consultar calendario"):
    st.session_state.vista = "calendario"
if "vista" not in st.session_state:
    st.session_state.vista = "inicio"

# REGISTRO
if st.session_state.vista == "registro":
    st.header("📝 Registrar Nueva Actividad")
    df = cargar_datos()
    with st.form("formulario"):
        curso = st.selectbox("Curso", cursos)
        fecha = st.date_input("Fecha", value=datetime.today())
        hora = st.time_input("Hora en que se dejó la tarea", value=datetime.strptime("12:00", "%H:%M").time())
        tipo = st.selectbox("Tipo de tarea", ["Lectura", "Ejercicio", "Proyecto", "Examen", "Presentación"])
        descripcion = st.text_area("Descripción")

        fecha_completa = datetime.combine(fecha, hora)
        revisar = df[(df["Curso"] == curso) & (df["Fecha"].dt.date == fecha)]
        puede_guardar = revisar.shape[0] < 3 or st.session_state.usuario == "coordinacion"

        if not puede_guardar:
            st.error("⚠️ Ya hay 3 tareas ese día para ese curso.")

        if st.form_submit_button("✅ Registrar") and puede_guardar:
            fila = [
                fecha_completa.strftime("%Y-%m-%d %H:%M"),
                "-",  # Columna "Tarea" no usada
                curso,
                st.session_state.materia,
                st.session_state.nombre,
                tipo,
                hora.strftime("%H:%M"),
                descripcion
            ]
            guardar_tarea(fila)
            st.success("✅ Actividad registrada")
            st.rerun()

# CALENDARIO
elif st.session_state.vista == "calendario":
    st.header("📅 Vista Semanal del Calendario Escolar")
    df = cargar_datos()
    curso_sel = st.selectbox("Selecciona un curso", cursos)
    df_curso = df[df["Curso"] == curso_sel].copy()

    if df_curso.empty:
        st.info("No hay tareas aún para este curso.")
    else:
        eventos = []
        for i, row in df_curso.iterrows():
            fecha_entrega = pd.to_datetime(row["Fecha"])
            if pd.notnull(fecha_entrega):
                puede_ver = (st.session_state.usuario == "coordinacion" or row["Materia"] == st.session_state.materia)
                descripcion = row["Descripción"] if puede_ver else "🔒 Descripción no visible"
                eventos.append({
                    "id": i,
                    "title": f"{row['Materia']} ({row['Tipo de tarea']})",
                    "start": fecha_entrega.isoformat(),
                    "end": (fecha_entrega + timedelta(minutes=60)).isoformat(),
                    "color": colores.get(row["Materia"], "#ccc"),
                    "extendedProps": {
                        "Curso": row["Curso"],
                        "Profesora": row["Profesora"],
                        "Hora de asignación": row["Hora de asignación"],
                        "Descripción": descripcion
                    }
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
            st.write(f"📅 **Fecha:** {tarea['Fecha']}")
            st.write(f"🕓 **Hora asignada:** {tarea['Hora de asignación']}")
            if st.session_state.usuario == "coordinacion" or tarea['Materia'] == st.session_state.materia:
                st.write(f"🧾 **Descripción:** {tarea['Descripción']}")
            else:
                st.info("🔒 La descripción solo es visible para la profesora responsable o coordinación.")

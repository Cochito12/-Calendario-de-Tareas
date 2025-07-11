# app.py

import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="📚 Agenda Escolar", layout="centered")

# Base
archivo = "tareas.csv"
columnas = ["Fecha de entrega", "Curso", "Materia", "Profesora", "Tipo de tarea", "Duración (min)", "Descripción"]

# Crear o cargar datos
if not os.path.exists(archivo) or os.stat(archivo).st_size == 0:
    df = pd.DataFrame(columns=columnas)
    df.to_csv(archivo, index=False)
else:
    df = pd.read_csv(archivo, parse_dates=["Fecha de entrega"])

# Opciones de cursos
cursos = [
    "Primero", "Segundo", "Tercero", "Cuarto", "Quinto"
]

# --- PANTALLA INICIAL ---
st.title("🎓 Calendario Escolar Interactivo")

st.markdown("Hola profe 👩‍🏫👨‍🏫 ¿Qué deseas hacer hoy?")

col1, col2 = st.columns(2)
with col1:
    if st.button("📝 Ingresar nueva actividad"):
        st.session_state.pantalla = "registro"
with col2:
    if st.button("📅 Consultar calendario"):
        st.session_state.pantalla = "calendario"

# Definir pantalla por defecto si no existe
if "pantalla" not in st.session_state:
    st.session_state.pantalla = "inicio"

# --- REGISTRO DE TAREAS ---
if st.session_state.pantalla == "registro":
    st.header("📝 Registro de Nueva Actividad")

    with st.form("formulario_tarea"):
        col1, col2 = st.columns(2)
        with col1:
            curso = st.selectbox("Curso", cursos)
            fecha = st.date_input("Fecha de entrega", value=datetime.today())
            profe = st.text_input("Nombre de la profesora")
            duracion = st.slider("Duración estimada (min)", 5, 180, 30, step=5)
        with col2:
            materia = st.text_input("Materia")
            tipo = st.selectbox("Tipo de tarea", ["Lectura", "Ejercicio", "Proyecto", "Examen", "Presentación"])
            descripcion = st.text_area("Descripción de la tarea")

        revisar = df[(df["Curso"] == curso) & (df["Fecha de entrega"] == pd.to_datetime(fecha))]
        tareas_del_dia = revisar.shape[0]
        puede_guardar = tareas_del_dia < 3

        if not puede_guardar:
            st.error(f"🚫 Ya hay {tareas_del_dia} tareas para {curso} el {fecha}. No puedes agregar más.")
        enviar = st.form_submit_button("✅ Registrar")

        if enviar and puede_guardar:
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
            st.success("✅ Actividad registrada correctamente")

# --- CALENDARIO VISUAL ---
elif st.session_state.pantalla == "calendario":
    st.header("📅 Consulta del calendario")

    curso_sel = st.selectbox("Selecciona un curso", cursos)
    df_curso = df[df["Curso"] == curso_sel]

    if df_curso.empty:
        st.info("No hay tareas registradas para este curso aún.")
    else:
        # Timeline estilo calendario semanal
        st.subheader("Vista semanal (estilo calendario)")
        df_curso = df_curso.sort_values("Fecha de entrega")
        df_curso["Tarea"] = df_curso["Materia"] + ": " + df_curso["Tipo de tarea"]

        fig = px.timeline(
            df_curso,
            x_start="Fecha de entrega",
            x_end="Fecha de entrega",
            y="Tarea",
            color="Tipo de tarea",
            title=f"Tareas programadas para {curso_sel}",
            labels={"Tarea": "Tarea"}
        )
        fig.update_yaxes(autorange="reversed")
        st.plotly_chart(fig, use_container_width=True)

        # Tabla detallada
        st.subheader("📋 Tareas detalladas")
        st.dataframe(df_curso[["Fecha de entrega", "Materia", "Tipo de tarea", "Duración (min)", "Descripción"]])

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import os

st.set_page_config(page_title="📚 Calendario de Tareas", layout="centered")

# Cargar o crear archivo de tareas
archivo = "tareas.csv"
if os.path.exists(archivo):
    df = pd.read_csv(archivo, parse_dates=["Fecha de entrega"])
else:
    df = pd.DataFrame(columns=[
        "Fecha de entrega", "Curso", "Materia", "Profesora",
        "Tipo de tarea", "Duración (min)", "Descripción"
    ])
    df.to_csv(archivo, index=False)

st.title("📚 Calendario y Registro de Tareas")
st.markdown("_Evita sobrecargas de trabajo diario para tus estudiantes_ ✨")

# FORMULARIO DE REGISTRO
st.header("📝 Registrar nueva tarea")
with st.form("formulario_tarea"):
    col1, col2 = st.columns(2)
    with col1:
        curso = st.text_input("Curso (ej: 6B)")
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
        st.error(f"🚫 Ya hay {tareas_del_dia} tareas asignadas a {curso} para el {fecha}. No puedes agregar más.")
    submit = st.form_submit_button("Registrar tarea")

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
        st.success("✅ Tarea registrada con éxito")

# DASHBOARD DE TAREAS
st.header("📅 Calendario de tareas por curso")
if len(df) == 0:
    st.info("Aún no hay tareas registradas.")
else:
    curso_sel = st.selectbox("Selecciona un curso para visualizar", sorted(df["Curso"].unique()))
    df_curso = df[df["Curso"] == curso_sel]

    carga = df_curso.groupby("Fecha de entrega")["Duración (min)"].sum().reset_index()

    st.subheader("⏱️ Carga diaria de tareas")
    fig = px.bar(carga, x="Fecha de entrega", y="Duración (min)", title="Carga total por fecha")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Tareas detalladas")
    st.dataframe(df_curso.sort_values("Fecha de entrega"))

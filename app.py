import streamlit as st
import datetime
import json
from pathlib import Path
from model import predict_triage
from utils import save_patient_data
import psycopg2

# from voice_recon import transcribe_audio
from db_utils import (
    check_hospital_db,
    create_patient_entry,
    update_patient_record,
    create_triage_record,
    get_triage_records,
)
from public_api import check_public_records
from nlp_processor import process_text_to_keywords
from ticket_generator import generate_ticket
import warnings
import time
from google.cloud import storage
import os

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Triaje Hospitalario",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Diccionario de síntomas comunes
SINTOMAS = [
    "Dolor abdominal",
    "Dolor de cabeza",
    "Dificultad para respirar",
    "Dolor en el pecho",
    "Fiebre",
    "Mareos",
    "Náuseas",
    "Vómitos",
    "Diarrea",
    "Dolor muscular",
]

# Add new session state variables
if "page" not in st.session_state:
    st.session_state.update(
        {
            "page": "inicio",
            "patient_data": None,
            "symptoms_data": None,
            "triage_score": None,
        }
    )

# Add predefined questions
PREGUNTAS_TRIAJE = [
    "¿Tiene dolor en este momento? ¿Dónde?",
    "¿Desde cuándo presenta los síntomas?",
    "¿Ha tenido fiebre en las últimas 24 horas?",
    "¿Tiene alguna enfermedad crónica?",
]

warnings.filterwarnings("ignore", message=".*torch.classes.*")


def create_progress_bar():
    """Create a progress bar showing the current step in the process"""
    steps = {"inicio": 0, "dni": 1, "sintomas": 2, "ticket": 3}

    current_step = steps.get(st.session_state.page, 0)

    st.markdown("### Progreso del pre-triaje")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"{'🔵' if current_step >= 0 else '⚪'} **Inicio**")
    with col2:
        st.markdown(f"{'🔵' if current_step >= 1 else '⚪'} **Registro**")
    with col3:
        st.markdown(f"{'🔵' if current_step >= 2 else '⚪'} **Síntomas**")
    with col4:
        st.markdown(f"{'🔵' if current_step >= 3 else '⚪'} **Ticket**")

    st.divider()


def mostrar_ingreso_dni():
    create_progress_bar()

    st.title("🏥 Registro de Paciente")
    st.markdown("""
    ### Paso 1: Búsqueda de Paciente
    Ingrese el DNI del paciente para buscarlo en el sistema.
    """)

    # Initialize session states
    if "dni_input" not in st.session_state:
        st.session_state.dni_input = None
    if "search_done" not in st.session_state:
        st.session_state.search_done = False
    if "public_data" not in st.session_state:
        st.session_state.public_data = None
    if "create_clicked" not in st.session_state:
        st.session_state.create_clicked = False
    if "manual_entry" not in st.session_state:
        st.session_state.manual_entry = False

    # Search form
    if not st.session_state.manual_entry:
        with st.form("ingreso_dni"):
            dni = st.text_input("DNI del paciente")
            search_submitted = st.form_submit_button("Buscar")

            if search_submitted and dni:
                st.session_state.dni_input = dni
                st.session_state.search_done = True

    # Handle search results and patient creation
    if st.session_state.search_done:
        dni = st.session_state.dni_input
        print(f"Processing DNI: {dni}")  # Debug log

        # Buscar en base de datos pública
        public_data = check_public_records(dni)
        st.session_state.public_data = public_data
        print(f"Public records result: {public_data}")  # Debug log

        if public_data:
            st.success("Paciente encontrado en registros públicos")
            st.write("Datos encontrados:")
            st.json(public_data)

            # Verificar BD local
            hospital_data = check_hospital_db(dni)
            print(f"Hospital DB result: {hospital_data}")  # Debug log

            if not hospital_data:
                st.warning("Paciente no encontrado en la base de datos del hospital")
                if st.button("✅ Crear nuevo registro"):
                    try:
                        with st.spinner("Creando registro en la base de datos..."):
                            new_patient = create_patient_entry(public_data)

                        if new_patient:
                            st.success(f"""
                                ✅ Paciente registrado exitosamente
                                - DNI: {new_patient["dni"]}
                                - Nombre: {new_patient["nombre"]}
                                """)
                            st.session_state.patient_data = new_patient
                            time.sleep(1)
                            st.session_state.page = "sintomas"
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error al crear el registro: {str(e)}")
                        print(f"Error creating patient: {str(e)}")
                        st.error("Detalles técnicos:")
                        st.code(str(e))
            else:
                st.info("📋 Paciente ya registrado en el sistema")
                st.write("Datos del paciente:")
                st.json(hospital_data)
                if st.button("Continuar"):
                    st.session_state.patient_data = hospital_data
                    st.session_state.page = "sintomas"
                    st.rerun()
        else:
            st.error("❌ No se encontró el paciente en registros públicos")
            print("Patient not found in public records")  # Debug log

            # Show manual entry option only when public records are not found
            if st.button("📝 Ingresar datos manualmente"):
                st.session_state.manual_entry = True
                st.rerun()

    # Handle manual entry
    if st.session_state.manual_entry:
        st.subheader("📝 Ingreso Manual de Datos")
        with st.form("manual_entry_form"):
            col1, col2 = st.columns(2)
            with col1:
                nombre = st.text_input("Nombre completo*")
                dni = st.text_input("DNI / Documento de Identidad Extranjero*")
                fecha_nacimiento = st.date_input("Fecha de nacimiento*")
                genero = st.selectbox("Género", ["Masculino", "Femenino", "X", "Otro"])

            with col2:
                telefono = st.text_input("Teléfono")
                direccion = st.text_area("Dirección")
                grupo_sanguineo = st.selectbox(
                    "Grupo sanguíneo",
                    ["No conocido", "A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
                )
                cuit = st.text_input("Número de CUIT")
                nacionalidad = st.selectbox(
                    "Nacionalidad",
                    [
                        "Argentina",
                        "Paraguay",
                        "Brasil",
                        "Chile",
                        "Uruguay",
                        "Bolivia",
                        "Perú",
                        "Ecuador",
                        "Colombia",
                        "Venezuela",
                        "Guyana",
                        "Surinam",
                        "Guayana Francesa",
                        "USA",
                        "España",
                        "Portugal",
                        "Alemania",
                        "Italia",
                        "Rusia",
                        "Ucrania",
                        "Belgica",
                        "Holanda",
                        "Austria",
                        "Suiza",
                        "Dinamarca",
                        "Noruega",
                        "Suecia",
                        "Finlandia",
                        "Islandia",
                        "Groenlandia",
                        "Norfolk",
                        "Australia",
                        "Nueva Zelanda",
                        "Tonga",
                        "Samoa",
                        "Fiji",
                        "Vanuatu",
                        "Kiribati",
                        "Palau",
                        "Mongolia",
                        "China",
                        "Japon",
                        "Corea del Norte",
                        "Corea del Sur",
                        "Taiwan",
                        "Hong Kong",
                        "Macao",
                        "Singapur",
                        "Malasia",
                        "Indonesia",
                        "Filipinas",
                        "Tailandia",
                        "Vietnam",
                        "Camboya",
                        "Laos",
                        "Birmania",
                        "India",
                        "Pakistan",
                        "Bangladesh",
                        "Nepal",
                        "Butan",
                        "Bhutan",
                        "Sri Lanka",
                        "Maldivas",
                        "Myanmar",
                        "Tibet",
                        "Mongolia",
                        "China",
                        "Japon",
                        "Corea del Norte",
                        "Corea del Sur",
                        "Taiwan",
                        "Hong Kong",
                        "Macao",
                        "Singapur",
                        "Malasia",
                        "Indonesia",
                        "Filipinas",
                        "Tailandia",
                        "Vietnam",
                        "Camboya",
                        "Laos",
                        "Birmania",
                        "India",
                        "Pakistan",
                        "Bangladesh",
                        "Nepal",
                        "Butan",
                        "Bhutan",
                        "Sri Lanka",
                        "Maldivas",
                        "Myanmar",
                        "Tibet",
                    ],
                )

            st.markdown("*Campos obligatorios")
            col3, col4 = st.columns([1, 3])
            with col3:
                submitted = st.form_submit_button("Crear Paciente")
            with col4:
                if st.form_submit_button("Cancelar"):
                    st.session_state.manual_entry = False
                    st.session_state.search_done = False
                    st.rerun()

            if submitted:
                if not (nombre and dni and fecha_nacimiento):
                    st.error("Por favor complete todos los campos obligatorios")
                else:
                    manual_data = {
                        "nombre": nombre,
                        "dni": dni,
                        "fecha_nacimiento": fecha_nacimiento.strftime("%Y-%m-%d"),
                        "telefono": telefono,
                        "direccion": direccion,
                        "genero": genero,
                        "grupo_sanguineo": grupo_sanguineo,
                        "cuit": cuit,
                        "nacionalidad": nacionalidad,
                    }
                    try:
                        new_patient = create_patient_entry(manual_data)
                        st.success("✅ Paciente registrado exitosamente")
                        st.session_state.patient_data = new_patient
                        st.session_state.manual_entry = False
                        time.sleep(1)
                        st.session_state.page = "sintomas"
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error al crear el registro: {str(e)}")
                        st.error("Detalles técnicos:")
                        st.code(str(e))


def mostrar_ingreso_sintomas():
    create_progress_bar()

    st.title("🏥 Evaluación de Síntomas")
    st.markdown("""
    ### Paso 2: Registro de Síntomas
    Por favor, indique los síntomas que presenta el paciente.
    """)

    # Show process summary
    with st.expander("📋 Resumen del Proceso", expanded=True):
        st.markdown("""
        1. ✅ **Registro de Paciente** completado
        2. 🔄 **Evaluación de Síntomas** en proceso
        3. ⏳ **Generación de Ticket** pendiente
        """)

    # Show current patient info
    if st.session_state.patient_data:
        st.info(f"""
        **Paciente:** {st.session_state.patient_data["nombre"]}
        **DNI:** {st.session_state.patient_data["dni"]}
        """)

    # Predefined options for common symptoms
    NIVELES_DOLOR = ["No hay dolor", "Leve", "Moderado", "Severo", "Muy severo"]
    TIEMPO_SINTOMAS = [
        "Menos de 1 hora",
        "Algunas horas",
        "1 día",
        "2-3 días",
        "Más de 3 días",
    ]
    RESPUESTAS_SI_NO = ["No", "Sí"]

    # Display previous NLP results if they exist
    if "nlp_results" in st.session_state:
        st.divider()
        st.info("🔍 Análisis previo de palabras clave:")
        st.write(" | ".join(st.session_state.nlp_results["keywords"]))

        # Display symptom counts
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "🔴 Síntomas críticos",
                st.session_state.nlp_results["conteos"]["critico"],
            )
        with col2:
            st.metric(
                "🟡 Síntomas urgentes",
                st.session_state.nlp_results["conteos"]["urgente"],
            )
        with col3:
            st.metric(
                "🟢 Síntomas no urgentes",
                st.session_state.nlp_results["conteos"]["no_urgente"],
            )

    with st.form("sintomas_form"):
        st.subheader("🤒 Evaluación de Síntomas")

        # Dolor
        col1, col2 = st.columns(2)
        with col1:
            dolor = st.selectbox("Nivel de dolor", options=NIVELES_DOLOR, index=0)
        with col2:
            ubicacion_dolor = st.multiselect(
                "Ubicación del dolor",
                options=["Cabeza", "Pecho", "Abdomen", "Espalda", "Extremidades"],
                default=[],
            )

        # Tiempo y evolución
        tiempo_sintomas = st.select_slider(
            "Tiempo con los síntomas", options=TIEMPO_SINTOMAS, value=TIEMPO_SINTOMAS[0]
        )

        # Síntomas específicos
        st.subheader("🌡️ Síntomas Presentes")
        col3, col4 = st.columns(2)

        with col3:
            fiebre = st.radio("¿Tiene fiebre?", RESPUESTAS_SI_NO)
            dificultad_respirar = st.radio(
                "¿Tiene dificultad para respirar?", RESPUESTAS_SI_NO
            )
            nauseas = st.radio("¿Tiene náuseas o vómitos?", RESPUESTAS_SI_NO)

        with col4:
            mareos = st.radio("¿Tiene mareos?", RESPUESTAS_SI_NO)
            diarrea = st.radio("¿Tiene diarrea?", RESPUESTAS_SI_NO)
            perdida_consciencia = st.radio(
                "¿Ha perdido el conocimiento?", RESPUESTAS_SI_NO
            )

        # Condiciones preexistentes
        st.subheader("👨‍⚕️ Antecedentes Médicos")
        condiciones = st.multiselect(
            "Seleccione condiciones preexistentes",
            options=[
                "Hipertensión",
                "Diabetes",
                "Asma",
                "Problemas cardíacos",
                "Cáncer",
                "Problemas respiratorios",
                "Ninguna",
            ],
            default=["Ninguna"],
        )

        # Add observations text area at the bottom
        st.subheader("📝 Observaciones")
        observaciones = st.text_area(
            "Observaciones adicionales (opcional)",
            max_chars=200,
            help="Ingrese observaciones adicionales sobre el paciente",
        )

        # Display keyword analysis right after observations
        if "nlp_results" in st.session_state:
            st.markdown("---")
            st.info("🔍 Análisis de palabras clave en las observaciones:")
            st.write(" | ".join(st.session_state.nlp_results["keywords"]))

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "🔴 Síntomas críticos",
                    st.session_state.nlp_results["conteos"]["critico"],
                )
            with col2:
                st.metric(
                    "🟡 Síntomas urgentes",
                    st.session_state.nlp_results["conteos"]["urgente"],
                )
            with col3:
                st.metric(
                    "🟢 Síntomas no urgentes",
                    st.session_state.nlp_results["conteos"]["no_urgente"],
                )

        # Main form submit button
        submitted = st.form_submit_button("Guardar y Continuar")

        if submitted:
            # Prepare symptoms data
            symptoms_data = {
                "sintomas": ubicacion_dolor,
                "nivel_dolor": dolor,
                "ubicacion_dolor": ubicacion_dolor,
                "tiempo_sintomas": tiempo_sintomas,
                "fiebre": fiebre == "Sí",
                "dificultad_respirar": dificultad_respirar == "Sí",
                "nauseas": nauseas == "Sí",
                "mareos": mareos == "Sí",
                "diarrea": diarrea == "Sí",
                "perdida_consciencia": perdida_consciencia == "Sí",
                "condiciones_preexistentes": condiciones,
                "observaciones": observaciones,
            }

            # Convert boolean symptoms to list of active symptoms
            active_symptoms = []
            if symptoms_data["fiebre"]:
                active_symptoms.append("Fiebre")
            if symptoms_data["dificultad_respirar"]:
                active_symptoms.append("Dificultad para respirar")
            if symptoms_data["nauseas"]:
                active_symptoms.append("Náuseas")
            if symptoms_data["mareos"]:
                active_symptoms.append("Mareos")
            if symptoms_data["diarrea"]:
                active_symptoms.append("Diarrea")
            if symptoms_data["perdida_consciencia"]:
                active_symptoms.append("Pérdida de consciencia")

            # Update symptoms list with all active symptoms
            symptoms_data["sintomas"] = (
                active_symptoms + symptoms_data["ubicacion_dolor"]
            )

            # Store in session state
            st.session_state.symptoms_data = symptoms_data

            # Calculate triage score
            try:
                triage_result = predict_triage(symptoms_data)
                st.session_state.triage_score = triage_result["nivel"]

                # Store NLP results in session state
                if triage_result.get("keywords"):
                    st.session_state.nlp_results = {
                        "keywords": triage_result["keywords"],
                        "conteos": triage_result["conteos"],
                    }

                # Show success message and display NLP results temporarily
                st.success("Síntomas registrados correctamente")
                time.sleep(3)  # 3 second delay
                st.session_state.page = "ticket"
                st.rerun()

            except Exception as e:
                st.error(f"Error al procesar los síntomas: {str(e)}")
                print(f"Error processing symptoms: {str(e)}")
                st.error("Detalles técnicos:")
                st.code(symptoms_data)


def mostrar_ticket():
    create_progress_bar()

    st.title("🎫 Generación de Ticket")
    st.markdown("""
    ### Paso 3: Ticket de Atención
    Se generará un ticket con la información del paciente y el nivel de triaje asignado.
    """)

    # Show process summary
    with st.expander("📋 Resumen del Proceso", expanded=True):
        st.markdown("""
        1. ✅ **Registro de Paciente** completado
        2. ✅ **Evaluación de Síntomas** completada
        3. 🔄 **Generando Ticket**
        """)

    ticket_data = {
        "patient": st.session_state.patient_data,
        "symptoms": st.session_state.symptoms_data,
        "triage_score": st.session_state.triage_score,
        "timestamp": datetime.datetime.now(),
        "diagnosis": "Pendiente de evaluación médica",
    }

    try:
        generate_ticket(ticket_data)
        st.success("Ticket generado exitosamente")

        # Display ticket information
        st.subheader("Resumen del Ticket")
        st.write(f"""
        👤 **Paciente:** {ticket_data["patient"]["nombre"]}
        🏥 **DNI:** {ticket_data["patient"]["dni"]}
        🚨 **Nivel de Triaje:** {ticket_data["triage_score"]}
        ⏰ **Hora:** {ticket_data["timestamp"].strftime("%H:%M:%S")}
        """)

        # Add buttons in columns
        col1, col2, col3 = st.columns([1, 1, 2])

        with col1:
            # Add print button with PDF download
            with open("ticket.pdf", "rb") as pdf_file:
                pdf_bytes = pdf_file.read()
            st.download_button(
                label="🖨️ Imprimir",
                data=pdf_bytes,
                file_name=f"ticket_{ticket_data['patient']['dni']}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

        with col2:
            if st.button("🏁 Finalizar", use_container_width=True):
                # Clear session data
                st.session_state.patient_data = None
                st.session_state.symptoms_data = None
                st.session_state.triage_score = None
                st.session_state.page = "inicio"
                st.rerun()

    except Exception as e:
        st.error(f"Error al generar el ticket: {str(e)}")
        print(f"Error generating ticket: {str(e)}")  # Debug log
        st.error("Detalles técnicos:")
        st.code(ticket_data)


def mostrar_pagina_inicio():
    create_progress_bar()

    st.title("🏥 Sistema de Triaje")
    st.markdown("""
    ### Bienvenido al Sistema de Triaje
    Este sistema le guiará a través del proceso de triaje en tres pasos:
    
    1. 📝 **Registro de Paciente**
       - Búsqueda en base de datos
       - Registro de datos personales
    
    2. 🏥 **Evaluación de Síntomas**
       - Registro de síntomas actuales
       - Evaluación de condiciones preexistentes
    
    3. 🎫 **Generación de Ticket**
       - Asignación de nivel de triaje
       - Generación de ticket de atención
    """)

    st.markdown("---")

    # Crear dos columnas para los botones
    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "🆕 Ingreso de nuevo paciente (pre-triaje)", use_container_width=True
        ):
            st.session_state.page = "dni"
            st.rerun()

    with col2:
        if st.button("👩‍⚕️ Acceso Enfermería (Triaje)", use_container_width=True):
            st.session_state.page = "enfermeria"
            st.rerun()

    # Mostrar instrucciones básicas
    st.markdown("""
    ### Instrucciones
    1. Para **nuevo paciente**, haga clic en el primer botón
    2. Para **acceso de enfermería**, use el segundo botón
    """)


def create_navigation():
    """Create a navigation bar at the top of the app"""
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])

    with nav_col1:
        if st.button("🏠 Inicio"):
            st.session_state.page = "inicio"
            st.rerun()

    with nav_col2:
        if st.button("👥 Registrar Paciente (pre-triage)"):
            st.session_state.page = "dni"
            st.rerun()

    # Add a divider below the navigation
    st.divider()


def main():
    # Initialize session state if needed
    if "page" not in st.session_state:
        st.session_state.page = "inicio"

    # Add navigation bar at the top
    create_navigation()

    # Debug print
    print(f"Current page: {st.session_state.page}")

    # Page routing
    if st.session_state.page == "inicio":
        mostrar_pagina_inicio()
    elif st.session_state.page == "dni":
        mostrar_ingreso_dni()
    elif st.session_state.page == "sintomas":
        mostrar_ingreso_sintomas()
    elif st.session_state.page == "ticket":
        mostrar_ticket()
    elif st.session_state.page == "stats":
        mostrar_estadisticas()
    elif st.session_state.page == "enfermeria":
        mostrar_enfermeria()
    else:
        st.error(f"Página no encontrada: {st.session_state.page}")


def mostrar_estadisticas():
    """New function to display statistics page"""
    st.title("📊 Estadísticas del Sistema")
    st.write("Esta sección mostrará estadísticas y análisis del sistema de triaje.")

    # Placeholder for future statistics
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Pacientes Hoy", value="25")
    with col2:
        st.metric(label="Tiempo Promedio", value="12 min")


def mostrar_registro_paciente():
    st.title("📋 Registro de Paciente")

    with st.form("registro_paciente"):
        col1, col2 = st.columns(2)

        with col1:
            nombre = st.text_input("Nombre completo")
            fecha_nacimiento = st.date_input("Fecha de nacimiento")
            dni = st.text_input("DNI")

        with col2:
            telefono = st.text_input("Teléfono")
            direccion = st.text_area("Dirección")

        st.markdown("### Síntomas")
        sintomas_seleccionados = st.multiselect(
            "Seleccione sus síntomas", options=SINTOMAS
        )

        descripcion = st.text_area("Descripción adicional de los síntomas")

        submitted = st.form_submit_button("Enviar")

    if submitted:
        if not nombre or not dni or not sintomas_seleccionados:
            st.error("Por favor, complete todos los campos obligatorios")
            return

        # Crear diccionario con datos del paciente
        datos_paciente = {
            "nombre": nombre,
            "fecha_nacimiento": str(fecha_nacimiento),
            "dni": dni,
            "telefono": telefono,
            "direccion": direccion,
            "sintomas": sintomas_seleccionados,
            "descripcion": descripcion,
            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

        # Obtener predicción del modelo
        nivel_triage = predict_triage(datos_paciente)
        datos_paciente["nivel_triage"] = nivel_triage

        # Guardar datos
        save_patient_data(datos_paciente)

        # Mostrar resultado
        st.success("Registro completado exitosamente")
        mostrar_resultado_triage(datos_paciente)

        if st.button("Iniciar nuevo registro"):
            st.session_state.page = "inicio"
            st.rerun()


def mostrar_resultado_triage(datos):
    st.markdown("### Resultado del Triaje")
    nivel_triage = (
        datos["nivel_triage"]["nivel"]
        if isinstance(datos["nivel_triage"], dict)
        else datos["nivel_triage"]
    )

    st.markdown(f"""
    **Nivel de Triaje:** {nivel_triage}
    
    **Paciente:** {datos["nombre"]}
    **DNI:** {datos["dni"]}
    **Fecha y hora:** {datos["fecha_registro"]}
    
    **Síntomas reportados:**
    {", ".join(datos["sintomas"])}
    """)


def upload_to_gcs(file, patient_dni):
    """Upload a file to Google Cloud Storage bucket"""
    try:
        # Initialize GCS client
        storage_client = storage.Client()
        bucket_name = "minsal-triage-poc"
        bucket = storage_client.bucket(bucket_name)

        # Create path for patient files
        destination_blob_name = f"estudios-medicos/pacientes/{patient_dni}/{file.name}"
        blob = bucket.blob(destination_blob_name)

        # Upload file
        blob.upload_from_file(file)

        # Get public URL
        public_url = (
            f"https://storage.googleapis.com/{bucket_name}/{destination_blob_name}"
        )
        return public_url

    except Exception as e:
        print(f"Error uploading to GCS: {str(e)}")
        raise e


def mostrar_enfermeria():
    """Display nursing interface for patient assessment"""
    st.title("👩‍⚕️ Panel de Enfermería")

    # Search for patient
    st.subheader("🔍 Buscar Paciente")
    search_dni = st.text_input("DNI del paciente")

    if search_dni:
        patient_data = check_hospital_db(search_dni)
        if patient_data:
            st.success("Paciente encontrado")
            st.session_state.current_patient = patient_data

            # Show current patient info
            st.info(f"""
            **Paciente:** {patient_data["nombre"]}
            **DNI:** {patient_data["dni"]}
            """)

            # Show previous triage records in a table format
            st.subheader("📜 Registros anteriores")
            triage_records = get_triage_records(search_dni)
            if triage_records:
                for record in triage_records:
                    st.markdown(f"""
                    **Fecha:** {record["fecha_triage"]}  
                    **Nivel:** {record["nivel_triage"]}  
                    **Presión:** {record["presion_arterial"]} | 
                    **Temp:** {record["temperatura"]}°C | 
                    **Pulso:** {record["frecuencia_cardiaca"]} bpm | 
                    **O2:** {record["saturacion_oxigeno"]}%
                    ---
                    """)

            # New triage form
            st.subheader("📋 Nuevo Registro")

            # File upload section
            st.subheader("📎 Adjuntar Estudios Médicos")
            uploaded_file = st.file_uploader(
                "Seleccione archivo para subir (PDF, JPG, PNG)",
                type=["pdf", "jpg", "jpeg", "png"],
            )

            with st.form("vital_signs"):
                col1, col2 = st.columns(2)

                with col1:
                    pressure = st.text_input("Presión Arterial (mmHg)")
                    temp = st.number_input(
                        "Temperatura (°C)", min_value=35.0, max_value=42.0, value=36.5
                    )

                with col2:
                    heart_rate = st.number_input(
                        "Frecuencia Cardíaca (bpm)",
                        min_value=40,
                        max_value=200,
                        value=80,
                    )
                    oxygen = st.number_input(
                        "Saturación de Oxígeno (%)",
                        min_value=50,
                        max_value=100,
                        value=98,
                    )

                notes = st.text_area("Notas adicionales")

                # Display keyword analysis right after notes
                if "nlp_results_nursing" in st.session_state:
                    st.markdown("---")
                    st.info("🔍 Análisis de palabras clave en las notas:")
                    st.write(
                        " | ".join(st.session_state.nlp_results_nursing["keywords"])
                    )

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric(
                            "🔴 Síntomas críticos",
                            st.session_state.nlp_results_nursing["conteos"]["critico"],
                        )
                    with col2:
                        st.metric(
                            "🟡 Síntomas urgentes",
                            st.session_state.nlp_results_nursing["conteos"]["urgente"],
                        )
                    with col3:
                        st.metric(
                            "🟢 Síntomas no urgentes",
                            st.session_state.nlp_results_nursing["conteos"][
                                "no_urgente"
                            ],
                        )

                submitted = st.form_submit_button("Guardar Registro")

                if submitted:
                    try:
                        # Handle file upload if present
                        file_url = None
                        if uploaded_file is not None:
                            with st.spinner("Subiendo archivo..."):
                                file_url = upload_to_gcs(
                                    uploaded_file,
                                    st.session_state.current_patient["dni"],
                                )
                                st.success("✅ Archivo subido exitosamente")

                        # Prepare symptoms list
                        sintomas = []
                        if pressure != "":
                            sintomas.append(f"PA: {pressure}")
                        if temp > 37.5:
                            sintomas.append("Fiebre")
                        if heart_rate > 100:
                            sintomas.append("Taquicardia")
                        if oxygen < 95:
                            sintomas.append("Baja saturación")

                        # Calculate triage level
                        triage_result = predict_triage(
                            {
                                "presion_arterial": pressure,
                                "temperatura": temp,
                                "frecuencia_cardiaca": heart_rate,
                                "saturacion_oxigeno": oxygen,
                                "sintomas": sintomas,
                                "observaciones": notes,  # Add notes for NLP processing
                            }
                        )

                        # Create triage record with the nivel value
                        triage_data = {
                            "presion_arterial": pressure,
                            "temperatura": temp,
                            "frecuencia_cardiaca": heart_rate,
                            "saturacion_oxigeno": oxygen,
                            "notas": notes,
                            "nivel_triage": triage_result[
                                "nivel"
                            ],  # Use the nivel value
                            "archivo_adjunto": file_url,
                            "sintomas": sintomas,
                        }

                        new_record = create_triage_record(
                            st.session_state.current_patient["dni"], triage_data
                        )

                        # Store NLP results in session state
                        if triage_result.get("keywords"):
                            st.session_state.nlp_results_nursing = {
                                "keywords": triage_result["keywords"],
                                "conteos": triage_result["conteos"],
                            }

                        st.success("✅ Registro creado exitosamente")
                        st.info(f"Nivel de triaje sugerido: {triage_result['nivel']}")
                        st.rerun()  # This will show the stored NLP results

                    except Exception as e:
                        st.error(f"Error al crear el registro: {str(e)}")
                        st.error("Detalles técnicos:")
                        st.code(str(e))
        else:
            st.error("Paciente no encontrado")


if __name__ == "__main__":
    main()

import streamlit as st
import datetime
import json
from pathlib import Path
from model import predict_triage
from utils import save_patient_data
import psycopg2
from voice_recon import transcribe_audio
from db_utils import check_hospital_db, create_patient_entry, update_patient_record
from public_api import check_public_records
from nlp_processor import process_text_to_keywords
from ticket_generator import generate_ticket
import warnings
import time

# Configuración inicial de la página
st.set_page_config(
    page_title="Sistema de Triaje Hospitalario",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    "Dolor muscular"
]

# Add new session state variables
if 'page' not in st.session_state:
    st.session_state.update({
        'page': 'inicio',
        'patient_data': None,
        'symptoms_data': None,
        'triage_score': None
    })

# Add predefined questions
PREGUNTAS_TRIAJE = [
    "¿Tiene dolor en este momento? ¿Dónde?",
    "¿Desde cuándo presenta los síntomas?",
    "¿Ha tenido fiebre en las últimas 24 horas?",
    "¿Tiene alguna enfermedad crónica?"
]

warnings.filterwarnings('ignore', message='.*torch.classes.*')

def mostrar_ingreso_dni():
    st.title("🏥 Ingreso de Paciente")
    
    # Initialize session states
    if 'dni_input' not in st.session_state:
        st.session_state.dni_input = None
    if 'search_done' not in st.session_state:
        st.session_state.search_done = False
    if 'public_data' not in st.session_state:
        st.session_state.public_data = None
    if 'create_clicked' not in st.session_state:
        st.session_state.create_clicked = False
        
    def handle_create_click():
        st.session_state.create_clicked = True
    
    # Only show the search form if we're not in the middle of creating a patient
    if not st.session_state.create_clicked:
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
        
        if not st.session_state.public_data:
            public_data = check_public_records(dni)
            st.session_state.public_data = public_data
            print(f"Public records result: {public_data}")  # Debug log
        else:
            public_data = st.session_state.public_data
        
        if public_data:
            st.success("Paciente encontrado en registros públicos")
            st.write("Datos encontrados:")
            st.json(public_data)
            
            # Verificar BD local
            hospital_data = check_hospital_db(dni)
            print(f"Hospital DB result: {hospital_data}")  # Debug log
            
            if not hospital_data:
                st.warning("Paciente no encontrado en la base de datos del hospital")
                if not st.session_state.create_clicked:
                    st.button("✅ Crear nuevo registro", key="create_patient", on_click=handle_create_click)
                
                if st.session_state.create_clicked:
                    try:
                        print(f"Creating new patient with data: {public_data}")  # Debug log
                        
                        with st.spinner('Creando registro en la base de datos...'):
                            new_patient = create_patient_entry(public_data)
                            print(f"New patient created: {new_patient}")  # Debug log
                        
                        if new_patient:
                            st.success(f"""
                                ✅ Paciente registrado exitosamente
                                - DNI: {new_patient['dni']}
                                - Nombre: {new_patient['nombre']}
                                """)
                            
                            # Reset states and move to next page
                            st.session_state.patient_data = new_patient
                            st.session_state.create_clicked = False
                            st.session_state.search_done = False
                            st.session_state.public_data = None
                            st.session_state.dni_input = None
                            
                            # Use a placeholder for the rerun button
                            placeholder = st.empty()
                            with placeholder:
                                st.info("Redirigiendo a la página de síntomas...")
                                time.sleep(1)
                            st.session_state.page = 'sintomas'
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"❌ Error al crear el registro: {str(e)}")
                        print(f"Error creating patient: {str(e)}")  # Debug log
                        st.error("Detalles técnicos del error:")
                        st.code(str(e))
                        st.session_state.create_clicked = False
            else:
                st.info("📋 Paciente ya registrado en el sistema")
                st.write("Datos del paciente:")
                st.json(hospital_data)
                if st.button("Continuar"):
                    st.session_state.patient_data = hospital_data
                    st.session_state.page = 'sintomas'
                    st.rerun()
        else:
            st.error("❌ No se encontró el paciente en registros públicos")
            print("Patient not found in public records")  # Debug log
            st.session_state.search_done = False

def mostrar_ingreso_sintomas():
    st.title("📋 Registro de Síntomas")
    
    # Predefined options for common symptoms
    NIVELES_DOLOR = ["No hay dolor", "Leve", "Moderado", "Severo", "Muy severo"]
    TIEMPO_SINTOMAS = ["Menos de 1 hora", "Algunas horas", "1 día", "2-3 días", "Más de 3 días"]
    RESPUESTAS_SI_NO = ["No", "Sí"]
    
    with st.form("sintomas_form"):
        st.subheader("🤒 Evaluación de Síntomas")
        
        # Dolor
        col1, col2 = st.columns(2)
        with col1:
            dolor = st.selectbox(
                "Nivel de dolor",
                options=NIVELES_DOLOR,
                index=0
            )
        with col2:
            ubicacion_dolor = st.multiselect(
                "Ubicación del dolor",
                options=["Cabeza", "Pecho", "Abdomen", "Espalda", "Extremidades"],
                default=[]
            )
        
        # Tiempo y evolución
        tiempo_sintomas = st.select_slider(
            "Tiempo con los síntomas",
            options=TIEMPO_SINTOMAS,
            value=TIEMPO_SINTOMAS[0]
        )
        
        # Síntomas específicos
        st.subheader("🌡️ Síntomas Presentes")
        col3, col4 = st.columns(2)
        
        with col3:
            fiebre = st.radio("¿Tiene fiebre?", RESPUESTAS_SI_NO)
            dificultad_respirar = st.radio("¿Tiene dificultad para respirar?", RESPUESTAS_SI_NO)
            nauseas = st.radio("¿Tiene náuseas o vómitos?", RESPUESTAS_SI_NO)
        
        with col4:
            mareos = st.radio("¿Tiene mareos?", RESPUESTAS_SI_NO)
            diarrea = st.radio("¿Tiene diarrea?", RESPUESTAS_SI_NO)
            perdida_consciencia = st.radio("¿Ha perdido el conocimiento?", RESPUESTAS_SI_NO)
        
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
                "Ninguna"
            ],
            default=["Ninguna"]
        )
        
        # Observaciones adicionales
        observaciones = st.text_area(
            "Observaciones adicionales (opcional)",
            max_chars=200
        )
        
        submitted = st.form_submit_button("Guardar y Continuar")
        
        if submitted:
            # Prepare symptoms data
            symptoms_data = {
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
                "observaciones": observaciones
            }
            
            # Store in session state
            st.session_state.symptoms_data = symptoms_data
            
            # Calculate triage score
            try:
                nivel_triage = predict_triage(symptoms_data)
                st.session_state.triage_score = nivel_triage
                
                # Show success message and proceed
                st.success("Síntomas registrados correctamente")
                time.sleep(1)
                st.session_state.page = 'ticket'
                st.rerun()
                
            except Exception as e:
                st.error(f"Error al procesar los síntomas: {str(e)}")
                print(f"Error processing symptoms: {str(e)}")  # Debug log

def mostrar_ticket():
    st.title("🎫 Ticket de Atención")
    
    ticket_data = {
        "patient": st.session_state.patient_data,
        "symptoms": st.session_state.symptoms_data,
        "triage_score": st.session_state.triage_score,
        "timestamp": datetime.datetime.now()
    }
    
    generate_ticket(ticket_data)
    st.success("Ticket generado exitosamente")
    
    if st.button("Finalizar"):
        st.session_state.page = 'inicio'

def mostrar_pagina_inicio():
    st.title("🏥 Sistema de Triaje")
    
    # Crear tres columnas para los botones
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🆕 Nuevo Paciente"):
            st.session_state.page = 'dni'
            st.rerun()  # Force streamlit to rerun with new page
    
    with col2:
        if st.button("👩‍⚕️ Acceso Enfermería"):
            st.session_state.page = 'enfermeria'
            st.rerun()
    
    with col3:
        if st.button("👨‍⚕️ Acceso Médico"):
            st.session_state.page = 'medico'
            st.rerun()
    
    # Mostrar instrucciones básicas
    st.markdown("""
    ### Instrucciones
    1. Para **nuevo paciente**, haga clic en el primer botón
    2. Para **acceso de enfermería**, use el segundo botón
    3. Para **acceso médico**, use el tercer botón
    """)

def create_navigation():
    """Create a navigation bar at the top of the app"""
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([1, 1, 1, 2])
    
    with nav_col1:
        if st.button("🏠 Inicio"):
            st.session_state.page = 'inicio'
            st.rerun()
            
    with nav_col2:
        if st.button("👥 Pacientes"):
            st.session_state.page = 'dni'
            st.rerun()
            
    with nav_col3:
        if st.button("📊 Estadísticas"):
            st.session_state.page = 'stats'
            st.rerun()
    
    # Add a divider below the navigation
    st.divider()

def main():
    # Initialize session state if needed
    if 'page' not in st.session_state:
        st.session_state.page = 'inicio'
    
    # Add navigation bar at the top
    create_navigation()
    
    # Debug print
    print(f"Current page: {st.session_state.page}")
    
    # Page routing
    if st.session_state.page == 'inicio':
        mostrar_pagina_inicio()
    elif st.session_state.page == 'dni':
        mostrar_ingreso_dni()
    elif st.session_state.page == 'sintomas':
        mostrar_ingreso_sintomas()
    elif st.session_state.page == 'ticket':
        mostrar_ticket()
    elif st.session_state.page == 'stats':
        mostrar_estadisticas()
    elif st.session_state.page == 'enfermeria':
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
            "Seleccione sus síntomas",
            options=SINTOMAS
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
            "fecha_registro": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
            st.session_state.page = 'inicio'
            st.rerun()

def mostrar_resultado_triage(datos):
    st.markdown("### Resultado del Triaje")
    st.markdown(f"""
    **Nivel de Triaje:** {datos['nivel_triage']}
    
    **Paciente:** {datos['nombre']}
    **DNI:** {datos['dni']}
    **Fecha y hora:** {datos['fecha_registro']}
    
    **Síntomas reportados:**
    {', '.join(datos['sintomas'])}
    """)

def mostrar_enfermeria():
    """Display nursing interface for patient assessment"""
    st.title("👩‍⚕️ Panel de Enfermería")
    
    # Search for patient
    with st.expander("🔍 Buscar Paciente", expanded=True):
        search_dni = st.text_input("DNI del paciente")
        if search_dni:
            patient_data = check_hospital_db(search_dni)
            if patient_data:
                st.success("Paciente encontrado")
                st.session_state.current_patient = patient_data
            else:
                st.error("Paciente no encontrado")
    
    # If patient is selected, show vital signs form
    if 'current_patient' in st.session_state:
        st.subheader("📋 Registro de Signos Vitales")
        with st.form("vital_signs"):
            col1, col2 = st.columns(2)
            
            with col1:
                pressure = st.text_input("Presión Arterial (mmHg)")
                temp = st.number_input("Temperatura (°C)", min_value=35.0, max_value=42.0, value=36.5)
                
            with col2:
                heart_rate = st.number_input("Frecuencia Cardíaca (bpm)", min_value=40, max_value=200, value=80)
                oxygen = st.number_input("Saturación de Oxígeno (%)", min_value=50, max_value=100, value=98)
            
            notes = st.text_area("Notas adicionales")
            submitted = st.form_submit_button("Guardar Registro")
            
            if submitted:
                # Update patient record with new vital signs
                update_data = {
                    "presion_arterial": pressure,
                    "temperatura": temp,
                    "frecuencia_cardiaca": heart_rate,
                    "saturacion_oxigeno": oxygen,
                    "notas": notes
                }
                
                try:
                    update_patient_record(st.session_state.current_patient['dni'], update_data)
                    st.success("Registro actualizado exitosamente")
                    
                    # Recalculate triage score with new data
                    nivel_triage = predict_triage({
                        **st.session_state.current_patient,
                        **update_data
                    })
                    st.info(f"Nivel de triaje sugerido: {nivel_triage}")
                    
                except Exception as e:
                    st.error(f"Error al actualizar el registro: {str(e)}")

if __name__ == "__main__":
    main() 
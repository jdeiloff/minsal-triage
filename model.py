from nlp_processor import process_text_to_keywords

def predict_triage(datos_paciente):
    """
    Función para simular la predicción del modelo de triaje.
    Considera múltiples síntomas y signos vitales para determinar el nivel.
    """
    # Definir niveles de gravedad de síntomas
    sintomas_criticos = [
        "Dificultad para respirar", "respirar", "respiración",
        "Dolor en el pecho", "pecho", "torax",
        "Pérdida de consciencia", "desmayo", "inconsciente"
    ]
    
    sintomas_urgentes = [
        "Dolor abdominal", "abdomen", "estómago",
        "Fiebre", "temperatura", "calor",
        "Taquicardia", "corazón", "palpitaciones",
        "Baja saturación", "oxígeno"
    ]
    
    sintomas_no_urgentes = [
        "Dolor muscular", "músculo", "dolor",
        "Mareos", "mareo", "vértigo",
        "Náuseas", "nausea", "vómito",
        "Diarrea", "deposición"
    ]

    # Contadores para cada nivel
    conteo_critico = 0
    conteo_urgente = 0
    conteo_no_urgente = 0
    keywords_encontradas = []

    # Procesar notas si existen
    if 'observaciones' in datos_paciente and datos_paciente['observaciones']:
        keywords = process_text_to_keywords(datos_paciente['observaciones'])
        
        # Analizar keywords encontradas
        for keyword in keywords:
            if keyword in sintomas_criticos:
                conteo_critico += 1
                keywords_encontradas.append(f"🔴 {keyword}")
            elif keyword in sintomas_urgentes:
                conteo_urgente += 1
                keywords_encontradas.append(f"🟡 {keyword}")
            elif keyword in sintomas_no_urgentes:
                conteo_no_urgente += 1
                keywords_encontradas.append(f"🟢 {keyword}")

    # Analizar síntomas presentes
    sintomas = datos_paciente.get('sintomas', [])
    for sintoma in sintomas:
        if sintoma in sintomas_criticos:
            conteo_critico += 1
        elif sintoma in sintomas_urgentes:
            conteo_urgente += 1
        elif sintoma in sintomas_no_urgentes:
            conteo_no_urgente += 1

    # Analizar signos vitales si están presentes
    if 'temperatura' in datos_paciente:
        temp = float(datos_paciente['temperatura'])
        if temp >= 39.0:
            conteo_urgente += 1
        elif temp >= 37.5:
            conteo_no_urgente += 1

    if 'saturacion_oxigeno' in datos_paciente:
        sat_o2 = float(datos_paciente['saturacion_oxigeno'])
        if sat_o2 < 90:
            conteo_critico += 1
        elif sat_o2 < 95:
            conteo_urgente += 1

    if 'frecuencia_cardiaca' in datos_paciente:
        fc = float(datos_paciente['frecuencia_cardiaca'])
        if fc > 120 or fc < 50:
            conteo_urgente += 1
        elif fc > 100 or fc < 60:
            conteo_no_urgente += 1

    # Lógica de decisión
    if conteo_critico > 0:
        nivel = "NIVEL 1 - ATENCIÓN INMEDIATA"
    elif conteo_urgente >= 2 or (conteo_urgente == 1 and conteo_no_urgente >= 2):
        nivel = "NIVEL 2 - ATENCIÓN PRIORITARIA"
    elif conteo_urgente == 1 or conteo_no_urgente >= 2:
        nivel = "NIVEL 3 - ATENCIÓN PREFERENTE"
    else:
        nivel = "NIVEL 4 - ATENCIÓN NORMAL"

    return {
        'nivel': nivel,
        'keywords': keywords_encontradas if keywords_encontradas else None,
        'conteos': {
            'critico': conteo_critico,
            'urgente': conteo_urgente,
            'no_urgente': conteo_no_urgente
        }
    } 
def predict_triage(datos_paciente):
    """
    Función mock para simular la predicción del modelo de triaje.
    En una implementación real, aquí se llamaría al modelo ML.
    """
    sintomas_graves = ["Dificultad para respirar", "Dolor en el pecho"]
    sintomas_moderados = ["Dolor abdominal", "Fiebre"]
    
    # Lógica simple de ejemplo
    for sintoma in datos_paciente['sintomas']:
        if sintoma in sintomas_graves:
            return "NIVEL 1 - ATENCIÓN INMEDIATA"
        elif sintoma in sintomas_moderados:
            return "NIVEL 2 - ATENCIÓN PRIORITARIA"
    
    return "NIVEL 3 - ATENCIÓN NORMAL" 
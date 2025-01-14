import json
from pathlib import Path
import datetime

def save_patient_data(datos_paciente):
    # Crear directorio de datos si no existe
    data_dir = Path("datos_pacientes")
    data_dir.mkdir(exist_ok=True)
    
    # Crear nombre de archivo único
    filename = f"paciente_{datos_paciente['dni']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    # Guardar datos en formato texto
    with open(data_dir / filename, "w", encoding="utf-8") as f:
        f.write("=== REGISTRO DE PACIENTE ===\n\n")
        f.write(f"Nombre: {datos_paciente['nombre']}\n")
        f.write(f"DNI: {datos_paciente['dni']}\n")
        f.write(f"Fecha de nacimiento: {datos_paciente['fecha_nacimiento']}\n")
        f.write(f"Teléfono: {datos_paciente['telefono']}\n")
        f.write(f"Dirección: {datos_paciente['direccion']}\n")
        f.write(f"\nSíntomas: {', '.join(datos_paciente['sintomas'])}\n")
        f.write(f"Descripción adicional: {datos_paciente['descripcion']}\n")
        f.write(f"\nNivel de Triaje: {datos_paciente['nivel_triage']}\n")
        f.write(f"Fecha y hora de registro: {datos_paciente['fecha_registro']}\n")
    
    # También guardar versión JSON para futura integración con base de datos
    with open(data_dir / f"{filename}.json", "w", encoding="utf-8") as f:
        json.dump(datos_paciente, f, ensure_ascii=False, indent=2) 
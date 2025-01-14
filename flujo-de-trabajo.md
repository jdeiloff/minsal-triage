flowchart TB

Start([Inicio]) --> InputDNI[Paciente Ingresa DNI]
InputDNI --> QueryPublicDB{Consultar Base de Datos Pública}
QueryPublicDB -->|Éxito| ShowProfile[Mostrar Perfil del Paciente]
QueryPublicDB -->|Fallo| Error[Mostrar Mensaje de Error]

ShowProfile --> CheckLocalDB{Verificar BD Hospital}
CheckLocalDB -->|No Encontrado| CreateEntry[Crear Nueva Entrada]
CheckLocalDB -->|Encontrado| SymptomInput[Fase de Ingreso de Síntomas]
CreateEntry --> SymptomInput

subgraph Recolección de Síntomas
    SymptomInput --> Quest[Completar Cuestionario 4 Preguntas]
    Quest --> InputMethod{Elegir Método de Entrada}
    
    InputMethod -->|Voz| SpeechRec[Reconocimiento de Voz]
    InputMethod -->|Manual| TouchInput[Entrada Táctil]
    
    SpeechRec & TouchInput -->|Texto| NLP[Procesamiento NLP]
    NLP -->|Palabras Clave Médicas| PreTriage[Modelo ML Pre-Triaje]
end

PreTriage -->|Puntaje| SaveData[Guardar en Base de Datos]
SaveData --> PrintTicket[Imprimir Ticket de Prioridad]
PrintTicket --> NurseCheck[Examen de Enfermería]

subgraph Evaluación de Enfermería
    direction LR
    NurseCheck --> VitalSigns[Registrar Signos Vitales]
    VitalSigns --> MLTriage[Modelo ML de Triaje]
    MLTriage -->|Puntaje Final| UpdateRecord[Actualizar Registro]
end

UpdateRecord --> MedApproval{Aprobación Médica}
MedApproval -->|Aprobado| AssignPatient[Asignación de Paciente]
MedApproval -->|Rechazado| ReviseScore[Revisar Triaje]
ReviseScore --> UpdateRecord
AssignPatient --> End([Fin])

%% Styling
classDef process fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
classDef decision fill:#fff3e0,stroke:#ff6f00,stroke-width:2px;
classDef start fill:#81c784,stroke:#2e7d32,stroke-width:2px;
classDef DEFAULT fill:#ef9a9a,stroke:#c62828,stroke-width:2px;
classDef subprocesses fill:#f3e5f5,stroke:#6a1b9a,stroke-width:2px;

class Start,End start;
class QueryPublicDB,CheckLocalDB,InputMethod,MedApproval decision;
class InputDNI,ShowProfile,CreateEntry,NurseCheck,VitalSigns,UpdateRecord,AssignPatient process;
class SymptomInput,Quest,SpeechRec,TouchInput,NLP,PreTriage,MLTriage,ReviseScore subprocesses;
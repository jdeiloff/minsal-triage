# Sistema de Triaje Hospitalario 🏥

## Descripción
Sistema de registro y clasificación de pacientes basado en web que implementa los principios de TRIAJE hospitalario. Esta aplicación permite a los pacientes registrar sus datos personales y síntomas a través de una interfaz táctil amigable, y genera una clasificación de prioridad mediante un modelo de machine learning.

## Características Principales
- 📱 Interfaz táctil intuitiva
- 🗃️ Registro de datos personales del paciente
- 📋 Selección de síntomas desde lista predefinida
- 🎤 Entrada de síntomas por voz
- 🤖 Clasificación automática de TRIAJE
- 🎫 Generación de tickets de atención en PDF
- 💾 Integración con base de datos PostgreSQL
- 🔍 Búsqueda en registros públicos
- 🔄 Procesamiento de lenguaje natural para síntomas

## Requisitos
- Python 3.8 o superior
- PostgreSQL
- pip (gestor de paquetes de Python)

## Instalación

1. Clone el repositorio:
```bash
git clone [URL_DEL_REPOSITORIO]
cd sistema-triaje-hospitalario
```

2. Instale las dependencias:

```bash
pip install -r requirements.txt
```

## Uso

1. Inicie la aplicación:

```bash
streamlit run app.py
```


2. Abra su navegador web y acceda a la dirección:

```
http://localhost:8501
```

## Estructura del Proyecto

```
sistema-triaje-hospitalario/
├── app.py # Aplicación principal
├── model.py # Modelo de clasificación
├── utils.py # Funciones auxiliares
├── datos_pacientes/ # Directorio de almacenamiento de datos
└── README.md
```

## Flujo de Trabajo
1. Página de inicio con botón para solicitar atención
2. Formulario de registro de datos personales
3. Selección de síntomas
4. Procesamiento y clasificación automática
5. Generación de reporte para validación médica

## Almacenamiento de Datos
Los datos de cada paciente se almacenan en dos formatos:
- Archivo de texto (.txt) para impresión y revisión médica
- Archivo JSON (.json) para futura integración con sistemas hospitalarios

## Desarrollo Futuro
- Integración con base de datos hospitalaria
- Conexión con historial médico electrónico
- Mejora del modelo de clasificación
- Soporte para múltiples idiomas
- Interfaz para personal médico

## Notas de Seguridad
- Esta es una versión de prueba de concepto (POC)
- No utilizar en producción sin implementar medidas de seguridad adicionales
- Los datos sensibles deben ser manejados según normativas locales de protección de datos

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abra un issue para discutir cambios mayores antes de crear un pull request.

## Licencia
[Especificar tipo de licencia]

## Contacto
[Información de contacto del equipo de desarrollo]

# Descripción Técnica del Sistema de Tótems para Triaje Médico Automatizado

## 1. Descripción General del Sistema

El sistema de tótems médicos propuesto constituye una solución integral para la automatización del proceso de triaje en entornos hospitalarios. Este sistema está diseñado para optimizar el flujo de pacientes y facilitar una evaluación preliminar efectiva, reduciendo los tiempos de espera y mejorando la eficiencia operativa del personal médico.

## 2. Arquitectura del Sistema

### 2.1 Componentes Hardware

El tótem médico integra los siguientes componentes físicos:

- Pantalla táctil industrial de 21" con protección antimicrobiana
- Sistema de reconocimiento de voz con cancelación de ruido ambiental
- Lector de DNI/documentos de identidad con capacidad OCR o bien introducción manual
- Impresora térmica para tickets de prioridad
- UPS integrada para garantizar operación continua
- Gabinete metálico resistente al vandalismo con clasificación IP54
- Sistema de ventilación forzada con filtros antibacteriales
- Microfono integrado con filtro de ruido ambiente

### 2.2 Componentes Software

El sistema opera mediante una arquitectura distribuida que incluye:

- Sistema operativo Linux embebido con kernel personalizado
- Interfaz de usuario táctil desarrollada en React.js
- Backend en Python con FastAPI
- Servicio de reconocimento de voz a texto
- Base de datos PostgreSQL para almacenamiento local
- Sistema de procesamiento de lenguaje natural
- Modelos de machine learning para triaje automático
- API REST para integración con sistemas hospitalarios existentes

[Link al diagrama](https://mermaid.ink/img/pako:eNp9Vs1u4zYQfhVCiy12ASWwncR_CxRwbKcNYAdu7M2hsg80NbKZyKRAUUkcJw_Qx-ixhz311qtfrEPqx3QbJAeHPzPfzHz8ONTOYzIEr-tFsXxia6o0mV3OxVxMNY6_BNeCMy4XX8nJyc_kWiSZHtxcBxPKOAgNuLJSkFKCi4u5KPet8W8ZqO0kW8acDS53fSnSLEZMcklTICGQAdUyJZP9P8aCvs3FkYOBeN3_8cy1fCXTtXyaKBnxGIKxTLVCmAkonCNQTMpsFu9hXNE4RoihUlJVzmMQKb23adiNha34EMUW0F8DexhJRmPM_w4UjzBPzH9AfpVpwjWNMWnXyMa7kWQomBQYJ8S4fQVUwxCn28CMFbnJ4JGSoTWgi3cQXPfpdpNoubHEBlcFcznp0gyn-x8C92lqgA6hbP6ur6kvzZYrRZM1uQUmY2CM7_8WRyBzQfDP9StPMtVBX26SGMwJ9s2cS0EVl-ScTBSsMqFtDsbfmh_0Mga9luFuGMOKI_P7v7QMbe4FBW-5V_7reFgu7uQLkpAAsDVmHZjMhWR8Y87bgqDB4n3XMRUZjV_JTGZsnRNYRCSz_Z9M83jhRq6CkJ8cF4s0g2ejwpvRJEB9MNR7ER9XCgwcWdMJjelS0ZT0Y_oIptoQRZO-GpJmitOVETBqVpLxyKydmMV7o1wQoTmkyi6HM7zeA1KAaHhhaPBLRlWIZwDi-CIhQmljqZ8oLvSMswfQwfUmUUiZIvnc-OC2VDyk4cKErEyt602mUrCqDIbPdAMiP6wI1AbU_gddHIlp-EjjjFZacuxyZkKugBm1kNFtwVWFb8PdmZs05SuR4vGueH5BzRy7g92DUlgHS-s4Hv2PUUygItR4lCYumeSKC6OL70mI18UoSoVBj2kUC3_B0EUS8nAmrmUeGcJekiiJpe96-H9Z1F8cNyrasbCxcytzo3tpihVMqDYSCnpmcmDP6WT_RcDwa_piIW7hkacwxXQgsGPMuirb2bS5usnPxVF0uz8U4ZcAKVl8NaV-_kymehtzsZoLFtM0HUBEEiv6lGBnjLufoB5dROAbih6g-6lWv2h1lsX05ImHet1tJM_fHP8QGE-NAnKAKIrOoFYBRFEzqtU-BEjNW1R4t-us1T6vvBvQCs8aH3oPhle976NZmX7UoR1a-bNmo91ofxw9WxYMQMkBFnARXVQgTVpfVphHIAUMsa-pj1zntZTwx4-k7z4FvtPPfFcMJZsVRvnq-s4D5juPgX-4cP7hCvmuMPxjXRTlVhHcF8G37d2v2qV_aJY-dkG_amB-efl8V5Iumd8838NWsaE8xA-Qnbmyc0-vYQNzr4tD7HMPc28u3tCOZlpOt4J5Xa0y8D0ls9Xa60Y0TnGW2VoGGE3RTbUKIX49qHH-fWM_c3wvoeJ3KQ82OPe6O-_Z69Y7ndOzZuO81ao3W-coizPf23rds_Zpq94-r511mo16rdZsNt9878VC1E7bnXqj1ey0zhuNerNMY2jDFhHe_gUcXFg_?type=png)

## 3. Funcionalidades Principales

### 3.1 Identificación de Pacientes
- Lectura automática de documentos de identidad
- Integración con base de datos pública de ciudadanos
- Creación automática de perfiles temporales para pacientes no registrados

### 3.2 Recolección de Síntomas
- Interfaz dual con entrada por voz y táctil
- Cuestionario adaptativo basado en respuestas previas
- Procesamiento de lenguaje natural para interpretación de síntomas
- Sistema de preguntas de verificación para asegurar precisión

### 3.3 Sistema de Triaje Automatizado
- Modelo de machine learning pre-entrenado para evaluación inicial
- Algoritmos de priorización basados en estándares internacionales
- Sistema de alertas para casos críticos
- Integración con protocolos hospitalarios existentes

## 4. Medidas de Seguridad y Cumplimiento

### 4.1 Seguridad de Datos
- Encriptación de datos en reposo y en tránsito
- Cumplimiento con GDPR y regulaciones locales de protección de datos
- Sistema de logs para auditoría completa
- Borrado seguro de datos temporales

### 4.2 Seguridad Física
- Sensores de temperatura y humedad
- Sistema de desinfección UV programable
- Botón de pánico con conexión directa a seguridad
- Backup de energía con autonomía de 2 horas

## 5. Integración con Sistemas Existentes 

El sistema está diseñado para integrarse con:
- Historia Clínica Electrónica (HCE)
- Sistema de Gestión Hospitalaria
- Base de datos de farmacia
- Sistema de turnos y derivaciones

## 6. Mantenimiento y Soporte

- Monitoreo remoto 24/7
- Sistema de diagnóstico preventivo
- Actualizaciones automáticas de software
- Soporte técnico con tiempo de respuesta garantizado

## 7. Requerimientos de Instalación

### 7.1 Requerimientos Físicos
- Espacio mínimo: 1.5m x 1.5m
- Conexión eléctrica: 220V, 10A
- Conexión a internet: Mínimo 10Mbps simétricos / Revisar posibilidad de conexión con red móvil 4G
- Temperatura ambiente: 18-30°C

### 7.2 Requerimientos de Red
- IP fija
- VLAN dedicada
- Firewall configurado
- Acceso a servidores internos del hospital

## 8. Escalabilidad

El sistema está diseñado para escalar en:
- Número de tótems por institución
- Capacidad de procesamiento
- Volumen de datos almacenados
- Funcionalidades adicionales mediante módulos

## 9. Métricas y Reportes

El sistema genera automáticamente reportes sobre:
- Tiempo promedio de atención
- Precisión del triaje automático
- Uso del sistema por horarios
- Estadísticas de tipos de consultas
- Indicadores de satisfacción del usuario

## 10. Consideraciones de Implementación

Para una implementación exitosa se recomienda:
- Capacitación del personal médico y de enfermería
- Período de prueba con supervisión directa
- Evaluación continua de la precisión del triaje
- Ajuste de parámetros según retroalimentación del personal
-- Create patients table
CREATE TABLE IF NOT EXISTS patients (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    fecha_nacimiento DATE,
    telefono VARCHAR(20),
    direccion TEXT,
    genero VARCHAR(1),
    grupo_sanguineo VARCHAR(3),
    seguro_social VARCHAR(20),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultima_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create triage_records table for tracking triage history
CREATE TABLE IF NOT EXISTS triage_records (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    nivel_triage VARCHAR(50),
    sintomas TEXT[],
    presion_arterial VARCHAR(20),
    temperatura DECIMAL(4,2),
    frecuencia_cardiaca INTEGER,
    saturacion_oxigeno INTEGER,
    notas TEXT,
    fecha_triage TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verificado_por VARCHAR(100),
    FOREIGN KEY (patient_id) REFERENCES patients(id)
);

-- Add some indexes for better performance
CREATE INDEX idx_patients_dni ON patients(dni);
CREATE INDEX idx_triage_patient_id ON triage_records(patient_id);
CREATE INDEX idx_triage_fecha ON triage_records(fecha_triage); 
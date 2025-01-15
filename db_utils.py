import psycopg2
from psycopg2.extras import DictCursor
import streamlit as st

def get_db_connection():
    """Create a database connection using streamlit secrets"""
    try:
        print("Attempting to connect to database...")  # Debug log
        conn = psycopg2.connect(
            dbname=st.secrets["DB_NAME"],
            user=st.secrets["DB_USER"],
            password=st.secrets["DB_PASSWORD"],
            host=st.secrets["DB_HOST"],
            port=st.secrets["DB_PORT"]
        )
        print("Database connection successful!")  # Debug log
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")  # Debug log
        raise e

def create_patient_entry(patient_data):
    """Create a new patient entry in the database"""
    print(f"Starting create_patient_entry with data: {patient_data}")  # Debug log
    
    # Ensure all required fields are present
    required_fields = ['dni', 'nombre', 'fecha_nacimiento']
    for field in required_fields:
        if field not in patient_data:
            raise ValueError(f"Missing required field: {field}")
    
    conn = None
    try:
        conn = get_db_connection()
        print("Got database connection")  # Debug log
        
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # Prepare the SQL query
            sql = """
                INSERT INTO patients (
                    dni, 
                    nombre, 
                    fecha_nacimiento, 
                    telefono, 
                    direccion, 
                    genero, 
                    grupo_sanguineo, 
                    cuit
                ) VALUES (
                    %(dni)s, 
                    %(nombre)s, 
                    %(fecha_nacimiento)s, 
                    %(telefono)s, 
                    %(direccion)s, 
                    %(genero)s, 
                    %(grupo_sanguineo)s, 
                    %(cuit)s
                ) RETURNING *;
            """
            
            print(f"About to execute SQL with data: {patient_data}")  # Debug log
            print(f"SQL Query: {cur.mogrify(sql, patient_data)}")  # Debug log
            
            cur.execute(sql, patient_data)
            print("SQL executed successfully")  # Debug log
            
            new_patient = cur.fetchone()
            print(f"Fetched result: {new_patient}")  # Debug log
            
            if new_patient:
                print("Committing transaction...")  # Debug log
                conn.commit()
                print("Transaction committed successfully")  # Debug log
                
                # Convert to dictionary
                columns = [desc[0] for desc in cur.description]
                patient_dict = dict(zip(columns, new_patient))
                return patient_dict
            else:
                print("No data returned from insert")  # Debug log
                return None
                
    except Exception as e:
        print(f"Error in create_patient_entry: {str(e)}")  # Debug log
        if conn:
            print("Rolling back transaction...")  # Debug log
            conn.rollback()
        raise e
    finally:
        if conn:
            print("Closing database connection...")  # Debug log
            conn.close()
            print("Database connection closed")  # Debug log

def check_hospital_db(dni):
    """Check if a patient exists in the hospital database"""
    print(f"Checking hospital DB for DNI: {dni}")  # Debug log
    
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM patients WHERE dni = %s", (dni,))
            result = cur.fetchone()
            
            if result:
                print(f"Found patient in hospital DB: {result}")  # Debug log
                columns = [desc[0] for desc in cur.description]
                return dict(zip(columns, result))
            else:
                print("Patient not found in hospital DB")  # Debug log
                return None
                
    except Exception as e:
        print(f"Error in check_hospital_db: {str(e)}")  # Debug log
        return None
    finally:
        if conn:
            conn.close()

def update_patient_record(patient_id, update_data):
    """
    Update an existing patient record with new data
    
    Args:
        patient_id: DNI or unique identifier of the patient
        update_data: Dictionary containing the fields to update
    """
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            # Build the SQL update statement dynamically based on the provided fields
            update_fields = [f"{key} = %({key})s" for key in update_data.keys()]
            sql = f"""
                UPDATE patients 
                SET {', '.join(update_fields)}
                WHERE dni = %(patient_id)s
            """
            
            # Merge the patient_id into the update data
            execution_data = {**update_data, 'patient_id': patient_id}
            
            cur.execute(sql, execution_data)
            conn.commit() 

def create_triage_record(patient_dni, triage_data):
    """Create a new triage record for a patient"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            # First get patient_id from dni
            cur.execute("SELECT id FROM patients WHERE dni = %s", (patient_dni,))
            patient = cur.fetchone()
            
            if not patient:
                raise ValueError(f"Patient with DNI {patient_dni} not found")
            
            # Insert triage record
            sql = """
                INSERT INTO triage_records (
                    patient_id,
                    presion_arterial,
                    temperatura,
                    frecuencia_cardiaca,
                    saturacion_oxigeno,
                    notas,
                    nivel_triage,
                    verificado_por,
                    sintomas
                ) VALUES (
                    %(patient_id)s,
                    %(presion_arterial)s,
                    %(temperatura)s,
                    %(frecuencia_cardiaca)s,
                    %(saturacion_oxigeno)s,
                    %(notas)s,
                    %(nivel_triage)s,
                    %(verificado_por)s,
                    %(sintomas)s
                ) RETURNING *;
            """
            
            # Convert symptoms to array if string or keep as is if already array
            sintomas = triage_data.get('sintomas', [])
            if isinstance(sintomas, str):
                sintomas = [sintomas]
            
            # Prepare data for insertion
            insert_data = {
                'patient_id': patient['id'],
                'presion_arterial': triage_data.get('presion_arterial'),
                'temperatura': triage_data.get('temperatura'),
                'frecuencia_cardiaca': triage_data.get('frecuencia_cardiaca'),
                'saturacion_oxigeno': triage_data.get('saturacion_oxigeno'),
                'notas': triage_data.get('notas'),
                'nivel_triage': triage_data.get('nivel_triage'),
                'verificado_por': triage_data.get('verificado_por', 'Enfermería'),
                'sintomas': sintomas
            }
            
            print(f"Inserting triage record with data: {insert_data}")  # Debug log
            
            cur.execute(sql, insert_data)
            new_record = cur.fetchone()
            conn.commit()
            
            return new_record
            
    except Exception as e:
        print(f"Error creating triage record: {str(e)}")
        if conn:
            conn.rollback()
        raise e
    finally:
        if conn:
            conn.close()

def get_triage_records(patient_dni):
    """Get all triage records for a patient"""
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=DictCursor) as cur:
            sql = """
                SELECT tr.* 
                FROM triage_records tr
                JOIN patients p ON p.id = tr.patient_id
                WHERE p.dni = %s
                ORDER BY tr.fecha_triage DESC;
            """
            cur.execute(sql, (patient_dni,))
            records = cur.fetchall()
            return records
    except Exception as e:
        print(f"Error fetching triage records: {str(e)}")
        raise e
    finally:
        if conn:
            conn.close() 
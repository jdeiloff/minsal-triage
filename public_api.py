def check_public_records(dni):
    """
    Mock function to simulate checking public records.
    In production, this would connect to actual government APIs.
    
    Args:
        dni (str): DNI/NIE number to check
        
    Returns:
        dict: Mock patient data if DNI matches test cases, None otherwise
    """
    # Mock database of test DNIs
    mock_records = {
        "12345678": {
            "dni": "12345678",
            "nombre": "Juan Pérez",
            "fecha_nacimiento": "1980-05-15",
            "telefono": "600123456",
            "direccion": "Calle Principal 123",
            "genero": "M",
            "grupo_sanguineo": "A+",
            "cuit": "20-12345678-9",
            "nacionalidad": "Argentina"
        },
        "87654321": {
            "dni": "87654321",
            "nombre": "María García",
            "fecha_nacimiento": "1992-09-23",
            "telefono": "600789012",
            "direccion": "Avenida Central 456",
            "genero": "F",
            "grupo_sanguineo": "O-",
            "cuit": "27-87654321-4",
            "nacionalidad": "Argentina"
        },
        "11111111": {
            "dni": "11111111",
            "nombre": "Carlos Rodríguez",
            "fecha_nacimiento": "1975-12-01",
            "telefono": "600345678",
            "direccion": "Plaza Mayor 789",
            "genero": "M",
            "grupo_sanguineo": "B+",
            "cuit": "20-11111111-1",
            "nacionalidad": "Argentina"
        },
        "99999999": {
            "dni": "99999999",
            "nombre": "Pedro Gómez",
            "fecha_nacimiento": "1985-07-10",
            "telefono": "600987654",
            "direccion": "Avenida Libertador 321",
            "genero": "M",
            "grupo_sanguineo": "AB+",
            "cuit": "20-99999999-0",
            "nacionalidad": "Argentina"
        },
        "1234567890": {
            "dni": "1234567890",
            "nombre": "Ana López",
            "fecha_nacimiento": "1990-03-15",
            "telefono": "600567890",
            "direccion": "Plaza de la Libertad 123",
            "genero": "F",
            "grupo_sanguineo": "O+",
            "cuit": "27-12345678-9",
            "nacionalidad": "Paraguay"
        }
    }
    
    # Simulate API delay
    import time
    time.sleep(1)
    
    # Return mock data if DNI exists in our test cases
    return mock_records.get(dni) 
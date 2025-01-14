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
            "seguro_social": "SS123456789"
        },
        "87654321": {
            "dni": "87654321",
            "nombre": "María García",
            "fecha_nacimiento": "1992-09-23",
            "telefono": "600789012",
            "direccion": "Avenida Central 456",
            "genero": "F",
            "grupo_sanguineo": "O-",
            "seguro_social": "SS987654321"
        },
        "11111111": {
            "dni": "11111111",
            "nombre": "Carlos Rodríguez",
            "fecha_nacimiento": "1975-12-01",
            "telefono": "600345678",
            "direccion": "Plaza Mayor 789",
            "genero": "M",
            "grupo_sanguineo": "B+",
            "seguro_social": "SS111111111"
        }
    }
    
    # Simulate API delay
    import time
    time.sleep(1)
    
    # Return mock data if DNI exists in our test cases
    return mock_records.get(dni) 
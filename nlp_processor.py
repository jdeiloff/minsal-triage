def process_text_to_keywords(text):
    """
    Process text to extract keywords using a simple rule-based approach
    
    Args:
        text (str): Input text to process
        
    Returns:
        list: Extracted keywords
    """
    try:
        # Spanish stopwords (common words to filter out)
        stop_words = {
            'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas', 'y', 'o', 'pero', 'si',
            'de', 'del', 'a', 'en', 'para', 'por', 'con', 'al', 'lo', 'le', 'ha', 'he',
            'que', 'es', 'no', 'son', 'era', 'este', 'esta', 'estos', 'estas', 'ese',
            'esa', 'esos', 'esas', 'aquel', 'aquella', 'me', 'mi', 'tu', 'te', 'se',
            'nos', 'su', 'sus', 'como', 'cuando', 'donde', 'quien', 'cual', 'que',
            'mas', 'mas', 'mientras', 'antes', 'despues', 'ahora', 'durante'
        }

        # Medical terms to specifically look for
        medical_terms = {
            # Síntomas críticos
            'dolor': 'critico', 'pecho': 'critico', 'respirar': 'critico',
            'dificultad': 'critico', 'inconsciente': 'critico', 'sangrado': 'critico',
            'hemorragia': 'critico', 'convulsion': 'critico', 'convulsiones': 'critico',
            
            # Síntomas urgentes
            'fiebre': 'urgente', 'vomito': 'urgente', 'vómito': 'urgente',
            'diarrea': 'urgente', 'mareo': 'urgente', 'mareos': 'urgente',
            'nausea': 'urgente', 'náusea': 'urgente', 'abdomen': 'urgente',
            
            # Síntomas no urgentes
            'tos': 'no_urgente', 'cansancio': 'no_urgente', 'fatiga': 'no_urgente',
            'malestar': 'no_urgente', 'picazon': 'no_urgente', 'picazón': 'no_urgente',
            'comezon': 'no_urgente', 'comezón': 'no_urgente'
        }

        # Normalize text: lowercase and split into words
        words = text.lower().replace('.', ' ').replace(',', ' ').split()
        
        # Filter out stopwords and short words, keep medical terms
        keywords = []
        for word in words:
            if (word in medical_terms and 
                word not in stop_words and 
                len(word) > 2):
                keywords.append(word)

        return keywords

    except Exception as e:
        print(f"Error processing text: {str(e)}")
        return []

if __name__ == "__main__":
    # Test the processor
    test_text = "El paciente presenta dolor en el pecho y dificultad para respirar"
    print(f"Testing with text: {test_text}")
    print(f"Keywords: {process_text_to_keywords(test_text)}") 

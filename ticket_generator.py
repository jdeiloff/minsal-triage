from reportlab.pdfgen import canvas
import datetime

def generate_ticket(ticket_data):
    """Generate a PDF ticket with patient and triage information"""
    c = canvas.Canvas("ticket.pdf")
    c.setFont("Helvetica", 12)
    
    # Header
    c.drawString(100, 750, "TICKET DE ATENCIÓN")
    c.drawString(100, 725, f"Fecha: {ticket_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Patient info
    c.drawString(100, 700, f"Paciente: {ticket_data['patient']['nombre']}")
    c.drawString(100, 675, f"DNI: {ticket_data['patient']['dni']}")
    
    # Triage info
    c.drawString(100, 650, f"Nivel de Triaje: {ticket_data['triage_score']}")
    c.drawString(100, 625, f"Síntomas principales: {', '.join(ticket_data['symptoms']['sintomas'][:3])}")
    
    # Diagnosis (if available)
    diagnosis = ticket_data.get('diagnosis', 'Pendiente de evaluación médica')
    c.drawString(100, 600, f"Diagnóstico: {diagnosis}")
    
    # Footer
    c.drawString(100, 50, "Por favor, espere a ser llamado")
    
    c.save() 
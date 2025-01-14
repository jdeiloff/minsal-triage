from reportlab.pdfgen import canvas
import datetime

def generate_ticket(ticket_data):
    filename = f"ticket_{ticket_data['patient']['dni']}_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    c = canvas.Canvas(filename)
    
    # Add ticket content
    c.drawString(100, 750, "TICKET DE ATENCIÓN")
    c.drawString(100, 700, f"Paciente: {ticket_data['patient']['nombre']}")
    c.drawString(100, 675, f"DNI: {ticket_data['patient']['dni']}")
    c.drawString(100, 650, f"Nivel de Triaje: {ticket_data['triage_score']}")
    c.drawString(100, 625, f"Fecha: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    c.drawString(100, 600, f"Sintomas: {', '.join(ticket_data['symptoms'])}")
    c.drawString(100, 575, f"Diagnóstico: {ticket_data['diagnosis']}")
    c.drawString(100, 550, f"Tratamiento: {ticket_data['treatment']}")
    c.drawString(100, 525, f"Observaciones: {ticket_data['observations']}")
    
    c.save()
    return filename 
# modules/noti2.py

import smtplib
from email.message import EmailMessage
import os

REMITENTE_EMAIL = os.environ.get('EMAIL_USER', 'eleazararriola11@gmail.com')
REMITENTE_PASSWORD = os.environ.get('EMAIL_PASS', 'qmoctgsginmdxbqw')

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def enviar_correo(asunto, cuerpo_html, destinatario):
    """
    Envía un correo electrónico con el contenido de las alertas a un destinatario específico.
    """
    if not REMITENTE_EMAIL or not REMITENTE_PASSWORD or REMITENTE_EMAIL == 'tu_correo@gmail.com':
        print("ERROR: El correo o la contraseña no están configurados.")
        return False, "Credenciales de correo no configuradas."

    # Crear el mensaje
    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = REMITENTE_EMAIL
    msg['To'] = destinatario 
    msg.set_content("Este es un correo con formato HTML. Por favor, activa la vista HTML.")
    

    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(REMITENTE_EMAIL, REMITENTE_PASSWORD)
            server.send_message(msg)
            print(f"Correo de alerta enviado exitosamente a {destinatario}.")
            return True, f"Correo enviado exitosamente a {destinatario}."
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False, f"Error al enviar el correo: {e}"
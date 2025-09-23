# notificaciones.py

import smtplib
from email.message import EmailMessage
import os

REMITENTE_EMAIL = os.environ.get('EMAIL_USER', 'eleazararriola11@gmail.com')
REMITENTE_PASSWORD = os.environ.get('EMAIL_PASS', 'qmoctgsginmdxbqw')
DESTINATARIO_EMAIL = 'rosalesroy11@gmail.com' 
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def enviar_correo(asunto, cuerpo_html):
    """
    Envía un correo electrónico con el contenido de las alertas.
    """
    # <<< LÍNEA CORREGIDA >>>
    # Ahora solo comprueba que las variables no estén vacías.
    if not REMITENTE_EMAIL or not REMITENTE_PASSWORD:
        print("ERROR: El correo o la contraseña no están configurados.")
        return False, "Credenciales de correo no configuradas."

    # Crear el mensaje
    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = REMITENTE_EMAIL
    msg['To'] = DESTINATARIO_EMAIL
    msg.set_content("Este es un correo con formato HTML. Por favor, activa la vista HTML.")
    
    # Añadir la versión HTML
    msg.add_alternative(cuerpo_html, subtype='html')

    try:
        # Conectar con el servidor SMTP y enviar
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Activar seguridad
            server.login(REMITENTE_EMAIL, REMITENTE_PASSWORD)
            server.send_message(msg)
            print("Correo de alerta enviado exitosamente.")
            return True, "Correo enviado exitosamente."
    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False, f"Error al enviar el correo: {e}"
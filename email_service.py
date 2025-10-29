import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import string

class EmailService:
    """Servicio para envío de correos electrónicos"""
    
    # Configuración del servidor SMTP (Gmail como ejemplo)
    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    # Para Outlook/Hotmail:
    # SMTP_SERVER = "smtp-mail.outlook.com"
    # SMTP_PORT = 587
    
    EMAIL_FROM = "denisaguilon@gmail.com"  # Cambiar esto al correo de la empresa/due;o
    EMAIL_PASSWORD = "lwotxkbifwgohvwt"  # Usa contraseña de aplicación de Gmail
    
    @staticmethod
    def generar_codigo_verificacion(longitud=6):
        """Genera un código de verificación aleatorio"""
        caracteres = string.digits
        codigo = ''.join(random.choice(caracteres) for _ in range(longitud))
        return codigo
    
    @staticmethod
    def enviar_codigo_verificacion(email_destino, codigo):
        """Envía el código de verificación al correo del usuario"""
        try:
            # Crear mensaje
            mensaje = MIMEMultipart("alternative")
            mensaje["Subject"] = "Codigo de Verificacion - Farma PLUS"
            mensaje["From"] = EmailService.EMAIL_FROM
            mensaje["To"] = email_destino
            mensaje.set_charset('utf-8')
            
            # Contenido del correo en HTML
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #3A9D5A; text-align: center;">Farma PLUS</h2>
                        <h3 style="color: #333333;">Recuperacion de Contrasena</h3>
                        <p style="color: #666666; font-size: 16px;">
                            Has solicitado recuperar tu contrasena. Usa el siguiente codigo de verificacion:
                        </p>
                        <div style="background-color: #f0f0f0; padding: 20px; text-align: center; border-radius: 5px; margin: 20px 0;">
                            <h1 style="color: #3A9D5A; letter-spacing: 5px; margin: 0;">{codigo}</h1>
                        </div>
                        <p style="color: #666666; font-size: 14px;">
                            Este codigo es valido por 10 minutos.
                        </p>
                        <p style="color: #999999; font-size: 12px; margin-top: 30px;">
                            Si no solicitaste este codigo, por favor ignora este correo.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            # Adjuntar HTML con codificación UTF-8
            parte_html = MIMEText(html, "html", "utf-8")
            mensaje.attach(parte_html)
            
            # Enviar correo
            with smtplib.SMTP(EmailService.SMTP_SERVER, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.EMAIL_FROM, EmailService.EMAIL_PASSWORD)
                # Usar sendmail en lugar de send_message para mejor compatibilidad
                server.sendmail(
                    EmailService.EMAIL_FROM,
                    email_destino,
                    mensaje.as_string().encode('utf-8')
                )
            
            return True, "Código enviado exitosamente"
            
        except Exception as e:
            return False, f"Error al enviar correo: {str(e)}"
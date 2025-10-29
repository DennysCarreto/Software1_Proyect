import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, QDialog)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QAction
from PyQt6.QtCore import Qt, QSize, QTimer
from datetime import datetime, timedelta
from principal import MainWindow 
import mysql.connector
from conexion import ConexionBD
from email_service import EmailService
import re
#from principal import MainWindow

class ValidadorPassword:
    """Clase para validar políticas de contraseña"""
    
    @staticmethod
    def validar_password(password):
        """
        Valida que la contraseña cumpla con las políticas:
        - Mínimo 8 caracteres
        - Al menos una letra mayúscula
        - Al menos una letra minúscula
        - Al menos un número
        - Al menos un carácter especial
        """
        errores = []
        
        if len(password) < 8:
            errores.append("Mínimo 8 caracteres")
        
        if not re.search(r'[A-Z]', password):
            errores.append("Al menos una letra mayúscula")
        
        if not re.search(r'[a-z]', password):
            errores.append("Al menos una letra minúscula")
        
        if not re.search(r'\d', password):
            errores.append("Al menos un número")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errores.append("Al menos un carácter especial (!@#$%^&*...)")
        
        return len(errores) == 0, errores


class CambiarPasswordDialog(QDialog):
    """Diálogo para cambiar la contraseña después de verificar el código"""
    def __init__(self, username, parent=None):
        super().__init__(parent)
        self.username = username
        self.setWindowTitle("Cambiar Contraseña")
        self.setFixedSize(450, 400)
        self.setStyleSheet("background-color: #1A202C;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel("Establecer Nueva Contraseña")
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Políticas de contraseña
        policies_label = QLabel(
            "La contraseña debe cumplir:\n"
            "• Mínimo 8 caracteres\n"
            "• Al menos una mayúscula\n"
            "• Al menos una minúscula\n"
            "• Al menos un número\n"
            "• Al menos un carácter especial"
        )
        policies_label.setStyleSheet("""
            color: #A0AEC0;
            font-size: 11px;
            margin-bottom: 10px;
        """)
        policies_label.setWordWrap(True)
        layout.addWidget(policies_label)
        
        # Estilos
        input_style = """
            QLineEdit {
                background-color: #2D3A48;
                border: 1px solid #3A9D5A;
                border-radius: 5px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
        """
        
        # Nueva contraseña
        self.new_password_input = QLineEdit()
        self.new_password_input.setPlaceholderText("Nueva Contraseña")
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setStyleSheet(input_style)
        layout.addWidget(self.new_password_input)
        
        # Confirmar contraseña
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("Confirmar Contraseña")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet(input_style)
        layout.addWidget(self.confirm_password_input)
        
        layout.addSpacing(10)
        
        # Botones
        button_style = """
            QPushButton {
                background-color: #3A9D5A;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #278E43;
            }
        """
        
        cambiar_btn = QPushButton("Cambiar Contraseña")
        cambiar_btn.setStyleSheet(button_style)
        cambiar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cambiar_btn.clicked.connect(self.cambiar_password)
        layout.addWidget(cambiar_btn)
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2D3748;
            }
        """)
        cancelar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancelar_btn.clicked.connect(self.reject)
        layout.addWidget(cancelar_btn)
    
    def encriptarContraseña(self, contrasena):
        """Encripta la contraseña usando el método César"""
        clave = 3
        contrasena_encriptada = ""
        for caracter in contrasena:
            if caracter.isalpha():
                nuevo_caracter = chr(((ord(caracter) - ord('a' if caracter.islower() else 'A') + clave) % 26) + ord('a' if caracter.islower() else 'A'))
                contrasena_encriptada += nuevo_caracter
            else:
                contrasena_encriptada += caracter
        return contrasena_encriptada
    
    def cambiar_password(self):
        """Cambia la contraseña del usuario en la base de datos"""
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()
        
        # Validar campos vacíos
        if not new_password or not confirm_password:
            QMessageBox.warning(
                self,
                "Campos vacíos",
                "Por favor completa todos los campos.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Validar que las contraseñas coincidan
        if new_password != confirm_password:
            QMessageBox.warning(
                self,
                "Contraseñas no coinciden",
                "Las contraseñas ingresadas no son iguales.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        # Validar políticas de contraseña
        es_valida, errores = ValidadorPassword.validar_password(new_password)
        if not es_valida:
            mensaje_error = "La contraseña no cumple con los siguientes requisitos:\n\n"
            mensaje_error += "\n".join(f"• {error}" for error in errores)
            QMessageBox.warning(
                self,
                "Contraseña no válida",
                mensaje_error,
                QMessageBox.StandardButton.Ok
            )
            return
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            
            # Encriptar nueva contraseña
            password_encriptada = self.encriptarContraseña(new_password)
            
            # Actualizar contraseña en la base de datos
            query = "UPDATE Usuario SET Contraseña = %s WHERE Usuario = %s"
            cursor.execute(query, (password_encriptada, self.username))
            conexion.commit()
            
            QMessageBox.information(
                self,
                "Éxito",
                "Tu contraseña ha sido actualizada correctamente.\nYa puedes iniciar sesión con tu nueva contraseña.",
                QMessageBox.StandardButton.Ok
            )
            
            cursor.close()
            conexion.close()
            
            self.accept()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo actualizar la contraseña:\n{err}",
                QMessageBox.StandardButton.Ok
            )

class VerificarCodigoDialog(QDialog):
    """Diálogo para verificar el código enviado por correo"""
    def __init__(self, codigo_enviado, username, tiempo_expiracion, parent=None):
        super().__init__(parent)
        self.codigo_enviado = codigo_enviado
        self.username = username
        self.tiempo_expiracion = tiempo_expiracion
        self.setWindowTitle("Verificar Código")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #1A202C;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel("Verificación de Código")
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Instrucciones
        info_label = QLabel(
            f"Hemos enviado un código de verificación al correo registrado.\n\n"
            f"Por favor, ingresa el código que recibiste:"
        )
        info_label.setStyleSheet("""
            color: #A0AEC0;
            font-size: 12px;
            margin-bottom: 10px;
        """)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Timer label
        self.timer_label = QLabel()
        self.timer_label.setStyleSheet("""
            color: #3A9D5A;
            font-size: 14px;
            font-weight: bold;
        """)
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)
        
        # Iniciar temporizador
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.actualizar_tiempo)
        self.timer.start(1000)  # Actualizar cada segundo
        self.actualizar_tiempo()
        
        # Campo de código
        input_style = """
            QLineEdit {
                background-color: #2D3A48;
                border: 1px solid #3A9D5A;
                border-radius: 5px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 18px;
                letter-spacing: 5px;
                text-align: center;
            }
        """
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("000000")
        self.codigo_input.setMaxLength(6)
        self.codigo_input.setStyleSheet(input_style)
        self.codigo_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.codigo_input)
        
        layout.addSpacing(10)
        
        # Botones
        button_style = """
            QPushButton {
                background-color: #3A9D5A;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #278E43;
            }
        """
        
        verificar_btn = QPushButton("Verificar")
        verificar_btn.setStyleSheet(button_style)
        verificar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        verificar_btn.clicked.connect(self.verificar_codigo)
        layout.addWidget(verificar_btn)
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2D3748;
            }
        """)
        cancelar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancelar_btn.clicked.connect(self.reject)
        layout.addWidget(cancelar_btn)
    
    def actualizar_tiempo(self):
        """Actualiza el tiempo restante"""
        tiempo_restante = self.tiempo_expiracion - datetime.now()
        
        if tiempo_restante.total_seconds() <= 0:
            self.timer.stop()
            self.timer_label.setText("⏱️ Código expirado")
            self.timer_label.setStyleSheet("color: #E53E3E; font-size: 14px; font-weight: bold;")
            QMessageBox.warning(
                self,
                "Código expirado",
                "El código de verificación ha expirado.\nPor favor, solicita uno nuevo.",
                QMessageBox.StandardButton.Ok
            )
            self.reject()
        else:
            minutos = int(tiempo_restante.total_seconds() // 60)
            segundos = int(tiempo_restante.total_seconds() % 60)
            self.timer_label.setText(f"⏱️ Tiempo restante: {minutos:02d}:{segundos:02d}")
    
    def verificar_codigo(self):
        """Verifica el código ingresado"""
        codigo_ingresado = self.codigo_input.text().strip()
        
        if not codigo_ingresado:
            QMessageBox.warning(
                self,
                "Campo vacío",
                "Por favor ingresa el código de verificación.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        if codigo_ingresado == self.codigo_enviado:
            self.timer.stop()
            QMessageBox.information(
                self,
                "Código verificado",
                "Código correcto. Ahora puedes establecer tu nueva contraseña.",
                QMessageBox.StandardButton.Ok
            )
            self.accept()
            
            # Abrir diálogo para cambiar contraseña
            dialog = CambiarPasswordDialog(self.username, self.parent())
            dialog.exec()
        else:
            QMessageBox.warning(
                self,
                "Código incorrecto",
                "El código ingresado no es válido.\nPor favor verifica e intenta nuevamente.",
                QMessageBox.StandardButton.Ok
            )

class RecuperarPasswordDialog(QDialog):
    """Diálogo para recuperar contraseña"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recuperar Contraseña")
        self.setFixedSize(400, 300)
        self.setStyleSheet("background-color: #1A202C;")
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título
        title_label = QLabel("Recuperar Contraseña")
        title_label.setStyleSheet("""
            color: #FFFFFF;
            font-size: 20px;
            font-weight: bold;
            margin-bottom: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Instrucciones
        info_label = QLabel("Ingresa tu nombre de usuario para recuperar tu contraseña")
        info_label.setStyleSheet("""
            color: #A0AEC0;
            font-size: 12px;
            margin-bottom: 10px;
        """)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # Campo de usuario
        input_style = """
            QLineEdit {
                background-color: #2D3A48;
                border: 1px solid #3A9D5A;
                border-radius: 5px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
        """
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nombre de Usuario")
        self.username_input.setStyleSheet(input_style)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(10)
        
        # Botones
        button_style = """
            QPushButton {
                background-color: #3A9D5A;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #278E43;
            }
        """
        
        recuperar_btn = QPushButton("Enviar Código")
        recuperar_btn.setStyleSheet(button_style)
        recuperar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        recuperar_btn.clicked.connect(self.enviar_codigo)
        layout.addWidget(recuperar_btn)
        
        cancelar_btn = QPushButton("Cancelar")
        cancelar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2D3748;
            }
        """)
        cancelar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancelar_btn.clicked.connect(self.reject)
        layout.addWidget(cancelar_btn)
    
    def enviar_codigo(self):
        """Envía el código de verificación al correo del usuario"""
        username = self.username_input.text().strip()
        
        if not username:
            QMessageBox.warning(
                self,
                "Campo vacío",
                "Por favor ingresa tu nombre de usuario.",
                QMessageBox.StandardButton.Ok
            )
            return
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # Buscar usuario activo y obtener su correo
            query = "SELECT Correo FROM Usuario WHERE Usuario = %s AND Activo = 1"
            cursor.execute(query, (username,))
            resultado = cursor.fetchone()
            
            if resultado:
                correo = resultado["Correo"]
                
                # Generar código de verificación
                codigo = EmailService.generar_codigo_verificacion()
                
                # Enviar correo
                exito, mensaje = EmailService.enviar_codigo_verificacion(correo, codigo)
                
                if exito:
                    # Ocultar parte del correo por seguridad
                    correo_censurado = correo[:3] + "***" + correo[correo.index("@"):]
                    
                    QMessageBox.information(
                        self,
                        "Código enviado",
                        f"Se ha enviado un código de verificación a:\n{correo_censurado}",
                        QMessageBox.StandardButton.Ok
                    )
                    
                    self.accept()
                    
                    # Abrir diálogo de verificación
                    tiempo_expiracion = datetime.now() + timedelta(minutes=10)
                    dialog = VerificarCodigoDialog(codigo, username, tiempo_expiracion, self.parent())
                    dialog.exec()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"No se pudo enviar el correo:\n{mensaje}",
                        QMessageBox.StandardButton.Ok
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Usuario no encontrado",
                    "El usuario no existe o está inactivo.",
                    QMessageBox.StandardButton.Ok
                )
            
            cursor.close()
            conexion.close()
            
        except mysql.connector.Error as err:
            QMessageBox.critical(
                self,
                "Error de conexión",
                f"No se pudo conectar a la base de datos:\n{err}",
                QMessageBox.StandardButton.Ok
            )

    # def desencriptarContraseña(self, contrasena_encriptada):
    #     """Desencripta la contraseña usando el método César inverso"""
    #     clave = 3
    #     contrasena_original = ""
        
    #     for caracter in contrasena_encriptada:
    #         if caracter.isalpha():
    #             # Desplazar en sentido inverso
    #             nuevo_caracter = chr(((ord(caracter) - ord('a' if caracter.islower() else 'A') - clave) % 26) + ord('a' if caracter.islower() else 'A'))
    #             contrasena_original += nuevo_caracter
    #         else:
    #             contrasena_original += caracter
        
    #     return contrasena_original
    
    # def recuperar_password(self):
    #     """Recupera la contraseña del usuario"""
    #     username = self.username_input.text().strip()
        
    #     if not username:
    #         QMessageBox.warning(
    #             self,
    #             "Campo vacío",
    #             "Por favor ingresa tu nombre de usuario.",
    #             QMessageBox.StandardButton.Ok
    #         )
    #         return
        
    #     try:
    #         conexion = ConexionBD.obtener_conexion()
    #         cursor = conexion.cursor(dictionary=True)
            
    #         # Buscar usuario activo
    #         query = "SELECT Contraseña FROM Usuario WHERE Usuario = %s AND Activo = 1"
    #         cursor.execute(query, (username,))
    #         resultado = cursor.fetchone()
            
    #         if resultado:
    #             # Desencriptar contraseña
    #             password_encriptada = resultado["Contraseña"]
    #             password_original = self.desencriptarContraseña(password_encriptada)
                
    #             # Mostrar contraseña
    #             QMessageBox.information(
    #                 self,
    #                 "Contraseña Recuperada",
    #                 f"Tu contraseña es: {password_original}\n\nPor favor, cámbiala después de iniciar sesión.",
    #                 QMessageBox.StandardButton.Ok
    #             )
    #             self.accept()
    #         else:
    #             QMessageBox.warning(
    #                 self,
    #                 "Usuario no encontrado",
    #                 "El usuario no existe o está inactivo.",
    #                 QMessageBox.StandardButton.Ok
    #             )
            
    #         cursor.close()
    #         conexion.close()
            
    #     except mysql.connector.Error as err:
    #         QMessageBox.critical(
    #             self,
    #             "Error de conexión",
    #             f"No se pudo conectar a la base de datos:\n{err}",
    #             QMessageBox.StandardButton.Ok
    #         )


class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Farma PLUS - Login")
        self.setFixedSize(500, 600)
        self.setStyleSheet("background-color: #1A202C;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        layout.addStretch() # Para centrar verticalmente

        logo_container = QWidget()
        logo_container.setFixedSize(250, 180)
        logo_container.setStyleSheet("background-color: #2D3748; border-radius: 15px;")
        logo_layout = QVBoxLayout(logo_container)
        logo_label = QLabel()
        logo_pixmap = QPixmap("images/logo.png")
        logo_label.setPixmap(logo_pixmap.scaled(200, 150, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_layout.addWidget(logo_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(logo_container, alignment=Qt.AlignmentFlag.AlignCenter)
        
        input_style = """
            QLineEdit {
                background-color: #2D3A48;
                border: 1px solid #3A9D5A;
                border-radius: 5px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-family: "Roboto";
                font-size: 15px;       
            }
        """
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Nombre de Usuario")
        self.user_input.setFixedSize(300, 40)
        self.user_input.setStyleSheet(input_style)
        layout.addWidget(self.user_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setPlaceholderText("Contraseña")
        self.pwd_input.setFixedSize(300, 40)
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pwd_input.setStyleSheet(input_style)
        
        pixmap_closed = QPixmap("images/ocultar.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        pixmap_open = QPixmap("images/abrir.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        self.eye_icon_closed = QIcon(pixmap_closed)
        self.eye_icon_open = QIcon(pixmap_open)
        
        self.toggle_password_action = QAction(self.eye_icon_closed, "Mostrar/Ocultar Contraseña", self)
        
        self.pwd_input.addAction(self.toggle_password_action, QLineEdit.ActionPosition.TrailingPosition)
        
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)

        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Enlace "¿Olvidaste tu contraseña?"
        forgot_password_label = QLabel('<a href="#" style="color: #3A9D5A; text-decoration: none;">¿Olvidaste tu contraseña?</a>')
        forgot_password_label.setStyleSheet("font-size: 12px;")
        forgot_password_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        forgot_password_label.setFixedWidth(300)
        forgot_password_label.setCursor(Qt.CursorShape.PointingHandCursor)
        forgot_password_label.linkActivated.connect(self.abrir_recuperar_password)
        layout.addWidget(forgot_password_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(10)
        
        login_button = QPushButton("Ingresar")
        login_button.setFixedSize(300, 45)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3A9D5A;
                color: #FFFFFF;
                border-radius: 5px; 
                font-size: 16px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #278E43;
            }
        """)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # ### <<< INICIO: CONECTAR LA TECLA ENTER >>> ###
        # Conectar la señal returnPressed de ambos campos de texto a la función de login.
        self.user_input.returnPressed.connect(self.login)
        self.pwd_input.returnPressed.connect(self.login)
        # ### <<< FIN: CONECTAR LA TECLA ENTER >>> ###
        
        layout.addStretch() # Para centrar verticalmente
    
    def abrir_recuperar_password(self):
        """Abre el diálogo de recuperación de contraseña"""
        dialog = RecuperarPasswordDialog(self)
        dialog.exec()

    def toggle_password_visibility(self):
        if self.pwd_input.echoMode() == QLineEdit.EchoMode.Password:
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_action.setIcon(self.eye_icon_open)
        else:
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_action.setIcon(self.eye_icon_closed)

    def encriptarContraseña(self,contrasena):
        clave = 3
        contrasena_encriptada = ""
        for caracter in contrasena:
            if caracter.isalpha():
                nuevo_caracter = chr(((ord(caracter) - ord('a' if caracter.islower() else 'A') + clave) % 26) + ord('a' if caracter.islower() else 'A'))
                contrasena_encriptada += nuevo_caracter
            else:
                contrasena_encriptada += caracter
        return contrasena_encriptada
    
    
    def login(self):
        """Función para validar el login"""
        username = self.user_input.text()
        password = self.pwd_input.text()

        password_encriptada = self.encriptarContraseña(password)

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            query = "SELECT * FROM Usuario WHERE Usuario = %s AND Contraseña = %s AND Activo = 1"
            cursor.execute(query, (username, password_encriptada))
            resultado = cursor.fetchone()

            if resultado:
                cargo = resultado["cargo"]
                
                self.main_window = MainWindow(cargo)
                self.main_window.show()
                self.close()
            else:
                QMessageBox.warning(
                    self,
                    "Error de login",
                    "Usuario o contraseña incorrectos o cuenta inactiva.",
                    QMessageBox.StandardButton.Ok
                )

            cursor.close()
            conexion.close()

        except mysql.connector.Error as err:
            QMessageBox.critical(
                self,
                "Error de conexión",
                f"No se pudo conectar a la base de datos:\n{err}",
                QMessageBox.StandardButton.Ok
            )
    
    def open_main_app(self):
        """Abre la aplicación principal después del login exitoso"""
        
        from principal import MainWindow  # Evita import circular
        # Abrir ventana principal
        self.main_window = MainWindow()
        self.main_window.show()

        # Cerrar la ventana de login
        self.close()
        
        
# Codigo para probar solo la pesta;a login
#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    window = LoginWindow()
#    window.show()
#    sys.exit(app.exec())
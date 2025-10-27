import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox, QDialog)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QAction
from PyQt6.QtCore import Qt, QSize
from principal import MainWindow 
import mysql.connector
from conexion import ConexionBD
#from principal import MainWindow

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
        
        recuperar_btn = QPushButton("Recuperar")
        recuperar_btn.setStyleSheet(button_style)
        recuperar_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        recuperar_btn.clicked.connect(self.recuperar_password)
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
    
    def desencriptarContraseña(self, contrasena_encriptada):
        """Desencripta la contraseña usando el método César inverso"""
        clave = 3
        contrasena_original = ""
        
        for caracter in contrasena_encriptada:
            if caracter.isalpha():
                # Desplazar en sentido inverso
                nuevo_caracter = chr(((ord(caracter) - ord('a' if caracter.islower() else 'A') - clave) % 26) + ord('a' if caracter.islower() else 'A'))
                contrasena_original += nuevo_caracter
            else:
                contrasena_original += caracter
        
        return contrasena_original
    
    def recuperar_password(self):
        """Recupera la contraseña del usuario"""
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
            
            # Buscar usuario activo
            query = "SELECT Contraseña FROM Usuario WHERE Usuario = %s AND Activo = 1"
            cursor.execute(query, (username,))
            resultado = cursor.fetchone()
            
            if resultado:
                # Desencriptar contraseña
                password_encriptada = resultado["Contraseña"]
                password_original = self.desencriptarContraseña(password_encriptada)
                
                # Mostrar contraseña
                QMessageBox.information(
                    self,
                    "Contraseña Recuperada",
                    f"Tu contraseña es: {password_original}\n\nPor favor, cámbiala después de iniciar sesión.",
                    QMessageBox.StandardButton.Ok
                )
                self.accept()
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
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtGui import QPixmap, QFont, QIcon, QAction
from PyQt6.QtCore import Qt, QSize
from principal import MainWindow 
import mysql.connector
from conexion import ConexionBD
#from principal import MainWindow
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
                border: 1px solid #3A9D5A; /* <<< CAMBIO AQUÍ */
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
        
        # ### <<< INICIO: LÓGICA DEL ICONO DE OJO >>> ###
        pixmap_closed = QPixmap("images/ocultar.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        pixmap_open = QPixmap("images/abrir.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

        # Creamos el QIcon a partir del Pixmap redimensionado
        self.eye_icon_closed = QIcon(pixmap_closed)
        self.eye_icon_open = QIcon(pixmap_open)
        
        self.toggle_password_action = QAction(self.eye_icon_closed, "Mostrar/Ocultar Contraseña", self)
        
        self.pwd_input.addAction(self.toggle_password_action, QLineEdit.ActionPosition.TrailingPosition)
        
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        # ### <<< FIN: LÓGICA DEL ICONO DE OJO >>> ###

        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addSpacing(10)
        
        login_button = QPushButton("Ingresar")
        login_button.setFixedSize(300, 45)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #3A9D5A; /* <<< CAMBIO AQUÍ */
                color: #FFFFFF; /* Cambiamos el texto a blanco para mejor contraste */
                border-radius: 5px; 
                font-size: 16px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #278E43; /* Un verde un poco más oscuro para el hover */
            }
        """)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch() # Para centrar verticalmente
    
    def toggle_password_visibility(self):
        """
        Cambia el modo de visualización de la contraseña y el icono.
        """
        if self.pwd_input.echoMode() == QLineEdit.EchoMode.Password:
            # Si está oculto, mostrarlo
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_action.setIcon(self.eye_icon_open)
        else:
            # Si se está mostrando, ocultarlo
            self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_action.setIcon(self.eye_icon_closed)

    def encriptarContraseña(self,contrasena):
        clave = 3  # Desplazamiento para el cifrado (puedes elegir cualquier número)

        contrasena_encriptada = ""
        for caracter in contrasena:
            if caracter.isalpha():  # Verifica si es una letra
                # Calcula el nuevo carácter desplazando en la clave
                nuevo_caracter = chr(((ord(caracter) - ord('a' if caracter.islower() else 'A') + clave) % 26) + ord('a' if caracter.islower() else 'A'))
                contrasena_encriptada += nuevo_caracter
            else:
                contrasena_encriptada += caracter  # Mantén otros caracteres sin cambios
    
        return contrasena_encriptada
    
    
    def login(self):
        """Función para validar el login"""
        username = self.user_input.text()
        password = self.pwd_input.text()

        # Encriptar contraseña antes de comparar
        password_encriptada = self.encriptarContraseña(password)

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)

            # Consulta con verificación de usuario activo
            query = """
                SELECT * FROM Usuario
                WHERE Usuario = %s AND Contraseña = %s AND Activo = 1
            """
            cursor.execute(query, (username, password_encriptada))
            resultado = cursor.fetchone()

            if resultado:
                # Usuario válido, obtener el cargo
                cargo = resultado["cargo"]

                # Abrir la ventana principal con el cargo
                from principal import MainWindow  # Evita import circular
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
        
        # # Ventana principal
        # QMessageBox.information(
        #     self,
        #     "Login exitoso",
        #     "Bienvenido al sistema Farma PLUS!",
        #     QMessageBox.StandardButton.Ok
        # )
    
        # Abrir ventana principal
        self.main_window = MainWindow()
        self.main_window.show()

        # Cerrar la ventana de login
        self.close()
        
        

#if __name__ == "__main__":
#    app = QApplication(sys.argv)
#    window = LoginWindow()
#    window.show()
#    sys.exit(app.exec())
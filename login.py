import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt6.QtGui import QPixmap, QFont, QIcon
from PyQt6.QtCore import Qt, QSize
from principal import MainWindow 
import mysql.connector
from conexion import ConexionBD
#from principal import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Ventana principal
        self.setWindowTitle("Farma PLUS - Login")
        self.setFixedSize(500, 600)
        self.setStyleSheet("background-color: #45B5AA;")  # Color turquesa 
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Titulo de bienvenida
        welcome_label = QLabel("Bienvenido...")
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #333333;")
        layout.addWidget(welcome_label)
        
        # Logo
        logo_container = QWidget()
        logo_container.setFixedSize(220, 220)
        logo_container.setStyleSheet("background-color: #D1F0EC; border-radius: 10px;")
        
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        logo_label = QLabel()
        # Tener un archivo logo.png en la misma carpeta o especificar la ruta correcta
        logo_pixmap = QPixmap("images/logo.png")
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(180, 180, Qt.AspectRatioMode.KeepAspectRatio))
        else:
            # Si no hay logo disponible, mostrar texto
            logo_label.setText("FARMA PLUS")
            logo_label.setFont(QFont("Arial", 18, QFont.Weight.Bold))
            logo_label.setStyleSheet("color: #0B6654;")
        
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_layout.addWidget(logo_label)
        layout.addWidget(logo_container)
        
        # Espacio
        layout.addSpacing(20)
        
        # Usuario
        user_label = QLabel("Usuario")
        user_label.setFont(QFont("Arial", 16))
        user_label.setStyleSheet("color: #333333;")
        layout.addWidget(user_label)
        
        self.user_input = QLineEdit()
        self.user_input.setFixedSize(230, 30)
        self.user_input.setStyleSheet("background-color: white; border-radius: 3px;")
        layout.addWidget(self.user_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Espacio
        layout.addSpacing(10)
        
        # Contraseña
        pwd_label = QLabel("Contraseña")
        pwd_label.setFont(QFont("Arial", 16))
        pwd_label.setStyleSheet("color: #333333;")
        layout.addWidget(pwd_label)
        
        self.pwd_input = QLineEdit()
        self.pwd_input.setFixedSize(230, 30)
        self.pwd_input.setStyleSheet("background-color: white; border-radius: 3px;")
        self.pwd_input.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addWidget(self.pwd_input, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Espacio
        layout.addSpacing(20)
        
        # Botón de login
        login_button = QPushButton("Ingresar")
        login_button.setFixedSize(120, 40)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #0B6654;
                color: white;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0A5A4A;
            }
        """)
        login_button.clicked.connect(self.login)
        layout.addWidget(login_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Espacio al final
        layout.addSpacing(30)
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
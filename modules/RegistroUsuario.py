from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, 
                            QPushButton, QWidget, QComboBox, QLineEdit, QMessageBox)
from PyQt6.QtGui import QPixmap, QIntValidator, QIcon, QAction
from PyQt6.QtCore import Qt
import hashlib
import re
import mysql.connector
from conexion import ConexionBD

class VentanaRegistro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro de Usuario")
        # Obtener dimensiones de la pantalla y ajustar
        from PyQt6.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        window_height = min(800, screen.height() - 100)  # Máximo 800 o altura de pantalla menos margen
        self.setGeometry(200, 30, 520, window_height)
        self.setStyleSheet("background-color: #1A202C;")
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Crear scroll area para contenido largo
        from PyQt6.QtWidgets import QScrollArea
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #1A202C;
            }
            QScrollBar:vertical {
                background-color: #2D3A48;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #3A9D5A;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #278E43;
            }
        """)
        
        scroll_content = QWidget()
        layout_vertical = QVBoxLayout(scroll_content)
        layout_vertical.setSpacing(10)
        layout_vertical.setContentsMargins(30, 30, 30, 30)
        
        # Estilo para etiquetas
        label_style = """
            QLabel {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: bold;
            }
        """
        
        # Estilo para campos de entrada
        input_style = """
            QLineEdit {
                background-color: #2D3A48;
                border: 1px solid #3A9D5A;
                border-radius: 5px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 2px solid #3A9D5A;
            }
        """
        
        combo_style = """
            QComboBox {
                background-color: #2D3A48;
                border: 1px solid #3A9D5A;
                border-radius: 5px;
                padding: 8px 12px;
                color: #FFFFFF;
                font-size: 14px;
            }
            QComboBox:hover {
                border: 2px solid #3A9D5A;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #3A9D5A;
                margin-right: 10px;
            }
        """
        
        # Título
        titulo = QLabel("Registro de Nuevo Usuario")
        titulo.setStyleSheet("color: #FFFFFF; font-size: 20px; font-weight: bold; margin-bottom: 20px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_vertical.addWidget(titulo)
        
        # Campos de registro
        self.etiquetaN = QLabel("Nombre:")
        self.etiquetaN.setStyleSheet(label_style)
        self.setNombre = QLineEdit(self)
        self.setNombre.setPlaceholderText("Ingresa tu nombre")
        self.setNombre.setStyleSheet(input_style)
        layout_vertical.addWidget(self.etiquetaN)
        layout_vertical.addWidget(self.setNombre)
        
        self.etiquetaA = QLabel("Apellido:")
        self.etiquetaA.setStyleSheet(label_style)
        self.setApellido = QLineEdit(self)
        self.setApellido.setPlaceholderText("Ingresa tu apellido")
        self.setApellido.setStyleSheet(input_style)
        layout_vertical.addWidget(self.etiquetaA)
        layout_vertical.addWidget(self.setApellido)
        
        # Campo de correo electrónico
        self.etiquetaCorreo = QLabel("Correo Electrónico:")
        self.etiquetaCorreo.setStyleSheet(label_style)
        self.setCorreo = QLineEdit(self)
        self.setCorreo.setPlaceholderText("ejemplo@correo.com")
        self.setCorreo.setStyleSheet(input_style)
        layout_vertical.addWidget(self.etiquetaCorreo)
        layout_vertical.addWidget(self.setCorreo)
        
        # Teléfono con extensión
        self.etiquetaT = QLabel("Teléfono:")
        self.etiquetaT.setStyleSheet(label_style)
        layout_vertical.addWidget(self.etiquetaT)
        
        tel_layout = QHBoxLayout()
        self.extension_combo = QComboBox()
        self.extension_combo.addItems([
            "+502 (GT)",
            "+1 (US/CA)",
            "+52 (MX)",
            "+503 (SV)",
            "+504 (HN)",
            "+505 (NI)",
            "+506 (CR)",
            "+507 (PA)",
            "+34 (ES)",
            "+591 (BO)"
        ])
        self.extension_combo.setStyleSheet(combo_style)
        self.extension_combo.setFixedWidth(120)
        
        self.setTel = QLineEdit(self)
        self.setTel.setPlaceholderText("Ej: 12345678")
        self.setTel.setStyleSheet(input_style)
        self.setTel.setMaxLength(15)
        
        tel_layout.addWidget(self.extension_combo)
        tel_layout.addWidget(self.setTel)
        layout_vertical.addLayout(tel_layout)
        
        self.etiquetaNU = QLabel("Nombre de Usuario:")
        self.etiquetaNU.setStyleSheet(label_style)
        self.setNombreUsuario = QLineEdit(self)
        self.setNombreUsuario.setPlaceholderText("Usuario único")
        self.setNombreUsuario.setStyleSheet(input_style)
        layout_vertical.addWidget(self.etiquetaNU)
        layout_vertical.addWidget(self.setNombreUsuario)
        
        self.etiquetaC = QLabel("Contraseña:")
        self.etiquetaC.setStyleSheet(label_style)
        self.setContraseña = QLineEdit(self)
        self.setContraseña.setPlaceholderText("Mínimo 8 caracteres")
        self.setContraseña.setEchoMode(QLineEdit.EchoMode.Password)
        self.setContraseña.setStyleSheet(input_style)
        
        # Agregar icono de ojo para mostrar/ocultar contraseña
        pixmap_closed = QPixmap("images/ocultar.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        pixmap_open = QPixmap("images/abrir.png").scaled(24, 24, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        
        from PyQt6.QtGui import QIcon, QAction
        self.eye_icon_closed = QIcon(pixmap_closed)
        self.eye_icon_open = QIcon(pixmap_open)
        
        self.toggle_password_action = QAction(self.eye_icon_closed, "Mostrar/Ocultar Contraseña", self)
        self.setContraseña.addAction(self.toggle_password_action, QLineEdit.ActionPosition.TrailingPosition)
        self.toggle_password_action.triggered.connect(self.toggle_password_visibility)
        
        layout_vertical.addWidget(self.etiquetaC)
        layout_vertical.addWidget(self.setContraseña)
        
        # Requisitos de contraseña
        requisitos = QLabel(
            "• Mínimo 8 caracteres\n"
            "• Al menos una mayúscula\n"
            "• Al menos un número\n"
            "• Al menos un carácter especial (!@#$%^&*)"
        )
        requisitos.setStyleSheet("color: #A0AEC0; font-size: 11px; margin-left: 5px;")
        layout_vertical.addWidget(requisitos)
        
        self.etiqueta_cargo = QLabel("Cargo:")
        self.etiqueta_cargo.setStyleSheet(label_style)
        self.set_tipo_Usuario = QComboBox()
        self.set_tipo_Usuario.addItems(["Empleado", "Gerente"])
        self.set_tipo_Usuario.setStyleSheet(combo_style)
        layout_vertical.addWidget(self.etiqueta_cargo)
        layout_vertical.addWidget(self.set_tipo_Usuario)
        
        layout_vertical.addSpacing(20)
        
        # Botones
        button_style = """
            QPushButton {
                background-color: #3A9D5A;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 12px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #278E43;
            }
        """
        
        self.botonRegistrarme = QPushButton("Registrarme")
        self.botonRegistrarme.setStyleSheet(button_style)
        self.botonRegistrarme.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_vertical.addWidget(self.botonRegistrarme)
        
        boton_regresar = QPushButton("Regresar")
        boton_regresar.setStyleSheet("""
            QPushButton {
                background-color: #4A5568;
                color: #FFFFFF;
                border-radius: 5px;
                padding: 12px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #2D3748;
            }
        """)
        boton_regresar.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_vertical.addWidget(boton_regresar)
        
        # Configurar scroll area
        scroll.setWidget(scroll_content)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll)
        
        boton_regresar.clicked.connect(self.cerrar_ventana)
        self.botonRegistrarme.clicked.connect(self.registrar)

    def toggle_password_visibility(self):
        """Cambia el modo de visualización de la contraseña y el icono"""
        if self.setContraseña.echoMode() == QLineEdit.EchoMode.Password:
            self.setContraseña.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_password_action.setIcon(self.eye_icon_open)
        else:
            self.setContraseña.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_password_action.setIcon(self.eye_icon_closed)

    def validar_correo(self, correo):
        """Valida que el correo tenga un formato válido"""
        if not correo:
            return False, "El correo electrónico no puede estar vacío"
        
        # Patrón regex para validar correo electrónico
        patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(patron, correo):
            return False, "El formato del correo electrónico no es válido"
        
        return True, ""

    def validar_telefono(self, telefono):
        """Valida que el teléfono contenga solo números"""
        if not telefono:
            return False, "El teléfono no puede estar vacío"
        
        if not telefono.isdigit():
            return False, "El teléfono solo puede contener números"
        
        if len(telefono) < 8:
            return False, "El teléfono debe tener al menos 8 dígitos"
        
        return True, ""

    def validar_contraseña(self, contraseña):
        """Valida que la contraseña cumpla con las políticas de seguridad"""
        if len(contraseña) < 8:
            return False, "La contraseña debe tener al menos 8 caracteres"
        
        if not re.search(r'[A-Z]', contraseña):
            return False, "La contraseña debe contener al menos una letra mayúscula"
        
        if not re.search(r'[0-9]', contraseña):
            return False, "La contraseña debe contener al menos un número"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', contraseña):
            return False, "La contraseña debe contener al menos un carácter especial (!@#$%^&*)"
        
        return True, ""

    def validar_campos_vacios(self):
        """Valida que todos los campos estén llenos"""
        if not self.setNombre.text().strip():
            return False, "El campo Nombre es obligatorio"
        
        if not self.setApellido.text().strip():
            return False, "El campo Apellido es obligatorio"
        
        if not self.setCorreo.text().strip():
            return False, "El campo Correo Electrónico es obligatorio"
        
        if not self.setTel.text().strip():
            return False, "El campo Teléfono es obligatorio"
        
        if not self.setNombreUsuario.text().strip():
            return False, "El campo Nombre de Usuario es obligatorio"
        
        if not self.setContraseña.text().strip():
            return False, "El campo Contraseña es obligatorio"
        
        return True, ""

    def cerrar_ventana(self):
        self.close()
    
    def registrar(self):
        # Validar campos vacíos
        valido, mensaje = self.validar_campos_vacios()
        if not valido:
            QMessageBox.warning(self, "Campos Incompletos", mensaje)
            return
        
        nombre = self.setNombre.text().strip()
        apellido = self.setApellido.text().strip()
        correo = self.setCorreo.text().strip()
        telefono = self.setTel.text().strip()
        nombreUsuario = self.setNombreUsuario.text().strip()
        contraseña = self.setContraseña.text()
        cargo = self.set_tipo_Usuario.currentText()
        extension = self.extension_combo.currentText().split()[0]
        
        # Validar correo
        valido_correo, mensaje_correo = self.validar_correo(correo)
        if not valido_correo:
            QMessageBox.warning(self, "Error en Correo", mensaje_correo)
            return
        
        # Validar teléfono
        valido_tel, mensaje_tel = self.validar_telefono(telefono)
        if not valido_tel:
            QMessageBox.warning(self, "Error en Teléfono", mensaje_tel)
            return
        
        # Validar contraseña
        valido_pass, mensaje_pass = self.validar_contraseña(contraseña)
        if not valido_pass:
            QMessageBox.warning(self, "Contraseña Débil", mensaje_pass)
            return
        
        # Encriptar contraseña
        contraseñaE = self.encriptarContraseña(contraseña)
        
        # Teléfono completo con extensión
        telefono_completo = f"{extension} {telefono}"
        
        # Agregar usuario
        self.agregar_Usuario(nombre, apellido, correo, telefono_completo, nombreUsuario, contraseñaE, cargo)

    def encriptarContraseña(self, contrasena):
        clave = 3
        contrasena_encriptada = ""
        
        for caracter in contrasena:
            if caracter.isalpha():
                nuevo_caracter = chr(((ord(caracter) - ord('a' if caracter.islower() else 'A') + clave) % 26) + ord('a' if caracter.islower() else 'A'))
                contrasena_encriptada += nuevo_caracter
            else:
                contrasena_encriptada += caracter
        
        return contrasena_encriptada

    def agregar_Usuario(self, nombre, apellido, correo, telefono, nombreUsuario, contrasenia, cargo):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()

            # Verificar si el usuario ya existe
            cursor.execute("SELECT Usuario FROM usuario WHERE Usuario = %s", (nombreUsuario,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Usuario Existente", 
                                   "El nombre de usuario ya está registrado. Por favor elige otro.")
                return

            # Verificar si el correo ya existe
            cursor.execute("SELECT correo FROM usuario WHERE correo = %s", (correo,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Correo Existente", 
                                   "El correo electrónico ya está registrado. Por favor usa otro.")
                return

            consulta = """
            INSERT INTO usuario (nombre, apellido, correo, telefono, usuario, contraseña, cargo, activo) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
            """
            datos = (nombre, apellido, correo, telefono, nombreUsuario, contrasenia, cargo)
            cursor.execute(consulta, datos)

            conexion.commit()
            QMessageBox.information(self, "Registro Exitoso", 
                                   f"Usuario '{nombreUsuario}' registrado correctamente")
            
            # Limpiar campos
            self.setNombre.clear()
            self.setApellido.clear()
            self.setCorreo.clear()
            self.setTel.clear()
            self.setNombreUsuario.clear()
            self.setContraseña.clear()
            self.set_tipo_Usuario.setCurrentIndex(0)

        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error de Base de Datos", 
                               f"Error al agregar usuario: {error}")

        finally:
            if conexion.is_connected():
                cursor.close()


# # Bloque de ejecución para pruebas
# if __name__ == "__main__":
#     from PyQt6.QtWidgets import QApplication
#     import sys
    
#     app = QApplication(sys.argv)
#     ventana = VentanaRegistro()
#     ventana.show()
#     sys.exit(app.exec())
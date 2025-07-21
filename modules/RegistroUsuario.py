from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QComboBox, QLineEdit,QMessageBox
from PyQt6.QtGui import QPixmap
import hashlib
import mysql.connector

from conexion import ConexionBD
class VentanaRegistro(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Registro")
        self.setGeometry(200, 200, 400, 300)  # X, Y, Ancho, Alto
        # Establecer imagen de fondo
        background_label = QLabel(self)
        pixmap = QPixmap("Images/login.jpg")
        background_label.setPixmap(pixmap)
        background_label.resize(pixmap.width(), pixmap.height())

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout_vertical = QVBoxLayout(central_widget)


        # Campos de habitación
        self.etiquetaN=QLabel("Nombre ")
        self.setNombre = QLineEdit(self)
        self.etiquetaA=QLabel("Apellido")
        self.setApellido = QLineEdit(self)
        self.etiquetaT=QLabel("Telefono")
        self.setTel = QLineEdit(self)
        self.etiquetaNU=QLabel("Nombre de Usuario")
        self.setNombreUsuario = QLineEdit(self)
        self.etiquetaC=QLabel("Contraseña")
        self.setContraseña = QLineEdit(self)
        self.set_tipo_Usuario = QComboBox()
        self.set_tipo_Usuario.addItems(["Empleado","Gerente"])
        self.botonRegistrarme = QPushButton("Registrarme")
        

        layout_vertical.addWidget(self.etiquetaN)
        layout_vertical.addWidget(self.setNombre)
        layout_vertical.addWidget(self.etiquetaA)
        layout_vertical.addWidget(self.setApellido)
        layout_vertical.addWidget(self.etiquetaT)
        layout_vertical.addWidget(self.setTel)
        layout_vertical.addWidget(self.etiquetaNU)
        layout_vertical.addWidget(self.setNombreUsuario)
        layout_vertical.addWidget(self.etiquetaC)
        layout_vertical.addWidget(self.setContraseña)
        layout_vertical.addWidget(self.set_tipo_Usuario)
        layout_vertical.addWidget(self.botonRegistrarme)
        
        
        

        # Botón de regresar
        boton_regresar = QPushButton("Regresar")
        layout_vertical.addWidget(boton_regresar)

        boton_regresar.clicked.connect(self.cerrar_ventana)
        self.botonRegistrarme.clicked.connect(self.registrar)

    def cerrar_ventana(self):
        self.close()
    def registrar(self):
        nombre = self.setNombre.text()
        apellido = self.setApellido.text()
        telefono=self.setTel.text()
        nombreUsuario = self.setNombreUsuario.text()
        contraseña = self.setContraseña.text()
        contraseniaE=self.encriptarContraseña(contraseña)
        cargo=self.set_tipo_Usuario.currentText()
        self.agregar_Usuario(nombre, apellido,telefono,nombreUsuario,contraseniaE,cargo)
        self.setNombre.clear()
        self.setApellido.clear()
        self.setNombreUsuario.clear()
        self.setContraseña.clear()
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

    def agregar_Usuario(self,nombre, apellido, telefono,nombreUsuario,contrasenia,cargo):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()

            consulta = """
            INSERT INTO usuario (nombre, apellido, telefono, usuario,contraseña,cargo,activo) 
            VALUES (%s, %s, %s, %s,%s,%s,1)
            """
            datos = (nombre, apellido, telefono,nombreUsuario,contrasenia,cargo)
            cursor.execute(consulta, datos)

            conexion.commit()
            QMessageBox.information(self, "correct", "Usuario agregado correctamente")

        except mysql.connector.Error as error:
            print(f"Error al agregar Usuario: {error}")

        finally:
            if conexion.is_connected():
                cursor.close()
                print("Cursor cerrado.")
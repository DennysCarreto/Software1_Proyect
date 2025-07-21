from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget,QGridLayout,QLineEdit,QTableWidget,QMessageBox,QTableWidgetItem
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import mysql.connector
from conexion import ConexionBD

class ProveedoresWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Módulo de Proveedores")
        self.setGeometry(600, 300, 700, 400)  # X, Y, Ancho, Alto
        # Establecer imagen de fondo
        background_label = QLabel(self)
        pixmap = QPixmap("Images/login.jpg")
        background_label.setPixmap(pixmap)
        background_label.resize(pixmap.width(), pixmap.height())


        # Creamos un widget central para la ventana principal
        widget_central = QWidget()
        #self.setCentralWidget(widget_central)

        # Creamos un layout grid para organizar los botones
        layout_grid = QGridLayout(widget_central)


        self.boton_agregar_cliente = QPushButton("Agregar")
        layout_grid.addWidget(self.boton_agregar_cliente, 0, 5,1,1)
        self.boton_agregar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.boton_agregar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        # Conecta la señal de cuando el mouse entra y sale del botón a los métodos correspondientes
        self.boton_agregar_cliente.enterEvent = self.on_enter_buttonA
        self.boton_agregar_cliente.leaveEvent = self.on_leave_buttonA

        self.boton_mostrar_cliente = QPushButton("Mostar")
        layout_grid.addWidget(self.boton_mostrar_cliente, 1, 5,1,1)
        self.boton_mostrar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.boton_mostrar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        # Conecta la señal de cuando el mouse entra y sale del botón a los métodos correspondientes
        self.boton_mostrar_cliente.enterEvent = self.on_enter_buttonM
        self.boton_mostrar_cliente.leaveEvent = self.on_leave_buttonM

        self.boton_actualizar_cliente = QPushButton("Actualizar")
        layout_grid.addWidget(self.boton_actualizar_cliente, 2, 5,1,1)
        self.boton_actualizar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.boton_actualizar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        # Conecta la señal de cuando el mouse entra y sale del botón a los métodos correspondientes
        self.boton_actualizar_cliente.enterEvent = self.on_enter_buttonAc
        self.boton_actualizar_cliente.leaveEvent = self.on_leave_buttonAc

        self.boton_eliminar_cliente = QPushButton("Eliminar")
        layout_grid.addWidget(self.boton_eliminar_cliente, 3, 5,1,1)
        self.boton_eliminar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.boton_eliminar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        # Conecta la señal de cuando el mouse entra y sale del botón a los métodos correspondientes
        self.boton_eliminar_cliente.enterEvent = self.on_enter_buttonD
        self.boton_eliminar_cliente.leaveEvent = self.on_leave_buttonD

        self.boton_buscar_cliente = QPushButton("Buscar")
        layout_grid.addWidget(self.boton_buscar_cliente, 3, 3,1,1)
        self.boton_buscar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.boton_buscar_cliente.setCursor(Qt.CursorShape.PointingHandCursor)
        # Conecta la señal de cuando el mouse entra y sale del botón a los métodos correspondientes
        self.boton_buscar_cliente.enterEvent = self.on_enter_buttonBus
        self.boton_buscar_cliente.leaveEvent = self.on_leave_buttonBus

        self.etiquetaN=QLabel("Nombre: ")
        layout_grid.addWidget(self.etiquetaN, 0, 0,1,1)
        self.setNombre_cliente = QLineEdit(self)
        layout_grid.addWidget(self.setNombre_cliente, 0, 1,1,1)
        

        self.etiquetaA=QLabel("Apellido: ")
        layout_grid.addWidget(self.etiquetaA, 1, 0,1,1)
        self.setApellido_cliente = QLineEdit(self)
        layout_grid.addWidget(self.setApellido_cliente, 1, 1,1,1)
        
       
        self.etiquetaT=QLabel("Telefono: ")
        layout_grid.addWidget(self.etiquetaT, 3, 0,1,1)
        self.setTel_cliente = QLineEdit(self)
        layout_grid.addWidget(self.setTel_cliente, 3, 1,1,1)
       

        self.etiquetaEC=QLabel("ID cliente")
        layout_grid.addWidget(self.etiquetaEC, 2, 3,1,1)
        self.search_cliente = QLineEdit(self)
        layout_grid.addWidget(self.search_cliente, 2, 4,1,1)
     


        self.tableWidget = QTableWidget()
        layout_grid.addWidget(self.tableWidget, 4, 0,1,6)


        # Botón de regresar
        self.boton_regresar = QPushButton("Regresar")
        layout_grid.addWidget(self.boton_regresar, 6, 5,1,1)
        self.boton_regresar.setStyleSheet("background-color: #ffffff; color: #000000;")
        self.boton_regresar.setCursor(Qt.CursorShape.PointingHandCursor)
        # Conecta la señal de cuando el mouse entra y sale del botón a los métodos correspondientes
        self.boton_regresar.enterEvent = self.on_enter_buttonRe
        self.boton_regresar.leaveEvent = self.on_leave_buttonRe

          # Establecer el layout para la ventana principal
        widget_central.setLayout(layout_grid)
        self.setCentralWidget(widget_central)

        # Conectamos la señal clicked del botón de regresar al método de cerrar la ventana
        self.boton_agregar_cliente.clicked.connect(self.agregar_cliente_datos)
        self.boton_mostrar_cliente.clicked.connect(self.mostrar_clientes)
        self.boton_buscar_cliente.clicked.connect(self.buscar_cliente)
        self.boton_actualizar_cliente.clicked.connect(self.actualizar_cliente_datos)
        self.boton_eliminar_cliente.clicked.connect(self.eliminar_cliente_datos)
        self.boton_regresar.clicked.connect(self.cerrar_ventana)
    # Define un nuevo método para obtener los valores de los campos de texto y llamar a agregar_cliente
    def agregar_cliente_datos(self):
        nombre = self.setNombre_cliente.text()
        apellido = self.setApellido_cliente.text()
        telefono = self.setTel_cliente.text()
        self.agregar_cliente(nombre, apellido, telefono)
        self.setNombre_cliente.clear()
        self.setApellido_cliente.clear()
        self.setTel_cliente.clear()

    def actualizar_cliente_datos(self):
        id=self.search_cliente.text()
        nombre = self.setNombre_cliente.text()
        apellido = self.setApellido_cliente.text()
        telefono = self.setTel_cliente.text()
        self.actualizar_cliente(id,nombre, apellido, telefono)
        self.setNombre_cliente.clear()
        self.setApellido_cliente.clear()
        self.setTel_cliente.clear()
        self.search_cliente.clear()

    def eliminar_cliente_datos(self):
        id=self.search_cliente.text()
        nombre = self.setNombre_cliente.text()
        apellido = self.setApellido_cliente.text()
        telefono = self.setTel_cliente.text()
        self.eliminar_cliente(id,nombre, apellido, telefono)
        self.setNombre_cliente.clear()
        self.setApellido_cliente.clear()
        self.setTel_cliente.clear()
        self.search_cliente.clear()

    
        
    def agregar_cliente(self,nombre, apellido, telefono):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()

            consulta = """
            INSERT INTO Proveedor (nombre, apellido, telefono,activo) 
            VALUES (%s, %s, %s,1)
            """
            datos = (nombre, apellido,telefono)
            cursor.execute(consulta, datos)

            conexion.commit()
            QMessageBox.information(self, "correct", "Proveedor agregado correctamente")

        except mysql.connector.Error as error:
            print(f"Error al agregar Proveedor: {error}")

        finally:
            if conexion.is_connected():
                cursor.close()
                print("Cursor cerrado.")

   
    def mostrar_clientes(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()

             #Verificar la conexión antes de ejecutar la consulta
            if not conexion.is_connected():
                print("¡Error! La conexión no está activa.")
                return
            
            column_names = ['id','Nombre','Apellido','Telefono']
            cursor.execute("SELECT id,nombre,apellido,telefono FROM Proveedor where activo=1")
            clientes = cursor.fetchall()
            

                # Limpiar la tabla antes de mostrar nuevos datos    
            self.tableWidget.setRowCount(0)
            self.tableWidget.setColumnCount(len(clientes[0]))

             # Establecer los nombres de las columnas
            self.tableWidget.setHorizontalHeaderLabels(column_names)
            

             # Insertar filas y llenar celdas con datos
            for fila_num, fila_datos in enumerate(clientes):
                self.tableWidget.insertRow(fila_num)
                for columna_num, dato in enumerate(fila_datos):
                    celda = QTableWidgetItem(str(dato))
                    self.tableWidget.setItem(fila_num, columna_num, celda)

        except mysql.connector.Error as error:
            print(f"Error al mostrar Proveedores: {error}")

        finally:
        # Cerrar cursor y conexión al finalizar
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
                print("Cursor cerrado.")
    def buscar_cliente(self):
        id = self.search_cliente.text()
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            # Verificar la conexión antes de ejecutar la consulta
            if not conexion.is_connected():
                print("¡Error! La conexión no está activa.")
                return
            cursor.execute("SELECT nombre, apellido, telefono FROM Proveedor WHERE id = %s", (id,))
            result = cursor.fetchone()
            if result:
                nombre, apellido, telefono = result
                tel = str(telefono)
                self.setNombre_cliente.setText(nombre)
                self.setApellido_cliente.setText(apellido)
                self.setTel_cliente.setText(tel)
            else:
                print(f"No se encontró ningún Proveeedor con el ID {id}.")
        except mysql.connector.Error as error:
            print(f"Error al mostrar Proveedor: {error}")
        finally:
        # Cerrar cursor y conexión al finalizar
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            print("Cursor cerrado.")

    def actualizar_cliente(self, id_cliente, nombre, apellido, telefono):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()

            consulta = """
            UPDATE Proveedor
            SET nombre = %s, apellido = %s, telefono = %s
            WHERE id = %s
            """
            datos = (nombre, apellido, telefono, id_cliente)
            cursor.execute(consulta, datos)

            conexion.commit()
            QMessageBox.information(self, "Correcto", "Proveedor actualizado correctamente")

        except mysql.connector.Error as error:
            print(f"Error al actualizar Proveedor: {error}")

        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
            print("Cursor cerrado.")
    def eliminar_cliente(self, id_cliente, nombre, apellido, telefono):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()

            consulta = """
            UPDATE Proveedor
            SET nombre = %s, apellido = %s, telefono = %s,activo=0
            WHERE id = %s
            """
            datos = (nombre, apellido, telefono, id_cliente)
            cursor.execute(consulta, datos)

            conexion.commit()
            QMessageBox.information(self, "Correcto", "Proveedor eliminado correctamente")

        except mysql.connector.Error as error:
            print(f"Error al actualizar Proveedor: {error}")

        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
            print("Cursor cerrado.")




    def cerrar_ventana(self):
        self.close()
    def on_enter_buttonA(self, event):
        # Cambia el color de fondo del botón cuando el mouse entra
        self.boton_agregar_cliente.setStyleSheet("background-color: #94e7ff; color: #000000;")
    def on_leave_buttonA(self, event):
        # Restaura el color de fondo original del botón cuando el mouse sale
        self.boton_agregar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
    def on_enter_buttonAc(self, event):
        # Cambia el color de fondo del botón cuando el mouse entra
        self.boton_actualizar_cliente.setStyleSheet("background-color: #94e7ff; color: #000000;")
    def on_leave_buttonAc(self, event):
        # Restaura el color de fondo original del botón cuando el mouse sale
        self.boton_actualizar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")

    def on_enter_buttonM(self, event):
        # Cambia el color de fondo del botón cuando el mouse entra
        self.boton_mostrar_cliente.setStyleSheet("background-color: #94e7ff; color: #000000;")
    def on_leave_buttonM(self, event):
        # Restaura el color de fondo original del botón cuando el mouse sale
        self.boton_mostrar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
    def on_enter_buttonD(self, event):
        # Cambia el color de fondo del botón cuando el mouse entra
        self.boton_eliminar_cliente.setStyleSheet("background-color: #94e7ff; color: #000000;")
    def on_leave_buttonD(self, event):
        # Restaura el color de fondo original del botón cuando el mouse sale
        self.boton_eliminar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")
    def on_enter_buttonBus(self, event):
        # Cambia el color de fondo del botón cuando el mouse entra
        self.boton_buscar_cliente.setStyleSheet("background-color: #94e7ff; color: #000000;")
    def on_leave_buttonBus(self, event):
        # Restaura el color de fondo original del botón cuando el mouse sale
        self.boton_buscar_cliente.setStyleSheet("background-color: #ffffff; color: #000000;")

    def on_enter_buttonRe(self, event):
        # Cambia el color de fondo del botón cuando el mouse entra
        self.boton_regresar.setStyleSheet("background-color: #94e7ff; color: #000000;")
    def on_leave_buttonRe(self, event):
        # Restaura el color de fondo original del botón cuando el mouse sale
        self.boton_regresar.setStyleSheet("background-color: #ffffff; color: #000000;")
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget,QGridLayout,QLineEdit,QTableWidget,QMessageBox,QTableWidgetItem, QHeaderView, QFrame, QFormLayout
from PyQt6.QtGui import QPixmap, QPalette, QColor
from PyQt6.QtCore import Qt
import mysql.connector

from conexion import ConexionBD

class ClientesWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Clientes")
        self.setMinimumSize(1024, 768)

        # ### <<< INICIO: SISTEMA DE DISEÑO PROFESIONAL >>> ###

        self.colores = {
            "fondo": "#F8F9FA", "cabecera": "#0B6E4F",
            "texto_principal": "#212529", "acento": "#3A9D5A",
            "borde": "#DEE2E6", "peligro": "#E53E3E"
        }
        
        self._create_stylesheets()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colores["fondo"]))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(15)

        self._setup_header_bar()
        self._setup_form_panel()
        self._setup_search_bar() # <-- NUEVO PANEL DE BÚSQUEDA
        self._setup_table()

        # ### <<< FIN: SISTEMA DE DISEÑO PROFESIONAL >>> ###

        self.mostrar_clientes() # Cargar datos iniciales

    def _create_stylesheets(self):
        """Método central para definir todos los estilos de la ventana."""
        # (Este método es idéntico al del módulo de Proveedores, puedes copiarlo de allí)
        # Por claridad, lo incluyo aquí de nuevo.
        self.style_header_label = f"font-size: 22px; font-weight: bold; color: white; background: transparent;"
        self.style_header_button = f"""
            QPushButton {{ background-color: #FFFFFF; color: {self.colores['texto_principal']};
                border: none; border-radius: 5px; padding: 8px 12px; font-weight: bold;
            }} QPushButton:hover {{ background-color: #E2E8F0; }}
        """
        self.style_input_field = f"""
            QLineEdit {{ border: 1px solid {self.colores['borde']}; border-radius: 5px;
                padding: 8px; font-size: 14px; background-color: white; color: {self.colores['texto_principal']};
            }}
        """
        self.style_primary_button = f"""
            QPushButton {{ background-color: {self.colores['acento']}; color: white;
                border: none; border-radius: 5px; padding: 10px; font-weight: bold;
            }} QPushButton:hover {{ background-color: {self.colores['cabecera']}; }}
        """
        self.style_danger_button = f"""
            QPushButton {{ background-color: {self.colores['peligro']}; color: white;
                border: none; border-radius: 5px; padding: 10px; font-weight: bold;
            }} QPushButton:hover {{ background-color: #C53030; }}
        """
        self.style_table = f"""
            QTableWidget {{ border: 1px solid {self.colores['borde']}; gridline-color: {self.colores['borde']}; font-size: 13px; }}
            QHeaderView::section {{ background-color: {self.colores['cabecera']}; color: white; padding: 8px;
                border: 1px solid {self.colores['cabecera']}; font-weight: bold;
            }}
            QTableWidget::item:selected {{ background-color: {self.colores['acento']}; color: white; }}
        """

    def _setup_header_bar(self):
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {self.colores['cabecera']};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)

        back_button = QPushButton("Regresar")
        back_button.setStyleSheet(self.style_header_button)
        back_button.clicked.connect(self.back_to_main)
        
        title_label = QLabel("Gestión de Clientes")
        title_label.setStyleSheet(self.style_header_label)

        header_layout.addWidget(back_button)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.main_layout.addWidget(header_frame)

    def _setup_form_panel(self):
        form_frame = QFrame()
        form_frame.setStyleSheet(f"margin: 0 10px;")
        form_layout = QVBoxLayout(form_frame)
        
        data_entry_layout = QFormLayout()
        data_entry_layout.setSpacing(10)
        
        self.nombre_input = QLineEdit()
        self.apellido_input = QLineEdit()
        self.telefono_input = QLineEdit()
        self.nit_input = QLineEdit()
        self.direccion_input = QLineEdit()
        
        for field in [self.nombre_input, self.apellido_input, self.telefono_input, self.nit_input, self.direccion_input]:
            field.setStyleSheet(self.style_input_field)

        data_entry_layout.addRow(QLabel("Nombre:"), self.nombre_input)
        data_entry_layout.addRow(QLabel("Apellido:"), self.apellido_input)
        data_entry_layout.addRow(QLabel("Teléfono:"), self.telefono_input)
        data_entry_layout.addRow(QLabel("NIT:"), self.nit_input)
        data_entry_layout.addRow(QLabel("Dirección:"), self.direccion_input)
        
        form_layout.addLayout(data_entry_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        self.agregar_btn = QPushButton("➕ Agregar Cliente")
        self.actualizar_btn = QPushButton("✏️ Actualizar Seleccionado")
        self.eliminar_btn = QPushButton("❌ Desactivar Seleccionado")
        self.limpiar_btn = QPushButton("✨ Limpiar Campos")
        
        self.agregar_btn.setStyleSheet(self.style_primary_button)
        self.actualizar_btn.setStyleSheet(self.style_header_button)
        self.eliminar_btn.setStyleSheet(self.style_danger_button)
        self.limpiar_btn.setStyleSheet(self.style_header_button)

        action_layout.addWidget(self.agregar_btn)
        action_layout.addWidget(self.actualizar_btn)
        action_layout.addWidget(self.eliminar_btn)
        action_layout.addStretch()
        action_layout.addWidget(self.limpiar_btn)
        form_layout.addLayout(action_layout)

        self.main_layout.addWidget(form_frame)
        
        self.agregar_btn.clicked.connect(self.agregar_cliente)
        self.actualizar_btn.clicked.connect(self.actualizar_cliente)
        self.eliminar_btn.clicked.connect(self.desactivar_cliente)
        self.limpiar_btn.clicked.connect(self.limpiar_campos)

    def _setup_search_bar(self):
        """Crea la barra de búsqueda dinámica."""
        search_frame = QFrame()
        search_frame.setStyleSheet("margin: 0 10px;")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 5, 0, 5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nombre, apellido o NIT...")
        self.search_input.setStyleSheet(self.style_input_field)
        
        self.search_input.textChanged.connect(self.filtrar_tabla)

        # ### <<< CORRECCIÓN AQUÍ >>> ###
        # Añadimos el campo de texto (self.search_input) al layout, no el frame.
        search_layout.addWidget(self.search_input)
        
        # Y finalmente, añadimos el frame (que ya contiene todo) al layout principal.
        self.main_layout.addWidget(search_frame)

    def _setup_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "Teléfono", "NIT"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet(self.style_table)
        self.table.clicked.connect(self.cargar_cliente_en_formulario)
        self.main_layout.addWidget(self.table)
    
    def filtrar_tabla(self):
        """Filtra las filas de la tabla basado en el texto de búsqueda."""
        texto_busqueda = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            nombre = self.table.item(i, 1).text().lower()
            apellido = self.table.item(i, 2).text().lower()
            nit = self.table.item(i, 4).text().lower()
            
            # Si el texto de búsqueda está en cualquiera de los campos, la fila es visible
            if texto_busqueda in nombre or texto_busqueda in apellido or texto_busqueda in nit:
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)
    
    def limpiar_campos(self):
        self.nombre_input.clear()
        self.apellido_input.clear()
        self.telefono_input.clear()
        self.nit_input.clear()
        self.direccion_input.clear()
        self.table.clearSelection()

    def cargar_cliente_en_formulario(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            return
            
        cliente_id = self.table.item(selected_row, 0).text()
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM cliente WHERE id = %s", (cliente_id,))
            cliente = cursor.fetchone()
            if cliente:
                self.nombre_input.setText(cliente.get('nombre', ''))
                self.apellido_input.setText(cliente.get('apellido', ''))
                self.telefono_input.setText(cliente.get('telefono', ''))
                self.nit_input.setText(cliente.get('nit', ''))
                self.direccion_input.setText(cliente.get('direccion', ''))
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"No se pudo cargar la información completa del cliente: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def agregar_cliente(self):
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        telefono = self.telefono_input.text().strip()
        nit = self.nit_input.text().strip()
        direccion = self.direccion_input.text().strip()

        if not nombre or not apellido:
            QMessageBox.warning(self, "Campos Vacíos", "Nombre y Apellido son obligatorios.")
            return

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            query = "INSERT INTO cliente (nombre, apellido, telefono, nit, direccion, activo) VALUES (%s, %s, %s, %s, %s, 1)"
            cursor.execute(query, (nombre, apellido, telefono, nit, direccion))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Cliente agregado correctamente.")
            self.limpiar_campos()
            self.mostrar_clientes()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al agregar cliente: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def mostrar_clientes(self):
        self.table.setRowCount(0)
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, apellido, telefono, nit FROM cliente WHERE activo = 1")
            clientes = cursor.fetchall()
            
            self.table.setRowCount(len(clientes))
            for i, cliente in enumerate(clientes):
                self.table.setItem(i, 0, QTableWidgetItem(str(cliente['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(cliente['nombre']))
                self.table.setItem(i, 2, QTableWidgetItem(cliente['apellido']))
                self.table.setItem(i, 3, QTableWidgetItem(cliente['telefono']))
                self.table.setItem(i, 4, QTableWidgetItem(cliente['nit']))
            
            self.table.setColumnHidden(0, True)
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al mostrar clientes: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def actualizar_cliente(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Por favor, seleccione un cliente de la tabla para actualizar.")
            return
        
        cliente_id = self.table.item(selected_row, 0).text()
        nombre = self.nombre_input.text().strip()
        apellido = self.apellido_input.text().strip()
        telefono = self.telefono_input.text().strip()
        nit = self.nit_input.text().strip()
        direccion = self.direccion_input.text().strip()
        
        if not nombre or not apellido:
            QMessageBox.warning(self, "Campos Vacíos", "Nombre y Apellido son obligatorios.")
            return

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            query = "UPDATE cliente SET nombre=%s, apellido=%s, telefono=%s, nit=%s, direccion=%s WHERE id=%s"
            cursor.execute(query, (nombre, apellido, telefono, nit, direccion, cliente_id))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente.")
            self.limpiar_campos()
            self.mostrar_clientes()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al actualizar cliente: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def desactivar_cliente(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Por favor, seleccione un cliente de la tabla para desactivar.")
            return

        cliente_id = self.table.item(selected_row, 0).text()
        nombre_cliente = self.table.item(selected_row, 1).text()
        
        confirm = QMessageBox.question(self, "Confirmar Desactivación", 
                                       f"¿Está seguro de que desea desactivar a '{nombre_cliente}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                query = "UPDATE cliente SET activo = 0 WHERE id = %s"
                cursor.execute(query, (cliente_id,))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Cliente desactivado correctamente.")
                self.limpiar_campos()
                self.mostrar_clientes()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de Base de Datos", f"Error al desactivar cliente: {err}")
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    cursor.close()
                    conexion.close()

    def back_to_main(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()
import sys
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, 
                             QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem,
                             QHBoxLayout, QFrame, QFormLayout, QHeaderView)
from PyQt6.QtGui import QPalette, QColor, QFont, QRegularExpressionValidator 
from PyQt6.QtCore import Qt, QRegularExpression 

import mysql.connector
from conexion import ConexionBD

class ProveedoresWindow(QMainWindow):
    def __init__(self, parent=None, cargo=None):
        super().__init__(parent)
        self.parent_window = parent
        self.cargo = cargo
        self.setWindowTitle("Módulo de Proveedores")
        self.setMinimumSize(1024, 768)

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
        
        # ### <<< PASO 1: AÑADIMOS LA NUEVA BARRA DE BÚSQUEDA >>> ###
        self._setup_search_bar()
        
        self._setup_table()

        self.mostrar_proveedores() # Cargar datos al iniciar

    def _create_stylesheets(self):
        """Método central para definir todos los estilos de la ventana."""
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
        title_label = QLabel("Gestión de Proveedores")
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
        self.marca_input = QLineEdit() # Ya renombrado a marca
        self.telefono_input = QLineEdit()
        name_regex = QRegularExpression(r"^[^\d]+$") 
        name_validator = QRegularExpressionValidator(name_regex, self)
        self.nombre_input.setValidator(name_validator)

        phone_regex = QRegularExpression(r"^\d{8}$") # Inicio, 8 dígitos, Fin
        phone_validator = QRegularExpressionValidator(phone_regex, self)
        self.telefono_input.setValidator(phone_validator)
        for field in [self.nombre_input, self.marca_input, self.telefono_input]:
            field.setStyleSheet(self.style_input_field)

        data_entry_layout.addRow(QLabel("Nombre Proveedor:"), self.nombre_input)
        data_entry_layout.addRow(QLabel("Marca Principal:"), self.marca_input) 
        data_entry_layout.addRow(QLabel("Teléfono (8 dígitos):"), self.telefono_input) # Añadir indicación
        
        form_layout.addLayout(data_entry_layout)

        # Botones de acción
        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        self.agregar_btn = QPushButton("➕ Agregar Proveedor")
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
        self.agregar_btn.clicked.connect(self.agregar_proveedor)
        self.actualizar_btn.clicked.connect(self.actualizar_proveedor)
        self.eliminar_btn.clicked.connect(self.desactivar_proveedor)
        self.limpiar_btn.clicked.connect(self.limpiar_campos)
        
        if self.cargo == 'Empleado':
            print("DEBUG: Aplicando restricciones para Empleado en Proveedores.")
            # Ocultar botones no permitidos
            self.agregar_btn.hide()
            self.actualizar_btn.hide()
            self.eliminar_btn.hide()


    def _setup_search_bar(self):
        search_frame = QFrame()
        search_frame.setStyleSheet("margin: 0 10px;")
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 5, 0, 5)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nombre o marca...") # Actualizar placeholder
        self.search_input.setStyleSheet(self.style_input_field)
        self.search_input.textChanged.connect(self.filtrar_tabla)

        search_layout.addWidget(self.search_input)
        self.main_layout.addWidget(search_frame)

    def _setup_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre", "Marca", "Teléfono"]) 
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows) 
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch) 
        self.table.setStyleSheet(self.style_table) 
        self.table.setAlternatingRowColors(True) 
        self.table.clicked.connect(self.cargar_proveedor_en_formulario)
        self.main_layout.addWidget(self.table)
    
    def filtrar_tabla(self):
        texto_busqueda = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            nombre = self.table.item(i, 1).text().lower()
            marca = self.table.item(i, 2).text().lower() # <-- CAMBIO: Filtrar por marca
            
            if texto_busqueda in nombre or texto_busqueda in marca: # <-- CAMBIO
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)
    
    def limpiar_campos(self):
        self.nombre_input.clear()
        self.marca_input.clear() 
        self.telefono_input.clear()
        self.table.clearSelection() 

    def cargar_proveedor_en_formulario(self):
        selected_row = self.table.currentRow()
        if selected_row < 0: return
            
        nombre = self.table.item(selected_row, 1).text()
        marca = self.table.item(selected_row, 2).text() 
        telefono = self.table.item(selected_row, 3).text()
        
        self.nombre_input.setText(nombre)
        self.marca_input.setText(marca) 
        self.telefono_input.setText(telefono)

    def agregar_proveedor(self):
        nombre = self.nombre_input.text().strip()
        marca = self.marca_input.text().strip() 
        telefono = self.telefono_input.text().strip()

        if not nombre or not marca:
            QMessageBox.warning(self, "Campos Vacíos", "Nombre y Marca son obligatorios.")
            return
        if not self.nombre_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El Nombre del proveedor no puede contener números.")
             return
        if not self.telefono_input.hasAcceptableInput() or len(telefono) != 8:
             QMessageBox.warning(self, "Formato Incorrecto", "El Teléfono debe contener exactamente 8 dígitos numéricos.")
             return

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            query = "INSERT INTO Proveedor (nombre, marca, telefono, activo) VALUES (%s, %s, %s, 1)"
            cursor.execute(query, (nombre, marca, telefono))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Proveedor agregado.")
            self.limpiar_campos()
            self.mostrar_proveedores()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al agregar: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def mostrar_proveedores(self):
        self.table.setRowCount(0)
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, marca, telefono FROM Proveedor WHERE activo = 1")
            proveedores = cursor.fetchall()
            
            self.table.setRowCount(len(proveedores))
            for i, proveedor in enumerate(proveedores):
                self.table.setItem(i, 0, QTableWidgetItem(str(proveedor['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(proveedor['nombre']))
                self.table.setItem(i, 2, QTableWidgetItem(proveedor['marca']))
                self.table.setItem(i, 3, QTableWidgetItem(proveedor['telefono']))
            
            self.table.setColumnHidden(0, True) # Ocultar columna de ID
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al mostrar proveedores: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def actualizar_proveedor(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Seleccione un proveedor.")
            return
        
        proveedor_id = self.table.item(selected_row, 0).text()
        nombre = self.nombre_input.text().strip()
        marca = self.marca_input.text().strip() 
        telefono = self.telefono_input.text().strip()
        if not nombre or not marca:
            QMessageBox.warning(self, "Campos Vacíos", "Nombre y Marca son obligatorios.")
            return
        if not self.nombre_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El Nombre no puede contener números.")
             return
        if not self.telefono_input.hasAcceptableInput() or len(telefono) != 8:
             QMessageBox.warning(self, "Formato Incorrecto", "El Teléfono debe ser de 8 dígitos.")
             return

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            query = "UPDATE Proveedor SET nombre = %s, marca = %s, telefono = %s WHERE id = %s"
            cursor.execute(query, (nombre, marca, telefono, proveedor_id)) 
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Proveedor actualizado.")
            self.limpiar_campos()
            self.mostrar_proveedores()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al actualizar: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def desactivar_proveedor(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Por favor, seleccione un proveedor de la tabla para desactivar.")
            return

        proveedor_id = self.table.item(selected_row, 0).text()
        nombre_proveedor = self.table.item(selected_row, 1).text()
        
        confirm = QMessageBox.question(self, "Confirmar Desactivación", 
                                       f"¿Está seguro de que desea desactivar a '{nombre_proveedor}'?",
                                       QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                # Usamos UPDATE para un borrado lógico (soft delete)
                query = "UPDATE Proveedor SET activo = 0 WHERE id = %s"
                cursor.execute(query, (proveedor_id,))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Proveedor desactivado correctamente.")
                self.limpiar_campos()
                self.mostrar_proveedores()
            except mysql.connector.Error as err:
                QMessageBox.critical(self, "Error de Base de Datos", f"Error al desactivar proveedor: {err}")
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    cursor.close()
                    conexion.close()

    def back_to_main(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()
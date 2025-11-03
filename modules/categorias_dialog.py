# modules/categorias_dialog.py
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QLineEdit, QTableWidget, QMessageBox, QTableWidgetItem,
                             QHeaderView, QFrame, QFormLayout, QApplication, QTextEdit, QWidget)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt, pyqtSignal

# Usar la conexión centralizada
from conexion import ConexionBD
import mysql.connector

class CategoriasDialog(QDialog):
    categories_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestionar Categorías de Productos")
        self.setMinimumSize(800, 600)

        # ### <<< INICIO: CORRECCIÓN DE DISEÑO Y TEMA >>> ###
        
        # 1. Definir una paleta OSCURA local y completa. No heredar del padre.
        self.colores = {
            "fondo": "#1A202C",           # Fondo principal oscuro
            "fondo_secundario": "#2D3748", # Fondo para inputs y tabla
            "texto_principal": "#E2E8F0", # Texto claro
            "texto_secundario": "#A0AEC0",
            "cabecera": "#0B6E4F",        # Verde cabecera tabla
            "acento": "#3A9D5A",          # Verde botones
            "borde": "#4A5568",           # Gris oscuro para bordes
            "peligro": "#E53E3E",         # Rojo
            "blanco": "#FFFFFF",
            "negro": "#000000"
        }
        
        # 2. Aplicar el fondo oscuro al DIÁLOGO y el color de texto por defecto
        self.setStyleSheet(f"""
            QDialog {{ 
                background-color: {self.colores['fondo']}; 
            }}
            QLabel {{
                font-size: 14px; 
                color: {self.colores['texto_principal']}; 
                background-color: transparent;
            }}
        """)
        
        self._create_stylesheets() # Generar todos los estilos detallados

        # 3. Eliminar el setPalette, ya no es necesario
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(15, 15, 15, 15)
        self.main_layout.setSpacing(15)

        self._setup_form_panel()
        self._setup_search_bar()
        self._setup_table()

        self.cargar_categorias() # Cargar datos al iniciar
        # ### <<< FIN: CORRECCIÓN DE DISEÑO Y TEMA >>> ###

    def _create_stylesheets(self):
        """Define los estilos de la ventana."""
        default_font_family = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"

        # ### CAMBIO: Usar fondo_secundario y texto_principal ###
        self.style_input_field = f"""
            QLineEdit, QTextEdit {{ 
                border: 1px solid {self.colores['borde']}; 
                border-radius: 5px;
                padding: 8px; 
                font-size: 14px; 
                background-color: {self.colores['fondo_secundario']}; /* Fondo oscuro-gris */
                color: {self.colores['texto_principal']}; /* Texto CLARO */
                font-family: {default_font_family};
            }}
            QTextEdit {{ min-height: 60px; }} 
        """
        self.style_label = f"font-size: 14px; color: {self.colores['texto_principal']}; font-family: {default_font_family}; background-color: transparent;"
        
        self.style_primary_button = f"""
            QPushButton {{ background-color: {self.colores['acento']}; color: white; border: none; 
                           border-radius: 5px; padding: 10px; font-weight: bold; 
                           font-family: {default_font_family}; }} 
            QPushButton:hover {{ background-color: {self.colores['cabecera']}; }}"""
        
        self.style_danger_button = f"""
            QPushButton {{ background-color: {self.colores['peligro']}; color: white; border: none; 
                           border-radius: 5px; padding: 10px; font-weight: bold; 
                           font-family: {default_font_family}; }} 
            QPushButton:hover {{ background-color: #C53030; }}"""
        
        self.style_header_button = f"""
            QPushButton {{ background-color: {self.colores['fondo_secundario']}; color: {self.colores['texto_principal']}; border: none; 
                           border-radius: 5px; padding: 8px 12px; font-weight: bold; 
                           font-family: {default_font_family}; }} 
            QPushButton:hover {{ background-color: {self.colores['borde']}; }}"""
            
        # ### CAMBIO: Usar fondo_secundario y texto_principal ###
        self.style_table = f"""
            QTableWidget {{ 
                border: 1px solid {self.colores['borde']}; 
                gridline-color: {self.colores['borde']}; 
                font-size: 13px; 
                font-family: {default_font_family}; 
                background-color: {self.colores['fondo_secundario']}; /* Fondo oscuro-gris */
            }}
            QHeaderView::section {{ 
                background-color: {self.colores['cabecera']}; 
                color: white; 
                padding: 8px;
                border: 1px solid {self.colores['cabecera']}; 
                font-weight: bold; 
                font-family: {default_font_family}; 
            }}
            QTableWidget::item {{
                color: {self.colores['texto_principal']}; /* Texto CLARO */
                padding: 5px;
            }}
            QTableWidget::item:selected {{ 
                background-color: {self.colores['acento']}; 
                color: white; 
            }}"""


    def _setup_form_panel(self):
        form_frame = QFrame()
        form_frame.setStyleSheet("background-color: transparent; border: none;") # Transparente
        form_layout = QVBoxLayout(form_frame)
        form_layout.setContentsMargins(0, 0, 0, 0)
        form_layout.setSpacing(10)
        
        data_entry_layout = QFormLayout()
        data_entry_layout.setSpacing(10)
        
        self.nombre_input = QLineEdit()
        self.descripcion_input = QTextEdit()
        
        self.nombre_input.setStyleSheet(self.style_input_field)
        self.descripcion_input.setStyleSheet(self.style_input_field)

        # Las etiquetas usarán el estilo global del QDialog
        data_entry_layout.addRow(QLabel("Nombre Categoría:"), self.nombre_input)
        data_entry_layout.addRow(QLabel("Descripción:"), self.descripcion_input)
        
        form_layout.addLayout(data_entry_layout)

        action_layout = QHBoxLayout()
        action_layout.setSpacing(10)
        self.agregar_btn = QPushButton("➕ Agregar")
        self.actualizar_btn = QPushButton("✏️ Actualizar")
        self.eliminar_btn = QPushButton("❌ Desactivar")
        self.limpiar_btn = QPushButton("✨ Limpiar")
        
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
        
        self.agregar_btn.clicked.connect(self.agregar_categoria)
        self.actualizar_btn.clicked.connect(self.actualizar_categoria)
        self.eliminar_btn.clicked.connect(self.desactivar_categoria)
        self.limpiar_btn.clicked.connect(self.limpiar_campos)

    def _setup_search_bar(self):
        search_frame = QFrame()
        search_frame.setStyleSheet("background-color: transparent; border: none;") # Transparente
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(0, 0, 0, 0)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Buscar por nombre...")
        self.search_input.setStyleSheet(self.style_input_field)
        self.search_input.textChanged.connect(self.filtrar_tabla)
        
        search_layout.addWidget(self.search_input)
        self.main_layout.addWidget(search_frame)

    def _setup_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "Nombre Categoría", "Descripción"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        header = self.table.horizontalHeader()
        
        # Ajuste de tamaño de columnas
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive) # Nombre
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) # Descripción (ocupa el resto)
        self.table.setColumnWidth(1, 200) # Ancho inicial para Nombre

        self.table.setStyleSheet(self.style_table)
        self.table.clicked.connect(self.cargar_categoria_en_formulario)
        self.main_layout.addWidget(self.table)
        self.table.setColumnHidden(0, True)
    
    def limpiar_campos(self):
        self.nombre_input.clear()
        self.descripcion_input.clear()
        self.table.clearSelection()

    def cargar_categoria_en_formulario(self):
        selected_row = self.table.currentRow()
        if selected_row < 0: return
            
        nombre = self.table.item(selected_row, 1).text()
        descripcion = self.table.item(selected_row, 2).text()
        
        self.nombre_input.setText(nombre)
        self.descripcion_input.setPlainText(descripcion)

    def cargar_categorias(self):
        self.table.setRowCount(0)
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre_categoria, descripcion FROM categoria WHERE estado = 1 ORDER BY nombre_categoria")
            categorias = cursor.fetchall()
            
            self.table.setRowCount(len(categorias))
            for i, cat in enumerate(categorias):
                self.table.setItem(i, 0, QTableWidgetItem(str(cat['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(cat['nombre_categoria']))
                self.table.setItem(i, 2, QTableWidgetItem(cat.get('descripcion', '')))
            
            self.table.setColumnHidden(0, True)
        except Exception as err:
            QMessageBox.critical(self, "Error", f"Error al cargar categorías: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def filtrar_tabla(self):
        texto_busqueda = self.search_input.text().lower()
        for i in range(self.table.rowCount()):
            nombre = self.table.item(i, 1).text().lower()
            descripcion_item = self.table.item(i, 2)
            descripcion = descripcion_item.text().lower() if descripcion_item else ""
            
            if texto_busqueda in nombre or texto_busqueda in descripcion:
                self.table.setRowHidden(i, False)
            else:
                self.table.setRowHidden(i, True)

    def agregar_categoria(self):
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()

        if not nombre:
            QMessageBox.warning(self, "Campo Vacío", "El nombre de la categoría es obligatorio.")
            return

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            query = "INSERT INTO categoria (nombre_categoria, descripcion, estado) VALUES (%s, %s, 1)"
            cursor.execute(query, (nombre, descripcion))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Categoría agregada.")
            self.limpiar_campos()
            self.cargar_categorias()
            self.categories_updated.emit()
        except mysql.connector.Error as err:
            if err.errno == 1062:
                QMessageBox.warning(self, "Error", f"La categoría '{nombre}' ya existe.")
            else:
                QMessageBox.critical(self, "Error", f"Error al agregar: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def actualizar_categoria(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Seleccione una categoría para actualizar.")
            return
        
        cat_id = self.table.item(selected_row, 0).text()
        nombre = self.nombre_input.text().strip()
        descripcion = self.descripcion_input.toPlainText().strip()
        
        if not nombre:
            QMessageBox.warning(self, "Campo Vacío", "El nombre es obligatorio.")
            return

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor()
            query = "UPDATE categoria SET nombre_categoria = %s, descripcion = %s WHERE id = %s"
            cursor.execute(query, (nombre, descripcion, cat_id))
            conexion.commit()
            QMessageBox.information(self, "Éxito", "Categoría actualizada.")
            self.limpiar_campos()
            self.cargar_categorias()
            self.categories_updated.emit()
        except mysql.connector.Error as err:
            if err.errno == 1062:
                QMessageBox.warning(self, "Error", f"Ya existe otra categoría con el nombre '{nombre}'.")
            else:
                QMessageBox.critical(self, "Error", f"Error al actualizar: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def desactivar_categoria(self):
        selected_row = self.table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "Sin Selección", "Seleccione una categoría para desactivar.")
            return

        cat_id = self.table.item(selected_row, 0).text()
        nombre_cat = self.table.item(selected_row, 1).text()
        
        confirm = QMessageBox.question(self, "Confirmar", f"¿Desactivar '{nombre_cat}'?",
                                             QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                query = "UPDATE categoria SET estado = 0 WHERE id = %s"
                cursor.execute(query, (cat_id,))
                conexion.commit()
                QMessageBox.information(self, "Éxito", "Categoría desactivada.")
                self.limpiar_campos()
                self.cargar_categorias()
                self.categories_updated.emit()
            except Exception as err:
                QMessageBox.critical(self, "Error", f"Error al desactivar: {err}")
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    cursor.close()
                    conexion.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    class FakeParent(QWidget):
        def __init__(self):
            super().__init__()
            self.colores = {
                "fondo": "#1A202C", "fondo_secundario": "#2D3748",
                "texto_principal": "#E2E8F0", "texto_secundario": "#A0AEC0",
                "cabecera": "#0B6E4F", "acento": "#3A9D5A", 
                "borde": "#4A5568", "peligro": "#E53E3E", 
                "advertencia": "#ED8936", "info": "#3182CE",
                "blanco": "#FFFFFF", "negro": "#000000"
                # "fondo_claro" ya no es necesaria
            }
    
    dialog = CategoriasDialog(parent=FakeParent())
    dialog.show()
    sys.exit(app.exec())
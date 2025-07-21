import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, 
                            QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
                            QDialog, QDateEdit, QMessageBox, QHeaderView, QComboBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPalette, QColor
from datetime import datetime

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importar la clase de conexión
from conexion import ConexionBD

class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None, proveedores=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar / Editar Producto")
        self.resize(400, 400)
        
        self.layout = QVBoxLayout()
        self.proveedores = proveedores or []
    
        # Campos del formulario
        self.codigo_label = QLabel("Código:")
        self.codigo_input = QLineEdit()
        
        self.nombre_label = QLabel("Nombre:")
        self.nombre_input = QLineEdit()
        
        self.categoria_label = QLabel("Categoría:")
        self.categoria_input = QLineEdit()
        
        self.stock_actual_label = QLabel("Stock Actual:")
        self.stock_actual_input = QLineEdit()
        
        self.stock_minimo_label = QLabel("Stock Mínimo:")
        self.stock_minimo_input = QLineEdit()
        
        self.precio_venta_label = QLabel("Precio Venta:")
        self.precio_venta_input = QLineEdit()
        
        self.precio_compra_label = QLabel("Precio Compra:")
        self.precio_compra_input = QLineEdit()
        
        # Cambiar el input de proveedor por un combobox
        self.proveedor_label = QLabel("Proveedor:")
        self.proveedor_combo = QComboBox()
        # Llenar el combobox con los proveedores
        for proveedor in self.proveedores:
            self.proveedor_combo.addItem(f"{proveedor['nombre']} {proveedor['apellido']}", proveedor['id'])
        
        self.vencimiento_label = QLabel("Vencimiento:")
        self.vencimiento_input = QDateEdit()
        self.vencimiento_input.setCalendarPopup(True)
        self.vencimiento_input.setDate(QDate.currentDate())
        
        # Campo oculto para el ID (si estamos editando)
        self.product_id = None
        
        # Botones
        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("QPushButton { background-color: #ff6961; border-radius: 5px; padding: 5px; }")
        self.cancel_button.clicked.connect(self.reject)
        
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("QPushButton { background-color: #77dd77; border-radius: 5px; padding: 5px; }")
        self.ok_button.clicked.connect(self.accept)
        
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)
        
        # Añadir widgets al layout
        self.layout.addWidget(self.codigo_label)
        self.layout.addWidget(self.codigo_input)
        self.layout.addWidget(self.nombre_label)
        self.layout.addWidget(self.nombre_input)
        self.layout.addWidget(self.categoria_label)
        self.layout.addWidget(self.categoria_input)
        self.layout.addWidget(self.stock_actual_label)
        self.layout.addWidget(self.stock_actual_input)
        self.layout.addWidget(self.stock_minimo_label)
        self.layout.addWidget(self.stock_minimo_input)
        self.layout.addWidget(self.precio_venta_label)
        self.layout.addWidget(self.precio_venta_input)
        self.layout.addWidget(self.precio_compra_label)
        self.layout.addWidget(self.precio_compra_input)
        self.layout.addWidget(self.proveedor_label)
        self.layout.addWidget(self.proveedor_combo)
        self.layout.addWidget(self.vencimiento_label)
        self.layout.addWidget(self.vencimiento_input)
        self.layout.addLayout(self.button_layout)
        
        self.setLayout(self.layout)
        
        # Si se proporcionan datos, llenar el formulario
        if product_data:
            self.populate_form(product_data)
    
    def populate_form(self, product_data):
        self.product_id = product_data.get('id')
        self.codigo_input.setText(product_data.get('codigo', ''))
        self.nombre_input.setText(product_data.get('nombre', ''))
        self.categoria_input.setText(product_data.get('categoria', ''))
        self.stock_actual_input.setText(str(product_data.get('stockActual', '')))
        self.stock_minimo_input.setText(str(product_data.get('stockMinimo', '')))
        self.precio_venta_input.setText(str(product_data.get('precioVenta', '')))
        self.precio_compra_input.setText(str(product_data.get('precioCompra', '')))
        
        # Seleccionar el proveedor en el combobox
        proveedor_id = product_data.get('proveedor_id')
        if proveedor_id is not None:
            index = self.proveedor_combo.findData(proveedor_id)
            if index >= 0:
                self.proveedor_combo.setCurrentIndex(index)
        
        # Convertir la fecha de vencimiento de string a QDate
        if 'fVencimiento' in product_data and product_data['fVencimiento']:
            try:
                # Si viene como string desde la base de datos
                if isinstance(product_data['fVencimiento'], str):
                    date_obj = datetime.strptime(product_data['fVencimiento'], '%Y-%m-%d')
                    self.vencimiento_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
                else:
                    # Si ya viene como objeto datetime
                    self.vencimiento_input.setDate(QDate(
                        product_data['fVencimiento'].year,
                        product_data['fVencimiento'].month,
                        product_data['fVencimiento'].day
                    ))
            except (ValueError, AttributeError):
                self.vencimiento_input.setDate(QDate.currentDate())
    
    def get_product_data(self):
        # Obtener el ID del proveedor seleccionado
        proveedor_id = self.proveedor_combo.currentData()
        
        return {
            'id': self.product_id,  # Puede ser None si es un nuevo producto
            'codigo': self.codigo_input.text(),
            'nombre': self.nombre_input.text(),
            'categoria': self.categoria_input.text(),
            'stockActual': int(self.stock_actual_input.text() or 0),
            'stockMinimo': int(self.stock_minimo_input.text() or 0),
            'precioVenta': float(self.precio_venta_input.text() or 0),
            'precioCompra': float(self.precio_compra_input.text() or 0),
            'proveedor_id': proveedor_id,
            'fVencimiento': self.vencimiento_input.date().toString("yyyy-MM-dd"),
            'fRegistro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class InventarioWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Inventario")
        self.resize(900, 600)
        
        # Establecer el color de fondo turquesa
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#45B5AA"))
        self.setPalette(palette)
        
        # Widget central y layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Título y botón de regresar
        title_layout = QHBoxLayout()
        
        # Botón de regresar
        back_button = QPushButton("Regresar")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        back_button.clicked.connect(self.back)
        title_layout.addWidget(back_button)
        
        # Título
        title_label = QLabel("Gestión de Inventario")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Barra de búsqueda
        search_layout = QHBoxLayout()
        
        self.nombre_input = QLineEdit()
        self.nombre_input.setPlaceholderText("Nombre")
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Código")
        
        self.categoria_input = QLineEdit()
        self.categoria_input.setPlaceholderText("Categoría")
        
        # Combobox para filtrar por proveedor
        self.proveedor_combo = QComboBox()
        self.proveedor_combo.setPlaceholderText("Proveedor")
        self.proveedor_combo.addItem("Todos", -1)  # Opción para mostrar todos
        
        self.buscar_button = QPushButton("Buscar")
        self.buscar_button.setStyleSheet("QPushButton { background-color: white; border-radius: 5px; padding: 5px; }")
        self.buscar_button.clicked.connect(self.buscar_productos)
        
        self.listar_button = QPushButton("Listar Todo")
        self.listar_button.setStyleSheet("QPushButton { background-color: white; border-radius: 5px; padding: 5px; }")
        self.listar_button.clicked.connect(self.listar_todos)
        
        search_layout.addWidget(self.nombre_input)
        search_layout.addWidget(self.codigo_input)
        search_layout.addWidget(self.categoria_input)
        search_layout.addWidget(self.proveedor_combo)
        search_layout.addWidget(self.buscar_button)
        search_layout.addWidget(self.listar_button)
        
        main_layout.addLayout(search_layout)
        
        # Botones de acción
        action_layout = QHBoxLayout()
        
        self.registrar_button = QPushButton("Registrar Producto")
        self.registrar_button.setStyleSheet("QPushButton { background-color: white; border-radius: 5px; padding: 10px; }")
        self.registrar_button.clicked.connect(self.registrar_producto)
        
        self.editar_button = QPushButton("Editar Producto")
        self.editar_button.setStyleSheet("QPushButton { background-color: white; border-radius: 5px; padding: 10px; }")
        self.editar_button.clicked.connect(self.editar_producto)
        
        self.eliminar_button = QPushButton("Eliminar Producto")
        self.eliminar_button.setStyleSheet("QPushButton { background-color: white; border-radius: 5px; padding: 10px; }")
        self.eliminar_button.clicked.connect(self.eliminar_producto)
        
        # Botón de limpiar
        self.limpiar_button = QPushButton("Limpiar Tabla")
        self.limpiar_button.setStyleSheet("""
            QPushButton { 
                background-color: #d9534f; 
                color: white;
                border-radius: 5px; 
                padding: 10px; 
            }
            QPushButton:hover { 
                background-color: #c9302c; 
            }
        """)
        self.limpiar_button.clicked.connect(self.limpiar_tabla)
        
        action_layout.addWidget(self.registrar_button)
        action_layout.addWidget(self.editar_button)
        action_layout.addWidget(self.eliminar_button)
        action_layout.addWidget(self.limpiar_button)
        
        main_layout.addLayout(action_layout)
        
        # Tabla de inventario
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Stock Actual", "Stock Mínimo",
            "Precio Venta", "Precio Compra", "Proveedor", "Vencimiento"
        ])
        
        # Configurar el comportamiento de la tabla
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.table)
        
        self.setCentralWidget(central_widget)
        
        # Inicializar la lista de productos y proveedores
        self.productos = []
        self.proveedores = []
        
        # Cargar datos iniciales
        self.cargar_proveedores()
        self.cargar_productos()
    
    def cargar_proveedores(self):
        """Cargar los proveedores desde la base de datos"""
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            cursor.execute("SELECT id, nombre, apellido FROM proveedor")
            self.proveedores = cursor.fetchall()
            
            # Llenar el combobox de proveedores para filtrar
            self.proveedor_combo.clear()
            self.proveedor_combo.addItem("Todos", -1)
            for proveedor in self.proveedores:
                self.proveedor_combo.addItem(
                    f"{proveedor['nombre']} {proveedor['apellido']}", 
                    proveedor['id']
                )
            
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar proveedores: {str(e)}")
    
    def cargar_productos(self):
        """Cargar todos los productos desde la base de datos"""
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # Consulta con JOIN para obtener el nombre del proveedor
            query = """
            SELECT p.*, CONCAT(prov.nombre, ' ', prov.apellido) as proveedor_nombre
            FROM producto p
            LEFT JOIN proveedor prov ON p.proveedor_id = prov.id
            """
            
            cursor.execute(query)
            self.productos = cursor.fetchall()
            cursor.close()
            
            self.actualizar_tabla()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar productos: {str(e)}")
    
    def actualizar_tabla(self, productos_filtrados=None):
        productos_mostrados = productos_filtrados if productos_filtrados is not None else self.productos
        
        self.table.setRowCount(0)  # Limpiar tabla
        
        for row_index, producto in enumerate(productos_mostrados):
            self.table.insertRow(row_index)
            
            # Columna ID (oculta para el usuario, pero útil para operaciones)
            id_item = QTableWidgetItem(str(producto['id']))
            self.table.setItem(row_index, 0, id_item)
            
            self.table.setItem(row_index, 1, QTableWidgetItem(producto['codigo']))
            self.table.setItem(row_index, 2, QTableWidgetItem(producto['nombre']))
            self.table.setItem(row_index, 3, QTableWidgetItem(producto['categoria']))
            self.table.setItem(row_index, 4, QTableWidgetItem(str(producto['stockActual'])))
            self.table.setItem(row_index, 5, QTableWidgetItem(str(producto['stockMinimo'])))
            self.table.setItem(row_index, 6, QTableWidgetItem(str(producto['precioVenta'])))
            self.table.setItem(row_index, 7, QTableWidgetItem(str(producto['precioCompra'])))
            
            # Columna del proveedor (muestra el nombre, no el ID)
            proveedor_nombre = producto.get('proveedor_nombre', 'Sin proveedor')
            self.table.setItem(row_index, 8, QTableWidgetItem(proveedor_nombre))
            
            # Formatear la fecha de vencimiento
            fecha_vencimiento = producto.get('fVencimiento', '')
            if fecha_vencimiento:
                if isinstance(fecha_vencimiento, datetime):
                    fecha_str = fecha_vencimiento.strftime('%Y-%m-%d')
                else:
                    fecha_str = str(fecha_vencimiento)
                self.table.setItem(row_index, 9, QTableWidgetItem(fecha_str))
            else:
                self.table.setItem(row_index, 9, QTableWidgetItem(""))
        
        # Ocultar la columna ID
        self.table.setColumnHidden(0, True)
    
    def registrar_producto(self):
        """Registrar un nuevo producto en la base de datos"""
        dialog = ProductDialog(self, proveedores=self.proveedores)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            nuevo_producto = dialog.get_product_data()
            
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                # Insertar el nuevo producto
                query = """
                INSERT INTO producto (codigo, nombre, categoria, stockActual, stockMinimo,
                                    precioVenta, precioCompra, proveedor_id, fVencimiento, fRegistro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    nuevo_producto['codigo'],
                    nuevo_producto['nombre'],
                    nuevo_producto['categoria'],
                    nuevo_producto['stockActual'],
                    nuevo_producto['stockMinimo'],
                    nuevo_producto['precioVenta'],
                    nuevo_producto['precioCompra'],
                    nuevo_producto['proveedor_id'],
                    nuevo_producto['fVencimiento'],
                    nuevo_producto['fRegistro']
                )
                
                cursor.execute(query, valores)
                conexion.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto registrado correctamente")
                self.cargar_productos()  # Recargar todos los productos
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al registrar producto: {str(e)}")
    
    def editar_producto(self):
        """Editar un producto existente"""
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un producto para editar")
            return
        
        # Obtener el índice de la fila seleccionada
        selected_row = selected_rows[0].row()
        
        # Obtener el ID del producto seleccionado (está en la columna 0)
        producto_id = int(self.table.item(selected_row, 0).text())
        
        # Encontrar el producto seleccionado en la lista
        producto_seleccionado = next((p for p in self.productos if p['id'] == producto_id), None)
        
        if not producto_seleccionado:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el producto seleccionado")
            return
        
        # Abrir el diálogo de edición
        dialog = ProductDialog(self, producto_seleccionado, self.proveedores)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            producto_editado = dialog.get_product_data()
            
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                # Actualizar el producto
                query = """
                UPDATE producto
                SET codigo = %s, nombre = %s, categoria = %s, stockActual = %s, stockMinimo = %s,
                    precioVenta = %s, precioCompra = %s, proveedor_id = %s, fVencimiento = %s
                WHERE id = %s
                """
                valores = (
                    producto_editado['codigo'],
                    producto_editado['nombre'],
                    producto_editado['categoria'],
                    producto_editado['stockActual'],
                    producto_editado['stockMinimo'],
                    producto_editado['precioVenta'],
                    producto_editado['precioCompra'],
                    producto_editado['proveedor_id'],
                    producto_editado['fVencimiento'],
                    producto_id
                )
                
                cursor.execute(query, valores)
                conexion.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
                self.cargar_productos()  # Recargar todos los productos
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar producto: {str(e)}")
    
    def eliminar_producto(self):
        """Eliminar un producto de la base de datos"""
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un producto para eliminar")
            return
        
        selected_row = selected_rows[0].row()
        producto_id = int(self.table.item(selected_row, 0).text())
        nombre_producto = self.table.item(selected_row, 2).text()
        
        # Confirmar eliminación
        confirmation = QMessageBox.question(
            self, "Confirmar eliminación", 
            f"¿Está seguro que desea eliminar el producto '{nombre_producto}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                # Eliminar el producto
                query = "DELETE FROM producto WHERE id = %s"
                cursor.execute(query, (producto_id,))
                conexion.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.cargar_productos()  # Recargar todos los productos
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar producto: {str(e)}")
    
    def limpiar_tabla(self):
        """Limpiar la visualización de la tabla sin eliminar los productos"""
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Información", "La tabla ya está vacía")
            return
        
        # Simplemente vaciar la tabla sin modificar los datos
        self.table.setRowCount(0)
        QMessageBox.information(self, "Éxito", "Tabla limpiada correctamente")
    
    def buscar_productos(self):
        """Buscar productos según los criterios especificados"""
        nombre = self.nombre_input.text().strip()
        codigo = self.codigo_input.text().strip()
        categoria = self.categoria_input.text().strip()
        proveedor_id = self.proveedor_combo.currentData()
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # Construir la consulta base
            query = """
            SELECT p.*, CONCAT(prov.nombre, ' ', prov.apellido) as proveedor_nombre
            FROM producto p
            LEFT JOIN proveedor prov ON p.proveedor_id = prov.id
            WHERE 1=1
            """
            
            parametros = []
            
            # Añadir condiciones según los filtros ingresados
            if nombre:
                query += " AND p.nombre LIKE %s"
                parametros.append(f"%{nombre}%")
            
            if codigo:
                query += " AND p.codigo LIKE %s"
                parametros.append(f"%{codigo}%")
            
            if categoria:
                query += " AND p.categoria LIKE %s"
                parametros.append(f"%{categoria}%")
            
            if proveedor_id != -1:  # Si no es "Todos"
                query += " AND p.proveedor_id = %s"
                parametros.append(proveedor_id)
            
            cursor.execute(query, parametros)
            productos_filtrados = cursor.fetchall()
            cursor.close()
            
            if not productos_filtrados:
                QMessageBox.information(self, "Información", "No se encontraron productos con los criterios especificados")
            
            self.actualizar_tabla(productos_filtrados)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al buscar productos: {str(e)}")
    
    def listar_todos(self):
        """Limpiar los filtros y mostrar todos los productos"""
        self.nombre_input.clear()
        self.codigo_input.clear()
        self.categoria_input.clear()
        self.proveedor_combo.setCurrentIndex(0)  # Seleccionar "Todos"
        self.cargar_productos()
    
    def back(self):
        """Regresar y mostrar principal"""
        from principal import MainWindow   # Importación dentro de la función para evitar el ciclo
        
        # Crear y mostrar la ventana principal
        self.prin_window = MainWindow('Empleado')
        self.prin_window.show()
        
        # Cerrar la ventana actual
        self.close()

# Solo ejecutar si se llama directamente
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventarioWindow()
    window.show()
    sys.exit(app.exec())
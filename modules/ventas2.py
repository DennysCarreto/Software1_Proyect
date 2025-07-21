import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, 
                            QMessageBox, QDateEdit, QHeaderView, QDialog, QDialogButtonBox, QComboBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPalette, QColor, QFont, QIntValidator
import mysql.connector

class NuevaVentaDialog(QDialog):
    def __init__(self, clientes, productos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Venta")
        self.resize(600, 400)
        
        layout = QVBoxLayout()
        
        # Selección de cliente
        self.cliente_combo = QComboBox()
        self.cliente_combo.addItem("Consumidor Final", 0)
        for cliente in clientes:
            self.cliente_combo.addItem(f"{cliente['nombre']} {cliente['apellido']}", cliente['id'])
        layout.addWidget(QLabel("Cliente:"))
        layout.addWidget(self.cliente_combo)
        
        # Tabla de productos
        self.productos_table = QTableWidget()
        self.productos_table.setColumnCount(4)
        self.productos_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "Total"])
        self.productos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.productos_table.setColumnHidden(0, True)
        layout.addWidget(self.productos_table)
        
        # Botones para productos
        btn_layout = QHBoxLayout()
        self.agregar_btn = QPushButton("Agregar Producto")
        self.agregar_btn.clicked.connect(self.agregar_producto)
        self.eliminar_btn = QPushButton("Eliminar Producto")
        self.eliminar_btn.clicked.connect(self.eliminar_producto)
        btn_layout.addWidget(self.agregar_btn)
        btn_layout.addWidget(self.eliminar_btn)
        layout.addLayout(btn_layout)
        
        # Total
        self.total_label = QLabel("Total: Q0.00")
        self.total_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(self.total_label)
        
        # Botones de acción
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.productos_disponibles = productos
        self.productos_seleccionados = []
    
    def agregar_producto(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar Producto")
        dialog_layout = QVBoxLayout()
        
        producto_combo = QComboBox()
        for producto in self.productos_disponibles:
            producto_combo.addItem(f"{producto['nombre']} - Q{float(producto['precioVenta']):.2f}", producto['id'])
        dialog_layout.addWidget(QLabel("Producto:"))
        dialog_layout.addWidget(producto_combo)
        
        cantidad_input = QLineEdit("1")
        cantidad_input.setValidator(QIntValidator(1, 999))
        dialog_layout.addWidget(QLabel("Cantidad:"))
        dialog_layout.addWidget(cantidad_input)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btn_box.accepted.connect(dialog.accept)
        btn_box.rejected.connect(dialog.reject)
        dialog_layout.addWidget(btn_box)
        
        dialog.setLayout(dialog_layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            producto_id = producto_combo.currentData()
            cantidad = int(cantidad_input.text())
            
            producto = next((p for p in self.productos_disponibles if p['id'] == producto_id), None)
            if producto:
                total = float(producto['precioVenta']) * cantidad
                
                self.productos_seleccionados.append({
                    'id': producto_id,
                    'nombre': producto['nombre'],
                    'cantidad': cantidad,
                    'total': total
                })
                
                self.actualizar_tabla()
                self.calcular_total()
    
    def eliminar_producto(self):
        selected = self.productos_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione un producto para eliminar")
            return
        
        row = selected[0].row()
        if 0 <= row < len(self.productos_seleccionados):
            del self.productos_seleccionados[row]
            self.actualizar_tabla()
            self.calcular_total()
    
    def actualizar_tabla(self):
        self.productos_table.setRowCount(len(self.productos_seleccionados))
        for row, producto in enumerate(self.productos_seleccionados):
            self.productos_table.setItem(row, 0, QTableWidgetItem(str(producto['id'])))
            self.productos_table.setItem(row, 1, QTableWidgetItem(producto['nombre']))
            self.productos_table.setItem(row, 2, QTableWidgetItem(str(producto['cantidad'])))
            self.productos_table.setItem(row, 3, QTableWidgetItem(f"Q{producto['total']:.2f}"))
    
    def calcular_total(self):
        total = sum(p['total'] for p in self.productos_seleccionados)
        self.total_label.setText(f"Total: Q{total:.2f}")
    
    def get_venta_data(self):
        return {
            'cliente_id': self.cliente_combo.currentData(),
            'productos': self.productos_seleccionados,
            'total': sum(p['total'] for p in self.productos_seleccionados)
        }

class VentasWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Ventas")
        self.resize(900, 600)
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor("#45B5AA"))
        self.setPalette(palette)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Barra superior con título y botón de regresar
        title_layout = QHBoxLayout()
        
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
        back_button.clicked.connect(self.go_back_to_main)
        title_layout.addWidget(back_button)
        
        title_label = QLabel("Gestión de Ventas")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Filtros de búsqueda
        search_layout = QHBoxLayout()
        
        self.fecha_inicio = QDateEdit(QDate.currentDate().addDays(-7))
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_fin = QDateEdit(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        
        self.cliente_input = QLineEdit()
        self.cliente_input.setPlaceholderText("Cliente")
        
        self.buscar_btn = QPushButton("Buscar")
        self.buscar_btn.setStyleSheet("QPushButton { background-color: white; border-radius: 5px; padding: 5px; }")
        self.buscar_btn.clicked.connect(self.buscar_ventas)
        
        self.nueva_venta_btn = QPushButton("Nueva Venta")
        self.nueva_venta_btn.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        self.nueva_venta_btn.clicked.connect(self.nueva_venta)
        
        search_layout.addWidget(QLabel("Desde:"))
        search_layout.addWidget(self.fecha_inicio)
        search_layout.addWidget(QLabel("Hasta:"))
        search_layout.addWidget(self.fecha_fin)
        search_layout.addWidget(self.cliente_input)
        search_layout.addWidget(self.buscar_btn)
        search_layout.addWidget(self.nueva_venta_btn)
        
        main_layout.addLayout(search_layout)
        
        # Tabla de ventas
        self.ventas_table = QTableWidget()
        self.ventas_table.setColumnCount(5)
        self.ventas_table.setHorizontalHeaderLabels(["ID", "Fecha", "Cliente", "Total", "Vendedor"])
        self.ventas_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ventas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ventas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        main_layout.addWidget(self.ventas_table)
        self.setCentralWidget(central_widget)
        self.cargar_ventas()
    
    def cargar_ventas(self, filtros=None):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="admin",
                database="farmaplus"
            )
            cursor = conexion.cursor(dictionary=True)
            
            # Verificar si la tabla ventas existe
            cursor.execute("SHOW TABLES LIKE 'ventas'")
            if not cursor.fetchone():
                QMessageBox.warning(self, "Error", "La tabla 'ventas' no existe en la base de datos")
                return
            
            query = """
            SELECT v.id, v.fechaVenta as fecha, v.total,
                   CONCAT(c.nombre, ' ', c.apellido) as cliente_nombre,
                   CONCAT(u.nombre, ' ', u.apellido) as vendedor
            FROM ventas v
            LEFT JOIN cliente c ON v.cliente_id = c.id
            LEFT JOIN usuario u ON v.usuario_id = u.id
            WHERE 1=1
            """
            
            params = []
            
            if filtros:
                if 'fecha_inicio' in filtros:
                    query += " AND v.fechaVenta >= %s"
                    params.append(filtros['fecha_inicio'])
                
                if 'fecha_fin' in filtros:
                    query += " AND v.fechaVenta <= %s"
                    params.append(filtros['fecha_fin'])
                
                if 'cliente' in filtros:
                    query += " AND (c.nombre LIKE %s OR c.apellido LIKE %s)"
                    params.append(f"%{filtros['cliente']}%")
                    params.append(f"%{filtros['cliente']}%")
            
            query += " ORDER BY v.fechaVenta DESC, v.id DESC"
            
            cursor.execute(query, params)
            ventas = cursor.fetchall()
            
            self.ventas_table.setRowCount(0)
            
            for row, venta in enumerate(ventas):
                self.ventas_table.insertRow(row)
                self.ventas_table.setItem(row, 0, QTableWidgetItem(str(venta['id'])))
                self.ventas_table.setItem(row, 1, QTableWidgetItem(str(venta['fecha'])))
                self.ventas_table.setItem(row, 2, QTableWidgetItem(venta['cliente_nombre'] or "Consumidor Final"))
                self.ventas_table.setItem(row, 3, QTableWidgetItem(f"Q{float(venta['total']):.2f}"))
                self.ventas_table.setItem(row, 4, QTableWidgetItem(venta['vendedor'] or "Sistema"))
            
            cursor.close()
            conexion.close()
            
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error", f"Error al cargar ventas: {error}")
    
    def buscar_ventas(self):
        filtros = {
            'fecha_inicio': self.fecha_inicio.date().toString("yyyy-MM-dd"),
            'fecha_fin': self.fecha_fin.date().toString("yyyy-MM-dd")
        }
        
        if self.cliente_input.text().strip():
            filtros['cliente'] = self.cliente_input.text().strip()
        
        self.cargar_ventas(filtros)
    
    def nueva_venta(self):
        try:
            conexion = mysql.connector.connect(
                host="localhost",
                user="root",
                password="admin",
                database="farmaplus"
            )
            
            # Obtener clientes activos
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, apellido FROM cliente WHERE activo = 1")
            clientes = cursor.fetchall()
            
            # Obtener productos con stock
            cursor.execute("""
                SELECT id, nombre, precioVenta, stockActual 
                FROM producto 
                WHERE stockActual > 0
                ORDER BY nombre
            """)
            productos = cursor.fetchall()
            
            cursor.close()
            
            if not productos:
                QMessageBox.warning(self, "Advertencia", "No hay productos con stock disponible")
                return
            
            dialog = NuevaVentaDialog(clientes, productos, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                venta_data = dialog.get_venta_data()
                
                if not venta_data['productos']:
                    QMessageBox.warning(self, "Advertencia", "Debe agregar al menos un producto")
                    return
                
                cursor = conexion.cursor()
                
                # Insertar venta principal
                venta_query = """
                INSERT INTO ventas (cliente_id, fechaVenta, total, usuario_id)
                VALUES (%s, CURDATE(), %s, 1)
                """
                venta_values = (
                    venta_data['cliente_id'] if venta_data['cliente_id'] != 0 else None,
                    str(venta_data['total'])  # Convertir a string para tu estructura actual
                )
                
                cursor.execute(venta_query, venta_values)
                venta_id = cursor.lastrowid
                
                # Insertar detalles de venta
                for producto in venta_data['productos']:
                    
                    detalle_query = """
                    INSERT INTO detalle_venta 
                    (ventas_id, producto_id, cantidad, precio_unitario, subtotal)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    for producto in venta_data['productos']:
                        precio_unitario = float(producto['total']) / producto['cantidad']
                        subtotal = float(producto['total'])  # Ya lo tienes calculado como producto['total']
                        
                        cursor.execute(detalle_query, (
                            venta_id,
                            producto['id'],
                            producto['cantidad'],
                            precio_unitario,
                            subtotal
                        ))
                
                    
                    # Actualizar stock
                    update_query = "UPDATE producto SET stockActual = stockActual - %s WHERE id = %s"
                    cursor.execute(update_query, (producto['cantidad'], producto['id']))
                
                conexion.commit()
                cursor.close()
                conexion.close()
                
                QMessageBox.information(self, "Éxito", "Venta registrada correctamente")
                self.cargar_ventas()
        
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error", f"Error al registrar venta: {error}")
            if 'cursor' in locals():
                cursor.close()
            if 'conexion' in locals() and conexion.is_connected():
                conexion.close()
    
    def go_back_to_main(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentasWindow()
    window.show()
    sys.exit(app.exec())
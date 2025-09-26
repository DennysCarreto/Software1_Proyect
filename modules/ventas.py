import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, 
                            QMessageBox, QDateEdit, QHeaderView, QDialog, QDialogButtonBox, QComboBox, QFrame)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPalette, QColor, QFont, QIntValidator
from conexion import ConexionBD
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
    
    def agregar_producto_por_id(self, producto_id, cantidad=1):
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
            return True
        return False
    
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
        self.setMinimumSize(1200, 800)
        
        # ### <<< MEJORA: Aplicar la paleta de colores profesional >>> ###
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
        
        # --- Construcción de la UI modular ---
        self.setup_header_bar()
        self.setup_control_panel()
        self.setup_table()
        
        # Cargar datos iniciales
        self.cargar_ventas()

    def _create_stylesheets(self):
        """Método central para definir todos los estilos de la ventana."""
        self.style_header_label = f"font-size: 22px; font-weight: bold; color: white; background: transparent;"
        self.style_header_button = f"""
            QPushButton {{ background-color: #FFFFFF; color: {self.colores['texto_principal']};
                border: none; border-radius: 5px; padding: 8px 12px; font-weight: bold;
            }} QPushButton:hover {{ background-color: #E2E8F0; }}
        """
        self.style_input_field = f"""
            QLineEdit, QDateEdit, QComboBox {{ border: 1px solid {self.colores['borde']}; border-radius: 5px;
                padding: 8px; font-size: 14px; background-color: white; color: {self.colores['texto_principal']};
            }}
        """
        self.style_primary_button = f"""
            QPushButton {{ background-color: {self.colores['acento']}; color: white;
                border: none; border-radius: 5px; padding: 10px; font-weight: bold;
            }} QPushButton:hover {{ background-color: {self.colores['cabecera']}; }}
        """
        self.style_table = f"""
            QTableWidget {{ border: 1px solid {self.colores['borde']}; gridline-color: {self.colores['borde']}; font-size: 13px; }}
            QHeaderView::section {{ background-color: {self.colores['cabecera']}; color: white; padding: 8px;
                border: 1px solid {self.colores['cabecera']}; font-weight: bold;
            }}
            QTableWidget::item:selected {{ background-color: {self.colores['acento']}; color: white; }}
        """

    def setup_header_bar(self):
        header_frame = QWidget()
        header_frame.setStyleSheet(f"background-color: {self.colores['cabecera']};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)

        back_button = QPushButton("Regresar")
        back_button.setStyleSheet(self.style_header_button)
        back_button.clicked.connect(self.go_back_to_main)
        
        title_label = QLabel("Gestión de Ventas")
        title_label.setStyleSheet(self.style_header_label)

        header_layout.addWidget(back_button)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.main_layout.addWidget(header_frame)

    def setup_control_panel(self):
        control_frame = QFrame()
        control_frame.setStyleSheet(f"margin: 0 10px;")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)
        
        # --- Filtros de búsqueda ---
        search_layout = QHBoxLayout()
        self.fecha_inicio = QDateEdit(QDate.currentDate().addDays(-30))
        self.fecha_fin = QDateEdit(QDate.currentDate())
        self.cliente_input = QLineEdit()
        self.cliente_input.setPlaceholderText("Nombre o Apellido del Cliente")
        self.buscar_btn = QPushButton("Buscar Ventas")
        self.buscar_btn.setStyleSheet(self.style_header_button)

        for widget in [self.fecha_inicio, self.fecha_fin, self.cliente_input]:
            widget.setStyleSheet(self.style_input_field)

        search_layout.addWidget(QLabel("Desde:"))
        search_layout.addWidget(self.fecha_inicio)
        search_layout.addWidget(QLabel("Hasta:"))
        search_layout.addWidget(self.fecha_fin)
        search_layout.addWidget(self.cliente_input, 1)
        search_layout.addWidget(self.buscar_btn)
        control_layout.addLayout(search_layout)
        
        # --- Botones de acción ---
        action_layout = QHBoxLayout()
        self.nueva_venta_btn = QPushButton("➕ Registrar Nueva Venta")
        self.nueva_venta_btn.setStyleSheet(self.style_primary_button)
        action_layout.addWidget(self.nueva_venta_btn)
        action_layout.addStretch()
        control_layout.addLayout(action_layout)
        
        self.main_layout.addWidget(control_frame)
        
        # Conexiones
        self.buscar_btn.clicked.connect(self.buscar_ventas)
        self.nueva_venta_btn.clicked.connect(self.nueva_venta)

    def setup_table(self):
        self.ventas_table = QTableWidget()
        self.ventas_table.setColumnCount(5)
        self.ventas_table.setHorizontalHeaderLabels(["ID Venta", "Fecha", "Cliente", "Total", "Vendedor"])
        self.ventas_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.ventas_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.ventas_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.ventas_table.verticalHeader().setVisible(False)
        self.ventas_table.setStyleSheet(self.style_table)
        self.main_layout.addWidget(self.ventas_table)

    def cargar_ventas(self, filtros=None):
        QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)
        self.ventas_table.setRowCount(0)
        try:
            # ### <<< MEJORA: Usar la conexión centralizada >>> ###
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # ### <<< CORRECCIÓN: Consulta optimizada con GROUP BY para evitar duplicados >>> ###
            query = """
            SELECT v.id, v.fechaVenta as fecha, v.total,
                   COALESCE(CONCAT(c.nombre, ' ', c.apellido), 'Consumidor Final') as cliente_nombre,
                   COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sistema') as vendedor
            FROM ventas v
            LEFT JOIN cliente c ON v.cliente_id = c.id
            LEFT JOIN usuario u ON v.usuario_id = u.id
            WHERE 1=1
            """
            
            params = []
            if filtros:
                if filtros.get('fecha_inicio'):
                    query += " AND v.fechaVenta >= %s"
                    params.append(filtros['fecha_inicio'])
                if filtros.get('fecha_fin'):
                    query += " AND v.fechaVenta <= %s"
                    params.append(filtros['fecha_fin'])
                if filtros.get('cliente'):
                    query += " AND (c.nombre LIKE %s OR c.apellido LIKE %s)"
                    params.extend([f"%{filtros['cliente']}%", f"%{filtros['cliente']}%"])
            
            # Agrupamos por ID de venta para asegurar una sola fila por venta
            query += " GROUP BY v.id ORDER BY v.fechaVenta DESC, v.id DESC"
            
            cursor.execute(query, params)
            ventas = cursor.fetchall()
            
            self.ventas_table.setRowCount(len(ventas))
            for row, venta in enumerate(ventas):
                self.ventas_table.setItem(row, 0, QTableWidgetItem(str(venta['id'])))
                self.ventas_table.setItem(row, 1, QTableWidgetItem(venta['fecha'].strftime('%Y-%m-%d')))
                self.ventas_table.setItem(row, 2, QTableWidgetItem(venta['cliente_nombre']))
                self.ventas_table.setItem(row, 3, QTableWidgetItem(f"Q{float(venta['total']):.2f}"))
                self.ventas_table.setItem(row, 4, QTableWidgetItem(venta['vendedor']))
            
            cursor.close()
            conexion.close()
            
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al cargar ventas:\n{error}")
        finally:
            QApplication.restoreOverrideCursor()
    
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
                password="root",
                database="dbfarmaplus"
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
            
            self.venta_dialog = NuevaVentaDialog(clientes, productos, self)
            if self.venta_dialog.exec() == QDialog.DialogCode.Accepted:
                venta_data = self.venta_dialog.get_venta_data()
                
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
                    str(venta_data['total'])
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
                    precio_unitario = float(producto['total']) / producto['cantidad']
                    subtotal = float(producto['total'])
                    
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
        finally:
            self.venta_dialog = None
    
    def go_back_to_main(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentasWindow()
    window.show()
    sys.exit(app.exec())
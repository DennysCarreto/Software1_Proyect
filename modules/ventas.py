import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTableWidget, QTableWidgetItem, QLineEdit, 
                            QMessageBox, QDateEdit, QHeaderView, QDialog, QDialogButtonBox, QComboBox, QFrame,
                            QSpinBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QPalette, QColor, QFont, QIntValidator
from conexion import ConexionBD
import mysql.connector

class NuevaVentaDialog(QDialog):
    def __init__(self, clientes, productos, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nueva Venta")
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Selección de cliente
        cliente_layout = QHBoxLayout()
        cliente_layout.addWidget(QLabel("Cliente:"))
        self.cliente_combo = QComboBox()
        self.cliente_combo.addItem("Consumidor Final", 0)
        for cliente in clientes:
            self.cliente_combo.addItem(f"{cliente['nombre']} {cliente['apellido']}", cliente['id'])
        cliente_layout.addWidget(self.cliente_combo)
        cliente_layout.addStretch()
        layout.addLayout(cliente_layout)
        
        # --- NUEVA SECCIÓN: Búsqueda rápida de productos ---
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Buscar Producto:"))
        self.product_search_input = QLineEdit()
        self.product_search_input.setPlaceholderText("Escriba el nombre o código del producto...")
        self.product_search_input.textChanged.connect(self.buscar_productos_en_tiempo_real)
        search_layout.addWidget(self.product_search_input, 1)
        
        layout.addLayout(search_layout)
        
        # Tabla de resultados de búsqueda
        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(5)
        self.search_results_table.setHorizontalHeaderLabels(["ID", "Código", "Producto", "Stock", "Precio"])
        self.search_results_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.search_results_table.setColumnHidden(0, True)
        self.search_results_table.setMaximumHeight(150)
        self.search_results_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.search_results_table.doubleClicked.connect(self.agregar_desde_busqueda)
        layout.addWidget(self.search_results_table)
        
        # Información del producto seleccionado
        self.product_info_layout = QHBoxLayout()
        self.product_info_layout.addWidget(QLabel("Producto seleccionado:"))
        self.selected_product_label = QLabel("Ninguno")
        self.selected_product_label.setStyleSheet("font-weight: bold; color: #2E86AB;")
        self.product_info_layout.addWidget(self.selected_product_label)
        
        self.product_info_layout.addWidget(QLabel("Cantidad:  "))
        self.cantidad_spinbox = QSpinBox()
        self.cantidad_spinbox.setMinimum(1)
        self.cantidad_spinbox.setMaximum(1000)
        self.cantidad_spinbox.setValue(1)
        self.product_info_layout.addWidget(self.cantidad_spinbox)
        
        self.agregar_rapido_btn = QPushButton("➕ Agregar a Venta")
        self.agregar_rapido_btn.setStyleSheet("background-color: #27AE60; color: white; padding: 5px; border-radius: 3px;")
        self.agregar_rapido_btn.clicked.connect(self.agregar_producto_rapido)
        self.agregar_rapido_btn.setEnabled(False)
        self.product_info_layout.addWidget(self.agregar_rapido_btn)
        
        self.product_info_layout.addStretch()
        layout.addLayout(self.product_info_layout)
        
        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)
        
        # Tabla de productos en la venta
        layout.addWidget(QLabel("Productos en la Venta:"))
        self.productos_table = QTableWidget()
        self.productos_table.setColumnCount(5)
        self.productos_table.setHorizontalHeaderLabels(["ID", "Producto", "Cantidad", "P. Unitario", "Subtotal"])
        self.productos_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.productos_table.setColumnHidden(0, True)
        self.productos_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        layout.addWidget(self.productos_table)
        
        # Botones para gestionar productos en la venta
        btn_layout = QHBoxLayout()
        self.modificar_cantidad_btn = QPushButton("✏️ Modificar Cantidad")
        self.modificar_cantidad_btn.clicked.connect(self.modificar_cantidad)
        self.eliminar_btn = QPushButton("❌ Eliminar Producto")
        self.eliminar_btn.clicked.connect(self.eliminar_producto)
        btn_layout.addWidget(self.modificar_cantidad_btn)
        btn_layout.addWidget(self.eliminar_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # Total
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        self.total_label = QLabel("Total: Q0.00")
        self.total_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #2E86AB; padding: 10px;")
        total_layout.addWidget(self.total_label)
        layout.addLayout(total_layout)
        
        # Botones de acción
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.validar_y_aceptar)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        self.productos_disponibles = productos
        self.productos_seleccionados = []
        self.producto_actual_seleccionado = None
        
        # Aplicar estilos
        self.aplicar_estilos()

    def aplicar_estilos(self):
        self.search_results_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #DEE2E6;
                gridline-color: #DEE2E6;
                font-size: 12px;
                background-color: white;
                color: #000000;  /* Letra negra */
                selection-background-color: #3498DB;  /* Color azul para selección */
                selection-color: white;                                
            }
            QTableWidget::item:selected {
                background-color: #3498DB;  /* Azul cuando está seleccionado */
                color: white;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #EBF5FB;  /* Azul claro al pasar el mouse */
                color: #000000;
            }                                    
            QHeaderView::section {
                background-color: #0B6E4F;
                color: white;
                padding: 6px;
                border: 1px solid #0B6E4F;
                font-weight: bold;
            }
        """)
        
        self.productos_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #DEE2E6;
                gridline-color: #DEE2E6;
                font-size: 13px;
                background-color: white;
                color: #000000;  /* Letra negra */
                selection-background-color: #2E86AB;  /* Color diferente para distinguir */
                selection-color: white;                           
            }
            QTableWidget::item:selected {
                background-color: #2E86AB;  /* Azul oscuro cuando está seleccionado */
                color: white;
                font-weight: bold;
            }
            QTableWidget::item:hover {
                background-color: #E8F4F8;  /* Azul muy claro al pasar el mouse */
                color: #000000;
            }                               
            QHeaderView::section {
                background-color: #2E86AB;
                color: white;
                padding: 8px;
                border: 1px solid #2E86AB;
                font-weight: bold;
            }
        """)

    def buscar_productos_en_tiempo_real(self):
        texto_busqueda = self.product_search_input.text().lower().strip()
        
        if not texto_busqueda:
            self.search_results_table.setRowCount(0)
            self.agregar_rapido_btn.setEnabled(False)
            self.selected_product_label.setText("Ninguno")
            self.producto_actual_seleccionado = None
            return
        
        productos_filtrados = []
        for producto in self.productos_disponibles:
            nombre_match = texto_busqueda in producto['nombre'].lower()
            codigo_match = texto_busqueda in producto.get('codigo', '').lower()
            
            if nombre_match or codigo_match:
                productos_filtrados.append(producto)
        
        self.mostrar_resultados_busqueda(productos_filtrados)

    def mostrar_resultados_busqueda(self, productos):
        self.search_results_table.setRowCount(len(productos))
        
        for row, producto in enumerate(productos):
            self.search_results_table.setItem(row, 0, QTableWidgetItem(str(producto['id'])))
            self.search_results_table.setItem(row, 1, QTableWidgetItem(producto.get('codigo', 'N/A')))
            self.search_results_table.setItem(row, 2, QTableWidgetItem(producto['nombre']))
            self.search_results_table.setItem(row, 3, QTableWidgetItem(str(producto['stockActual'])))
            self.search_results_table.setItem(row, 4, QTableWidgetItem(f"Q{float(producto['precioVenta']):.2f}"))
        
        # Seleccionar automáticamente la primera fila si hay resultados
        if productos:
            self.search_results_table.selectRow(0)
            self.seleccionar_producto_desde_busqueda(0, 0)

    def seleccionar_producto_desde_busqueda(self, row, column):
        if row < self.search_results_table.rowCount():
            producto_id = int(self.search_results_table.item(row, 0).text())
            producto_nombre = self.search_results_table.item(row, 2).text()
            producto_stock = int(self.search_results_table.item(row, 3).text())
            producto_precio = float(self.search_results_table.item(row, 4).text().replace('Q', ''))
            
            self.producto_actual_seleccionado = {
                'id': producto_id,
                'nombre': producto_nombre,
                'stock': producto_stock,
                'precio': producto_precio
            }
            
            self.selected_product_label.setText(f"{producto_nombre} (Stock: {producto_stock})")
            self.agregar_rapido_btn.setEnabled(True)
            
            # Establecer cantidad máxima según stock disponible
            self.cantidad_spinbox.setMaximum(producto_stock)

    def agregar_desde_busqueda(self, index):
        row = index.row()
        self.seleccionar_producto_desde_busqueda(row, 0)
        self.agregar_producto_rapido()

    def agregar_producto_rapido(self):
        if not self.producto_actual_seleccionado:
            QMessageBox.warning(self, "Advertencia", "No hay producto seleccionado.")
            return
        
        cantidad = self.cantidad_spinbox.value()
        producto = self.producto_actual_seleccionado
        
        if cantidad > producto['stock']:
            QMessageBox.warning(self, "Stock Insuficiente", 
                               f"No hay suficiente stock. Stock disponible: {producto['stock']}")
            return
        
        # Verificar si el producto ya está en la venta
        for item in self.productos_seleccionados:
            if item['id'] == producto['id']:
                # Preguntar si quiere actualizar la cantidad
                respuesta = QMessageBox.question(self, "Producto Existente", 
                                               f"El producto '{producto['nombre']}' ya está en la venta. ¿Desea actualizar la cantidad?",
                                               QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
                if respuesta == QMessageBox.StandardButton.Yes:
                    item['cantidad'] = cantidad
                    item['total'] = producto['precio'] * cantidad
                self.actualizar_tabla_venta()
                self.calcular_total()
                return
        
        # Agregar nuevo producto
        nuevo_producto = {
            'id': producto['id'],
            'nombre': producto['nombre'],
            'cantidad': cantidad,
            'precio_unitario': producto['precio'],
            'total': producto['precio'] * cantidad
        }
        
        self.productos_seleccionados.append(nuevo_producto)
        self.actualizar_tabla_venta()
        self.calcular_total()
        
        # Limpiar búsqueda después de agregar
        self.product_search_input.clear()
        self.selected_product_label.setText("Ninguno")
        self.agregar_rapido_btn.setEnabled(False)
        self.producto_actual_seleccionado = None

    def modificar_cantidad(self):
        selected = self.productos_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione un producto para modificar la cantidad.")
            return
        
        row = selected[0].row()
        producto_id = int(self.productos_table.item(row, 0).text())
        producto_nombre = self.productos_table.item(row, 1).text()
        cantidad_actual = int(self.productos_table.item(row, 2).text())
        
        # Encontrar el producto en la lista de productos seleccionados
        producto_en_venta = None
        for producto in self.productos_seleccionados:
            if producto['id'] == producto_id:
                producto_en_venta = producto
                break
        
        if not producto_en_venta:
            QMessageBox.warning(self, "Error", "No se encontró el producto en la venta.")
            return
        
        # Encontrar el producto original para verificar stock disponible
        producto_original = None
        for prod in self.productos_disponibles:
            if prod['id'] == producto_id:
                producto_original = prod
                break
        
        if not producto_original:
            QMessageBox.warning(self, "Error", "No se encontró información del producto original.")
            return
        
        # Calcular stock disponible real (stock original - lo que ya está en otras ventas)
        # Primero, calcular la cantidad total que ya tenemos en esta venta (excluyendo el producto actual)
        cantidad_en_otras_ventas = 0
        for prod in self.productos_seleccionados:
            if prod['id'] == producto_id and prod != producto_en_venta:
                cantidad_en_otras_ventas += prod['cantidad']
        
        # Stock disponible = stock original - lo que ya tenemos en otras ventas
        stock_disponible = producto_original['stockActual'] - cantidad_en_otras_ventas
        
        # Si el stock disponible es menor que 0, ajustar a 0
        if stock_disponible < 0:
            stock_disponible = 0
        
        # Si no hay stock disponible, mostrar mensaje
        if stock_disponible == 0:
            QMessageBox.warning(self, "Stock Insuficiente", 
                            f"No hay stock disponible para {producto_nombre}.\nStock total: {producto_original['stockActual']}\nYa en venta: {cantidad_en_otras_ventas}")
            return
        
        # Diálogo para modificar cantidad
        cantidad, ok = QInputDialog.getInt(
            self, 
            "Modificar Cantidad", 
            f"Nueva cantidad para {producto_nombre}:\n(Stock disponible: {stock_disponible})", 
            cantidad_actual,  # Valor actual
            1,               # Mínimo
            stock_disponible, # Máximo (basado en stock disponible)
            1                # Paso
        )
        
        if ok and cantidad != cantidad_actual:
            # Actualizar la cantidad y el total
            producto_en_venta['cantidad'] = cantidad
            producto_en_venta['total'] = producto_en_venta['precio_unitario'] * cantidad
            
            # Actualizar la interfaz
            self.actualizar_tabla_venta()
            self.calcular_total()
            
            QMessageBox.information(self, "Éxito", f"Cantidad actualizada a {cantidad} unidades.")

    def eliminar_producto(self):
        selected = self.productos_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione un producto para eliminar.")
            return
        
        row = selected[0].row()
        producto_id = int(self.productos_table.item(row, 0).text())
        producto_nombre = self.productos_table.item(row, 1).text()
        
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", 
                                          f"¿Está seguro de eliminar '{producto_nombre}' de la venta?",
                                          QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if confirmacion == QMessageBox.StandardButton.Yes:
            self.productos_seleccionados = [p for p in self.productos_seleccionados if p['id'] != producto_id]
            self.actualizar_tabla_venta()
            self.calcular_total()

    def actualizar_tabla_venta(self):
        self.productos_table.setRowCount(len(self.productos_seleccionados))
        for row, producto in enumerate(self.productos_seleccionados):
            self.productos_table.setItem(row, 0, QTableWidgetItem(str(producto['id'])))
            self.productos_table.setItem(row, 1, QTableWidgetItem(producto['nombre']))
            self.productos_table.setItem(row, 2, QTableWidgetItem(str(producto['cantidad'])))
            self.productos_table.setItem(row, 3, QTableWidgetItem(f"Q{producto['precio_unitario']:.2f}"))
            self.productos_table.setItem(row, 4, QTableWidgetItem(f"Q{producto['total']:.2f}"))

    def calcular_total(self):
        total = sum(p['total'] for p in self.productos_seleccionados)
        self.total_label.setText(f"Total: Q{total:.2f}")

    def validar_y_aceptar(self):
        if not self.productos_seleccionados:
            QMessageBox.warning(self, "Venta Vacía", "Debe agregar al menos un producto a la venta.")
            return
        
        # Validar stock suficiente para todos los productos
        for producto in self.productos_seleccionados:
            producto_original = next((p for p in self.productos_disponibles if p['id'] == producto['id']), None)
            if producto_original and producto['cantidad'] > producto_original['stockActual']:
                QMessageBox.warning(self, "Stock Insuficiente", 
                                  f"Stock insuficiente para {producto['nombre']}. Stock disponible: {producto_original['stockActual']}")
                return
        
        self.accept()

    def get_venta_data(self):
        return {
            'cliente_id': self.cliente_combo.currentData(),
            'productos': self.productos_seleccionados,
            'total': sum(p['total'] for p in self.productos_seleccionados)
        }

# Clase auxiliar para el diálogo de entrada (añadir al inicio del archivo)
from PyQt6.QtWidgets import QInputDialog

class VentasWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Ventas")
        self.setMinimumSize(1200, 800)
        
        # Paleta de colores profesional
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
        
        # Construcción de la UI modular
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
        
        # Filtros de búsqueda
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
        
        # Botones de acción
        action_layout = QHBoxLayout()
        self.nueva_venta_btn = QPushButton("➕ Registrar Nueva Venta")
        self.nueva_venta_btn.setStyleSheet(self.style_primary_button)
        self.ver_detalles_btn = QPushButton("📋 Ver Detalles de Venta")
        self.ver_detalles_btn.setStyleSheet(self.style_header_button)
        action_layout.addWidget(self.nueva_venta_btn)
        action_layout.addWidget(self.ver_detalles_btn)
        action_layout.addStretch()
        control_layout.addLayout(action_layout)
        
        self.main_layout.addWidget(control_frame)
        
        # Conexiones
        self.buscar_btn.clicked.connect(self.buscar_ventas)
        self.nueva_venta_btn.clicked.connect(self.nueva_venta)
        self.ver_detalles_btn.clicked.connect(self.ver_detalles_venta)

    def setup_table(self):
        self.ventas_table = QTableWidget()
        self.ventas_table.setColumnCount(6)
        self.ventas_table.setHorizontalHeaderLabels(["ID Venta", "Fecha", "Cliente", "Total", "Vendedor", "Estado"])
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
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            query = """
            SELECT v.id, v.fechaVenta as fecha, v.total,
                   COALESCE(CONCAT(c.nombre, ' ', c.apellido), 'Consumidor Final') as cliente_nombre,
                   COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sistema') as vendedor,
                   'Completada' as estado
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
            
            query += " ORDER BY v.fechaVenta DESC, v.id DESC"
            
            cursor.execute(query, params)
            ventas = cursor.fetchall()
            
            self.ventas_table.setRowCount(len(ventas))
            for row, venta in enumerate(ventas):
                self.ventas_table.setItem(row, 0, QTableWidgetItem(str(venta['id'])))
                self.ventas_table.setItem(row, 1, QTableWidgetItem(venta['fecha'].strftime('%Y-%m-%d %H:%M')))
                self.ventas_table.setItem(row, 2, QTableWidgetItem(venta['cliente_nombre']))
                self.ventas_table.setItem(row, 3, QTableWidgetItem(f"Q{float(venta['total']):.2f}"))
                self.ventas_table.setItem(row, 4, QTableWidgetItem(venta['vendedor']))
                self.ventas_table.setItem(row, 5, QTableWidgetItem(venta['estado']))
            
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
            conexion = ConexionBD.obtener_conexion()
            
            # Obtener clientes activos
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, apellido FROM cliente WHERE activo = 1")
            clientes = cursor.fetchall()
            
            # Obtener productos con stock
            cursor.execute("""
                SELECT id, codigo, nombre, precioVenta, stockActual 
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
                
                cursor = conexion.cursor()
                
                # Insertar venta principal
                venta_query = """
                INSERT INTO ventas (cliente_id, fechaVenta, total, usuario_id)
                VALUES (%s, NOW(), %s, 11)
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
                    
                    cursor.execute(detalle_query, (
                        venta_id,
                        producto['id'],
                        producto['cantidad'],
                        producto['precio_unitario'],
                        producto['total']
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

    def ver_detalles_venta(self):
        selected = self.ventas_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Advertencia", "Seleccione una venta para ver sus detalles.")
            return
        
        venta_id = self.ventas_table.item(selected[0].row(), 0).text()
        fecha = self.ventas_table.item(selected[0].row(), 1).text()
        cliente = self.ventas_table.item(selected[0].row(), 2).text()
        total_venta = self.ventas_table.item(selected[0].row(), 3).text()
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # Obtener detalles de la venta
            cursor.execute("""
                SELECT p.nombre, p.codigo, dv.cantidad, dv.precio_unitario, dv.subtotal
                FROM detalle_venta dv
                JOIN producto p ON dv.producto_id = p.id
                WHERE dv.ventas_id = %s
                ORDER BY p.nombre
            """, (venta_id,))
            
            detalles = cursor.fetchall()
            
            cursor.close()
            conexion.close()
            
            if not detalles:
                QMessageBox.information(self, "Detalles", "No se encontraron detalles para esta venta.")
                return
            
            # Crear diálogo personalizado para mostrar detalles
            dialog = QDialog(self)
            dialog.setWindowTitle(f"Detalles de Venta #{venta_id}")
            dialog.resize(700, 500)
            
            layout = QVBoxLayout()
            
            # Información general
            info_frame = QFrame()
            info_frame.setStyleSheet("background-color: white; color: #000000;  /* Letra negra */; border-radius: 5px; padding: 10px;")
            info_layout = QVBoxLayout(info_frame)
            
            info_layout.addWidget(QLabel(f"<b>Venta #:</b> {venta_id}"))
            info_layout.addWidget(QLabel(f"<b>Fecha:</b> {fecha}"))
            info_layout.addWidget(QLabel(f"<b>Cliente:</b> {cliente}"))
            info_layout.addWidget(QLabel(f"<b>Total:</b> {total_venta}"))
            
            layout.addWidget(info_frame)
            
            # Tabla de productos
            layout.addWidget(QLabel("<b>Productos:</b>"))
            tabla = QTableWidget()
            tabla.setColumnCount(5)
            tabla.setHorizontalHeaderLabels(["Código", "Producto", "Cantidad", "P. Unitario", "Subtotal"])
            tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            tabla.setRowCount(len(detalles))
            
            for row, detalle in enumerate(detalles):
                tabla.setItem(row, 0, QTableWidgetItem(detalle.get('codigo', 'N/A')))
                tabla.setItem(row, 1, QTableWidgetItem(detalle['nombre']))
                tabla.setItem(row, 2, QTableWidgetItem(str(detalle['cantidad'])))
                tabla.setItem(row, 3, QTableWidgetItem(f"Q{float(detalle['precio_unitario']):.2f}"))
                tabla.setItem(row, 4, QTableWidgetItem(f"Q{float(detalle['subtotal']):.2f}"))
            
            tabla.setStyleSheet(self.style_table)
            layout.addWidget(tabla)
            
            # Botón cerrar
            close_btn = QPushButton("Cerrar")
            close_btn.setStyleSheet(self.style_header_button)
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)
            
            dialog.setLayout(layout)
            dialog.exec()
            
        except mysql.connector.Error as error:
            QMessageBox.critical(self, "Error", f"Error al cargar detalles:\n{error}")

    def go_back_to_main(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = VentasWindow()
    window.show()
    sys.exit(app.exec())
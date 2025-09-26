import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
                             QDialog, QDateEdit, QMessageBox, QHeaderView, QComboBox, QFrame,
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QPalette, QColor, QIcon
from datetime import datetime, timedelta
from .noti2 import enviar_correo

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conexion import ConexionBD

# --- La clase ProductDialog permanece igual ---
class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None, proveedores=None):
        super().__init__(parent)
        self.setWindowTitle("Registrar / Editar Producto")
        self.resize(400, 400)
        
        self.layout = QVBoxLayout()
        self.proveedores = proveedores or []
    
        # --- Campos del formulario ---
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
        self.proveedor_label = QLabel("Proveedor:")
        self.proveedor_combo = QComboBox()
        if self.proveedores:
            for proveedor in self.proveedores:
                self.proveedor_combo.addItem(f"{proveedor['nombre']} {proveedor['apellido']}", proveedor['id'])
        self.vencimiento_label = QLabel("Vencimiento:")
        self.vencimiento_input = QDateEdit()
        self.vencimiento_input.setCalendarPopup(True)
        self.vencimiento_input.setDate(QDate.currentDate())
        self.product_id = None
        self.button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("Cancelar")
        self.cancel_button.setStyleSheet("background-color: #ff6961; border-radius: 5px; padding: 5px;")
        self.cancel_button.clicked.connect(self.reject)
        self.ok_button = QPushButton("OK")
        self.ok_button.setStyleSheet("background-color: #77dd77; border-radius: 5px; padding: 5px;")
        self.ok_button.clicked.connect(self.accept)
        self.button_layout.addWidget(self.cancel_button)
        self.button_layout.addWidget(self.ok_button)
        # --- Llenar Layout ---
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
        proveedor_id = product_data.get('proveedor_id')
        if proveedor_id is not None:
            index = self.proveedor_combo.findData(proveedor_id)
            if index >= 0:
                self.proveedor_combo.setCurrentIndex(index)
        if 'fVencimiento' in product_data and product_data['fVencimiento']:
            try:
                date_obj = product_data['fVencimiento']
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
                self.vencimiento_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, AttributeError):
                self.vencimiento_input.setDate(QDate.currentDate())

    def get_product_data(self):
        proveedor_id = self.proveedor_combo.currentData()
        return {
            'id': self.product_id,
            'codigo': self.codigo_input.text(), 'nombre': self.nombre_input.text(),
            'categoria': self.categoria_input.text(),
            'stockActual': int(self.stock_actual_input.text() or 0),
            'stockMinimo': int(self.stock_minimo_input.text() or 0),
            'precioVenta': float(self.precio_venta_input.text() or 0),
            'precioCompra': float(self.precio_compra_input.text() or 0),
            'proveedor_id': proveedor_id,
            'fVencimiento': self.vencimiento_input.date().toString("yyyy-MM-dd"),
            'fRegistro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


class NotificationCard(QFrame):
    dismissed = pyqtSignal()
    send_email_requested = pyqtSignal(dict)

    def __init__(self, icon, title, description, alert_data, color="#5DADE2"):
        super().__init__()
        self.alert_data = alert_data
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("NotificationCard")
        self.setStyleSheet(f"background-color: {color}; border-radius: 10px; border: 1px solid #FFFFFF;")
        
        main_layout = QHBoxLayout(self)
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px; color: white; background-color: transparent;")
        main_layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 14px; font-weight: bold; color: white; background-color: transparent;")
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 12px; color: white; background-color: transparent;")
        desc_label.setWordWrap(True)
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        main_layout.addLayout(text_layout, 1)

        button_layout = QVBoxLayout()
        self.email_button = QPushButton("📧 Enviar")
        self.email_button.setStyleSheet("background-color: #3498DB; color: white; padding: 5px; border-radius: 5px; border: none;")
        self.email_button.clicked.connect(lambda: self.send_email_requested.emit(self.alert_data))
        self.dismiss_button = QPushButton("Entendido")
        self.dismiss_button.setStyleSheet("background-color: #2ECC71; color: white; padding: 5px; border-radius: 5px; border: none;")
        self.dismiss_button.clicked.connect(self.dismissed.emit)
        button_layout.addWidget(self.email_button)
        button_layout.addWidget(self.dismiss_button)
        main_layout.addLayout(button_layout)


class InventarioWindow(QMainWindow):
    def __init__(self, parent=None, show_notifications_on_start=False):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Inventario")
        self.setMinimumSize(1200, 800)
        
        self.colores = {
            "fondo": "#F8F9FA", "cabecera": "#0B6E4F",
            "texto_principal": "#212529", "texto_secundario": "#6C757D",
            "acento": "#3A9D5A", "borde": "#DEE2E6", "peligro": "#E53E3E",
            "panel_notificaciones": "#2D3748" # Color oscuro consistente
        }
        
        self._create_stylesheets()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colores["fondo"]))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.overall_layout = QHBoxLayout(central_widget)
        self.overall_layout.setContentsMargins(0,0,0,0)
        self.overall_layout.setSpacing(0)

        main_content_widget = QWidget()
        self.main_layout = QVBoxLayout(main_content_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(15)

        self.setup_header_bar()
        self.setup_control_panel()
        self.setup_table()

        self.setup_notification_panel()
        self.overall_layout.addWidget(main_content_widget, 1)
        self.overall_layout.addWidget(self.notification_panel)
        
        self.productos = []
        self.proveedores = []
        self.notification_count = 0
        self.cargar_proveedores()
        self.cargar_productos()
        self.verificar_y_cargar_alertas()
        if show_notifications_on_start:
            self.toggle_notification_panel()

    def _create_stylesheets(self):
        """Método central para definir todos los estilos de la ventana."""
        self.style_header_label = f"font-size: 22px; font-weight: bold; color: white; background: transparent;"
        self.style_header_button = f"""
            QPushButton {{ background-color: #FFFFFF; color: {self.colores['texto_principal']};
                border: none; border-radius: 5px; padding: 8px 12px; font-weight: bold;
            }} QPushButton:hover {{ background-color: #E2E8F0; }}
        """
        self.style_notification_button = f"""
            QPushButton {{ background-color: #ED8936; color: white; border: none;
                border-radius: 15px; padding: 8px 12px; font-weight: bold; font-size: 14px;
            }} QPushButton:hover {{ background-color: #DD781D; }}
        """
        self.style_input_field = f"""
            QLineEdit, QComboBox {{ border: 1px solid {self.colores['borde']}; border-radius: 5px;
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

    def setup_header_bar(self):
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {self.colores['cabecera']};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)

        back_button = QPushButton("Regresar")
        back_button.setStyleSheet(self.style_header_button)
        back_button.clicked.connect(self.back)
        
        title_label = QLabel("Gestión de Inventario")
        title_label.setStyleSheet(self.style_header_label)

        self.notification_button = QPushButton("🔔 (0)")
        self.notification_button.setStyleSheet(self.style_notification_button)
        self.notification_button.clicked.connect(self.toggle_notification_panel)
        
        header_layout.addWidget(back_button)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.notification_button)
        self.main_layout.addWidget(header_frame)

    def setup_control_panel(self):
        control_frame = QFrame()
        control_frame.setObjectName("ControlFrame")
        control_frame.setStyleSheet(f"#ControlFrame {{ margin: 0 10px; }}")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)

        search_layout = QHBoxLayout()
        self.nombre_input = QLineEdit(); self.nombre_input.setPlaceholderText("Nombre de Producto")
        self.codigo_input = QLineEdit(); self.codigo_input.setPlaceholderText("Código")
        self.proveedor_combo = QComboBox()
        self.buscar_button = QPushButton("Buscar")
        self.buscar_button.setStyleSheet(self.style_header_button)
        self.listar_button = QPushButton("Mostrar Todo")
        self.listar_button.setStyleSheet(self.style_header_button)
        
        self.nombre_input.setStyleSheet(self.style_input_field)
        self.codigo_input.setStyleSheet(self.style_input_field)
        self.proveedor_combo.setStyleSheet(self.style_input_field)
        
        search_layout.addWidget(self.nombre_input, 2)
        search_layout.addWidget(self.codigo_input, 1)
        search_layout.addWidget(self.proveedor_combo, 1)
        search_layout.addWidget(self.buscar_button)
        search_layout.addWidget(self.listar_button)
        control_layout.addLayout(search_layout)

        action_layout = QHBoxLayout()
        self.registrar_button = QPushButton("➕ Registrar Producto")
        self.editar_button = QPushButton("✏️ Editar Seleccionado")
        self.eliminar_button = QPushButton("❌ Eliminar Seleccionado")
        self.limpiar_button = QPushButton("🗑️ Limpiar Tabla")

        self.registrar_button.setStyleSheet(self.style_primary_button)
        self.editar_button.setStyleSheet(self.style_header_button)
        self.eliminar_button.setStyleSheet(self.style_danger_button)
        self.limpiar_button.setStyleSheet(self.style_header_button) # Neutral style for a less destructive look

        self.registrar_button.clicked.connect(self.registrar_producto)
        self.editar_button.clicked.connect(self.editar_producto)
        self.eliminar_button.clicked.connect(self.eliminar_producto)
        self.limpiar_button.clicked.connect(self.limpiar_tabla)
        self.buscar_button.clicked.connect(self.buscar_productos)
        self.listar_button.clicked.connect(self.listar_todos)
        
        action_layout.addWidget(self.registrar_button)
        action_layout.addWidget(self.editar_button)
        action_layout.addStretch()
        action_layout.addWidget(self.limpiar_button)
        action_layout.addWidget(self.eliminar_button)
        control_layout.addLayout(action_layout)
        
        self.main_layout.addWidget(control_frame)

    def setup_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels(["ID", "Código", "Nombre", "Categoría", "Stock", "Mínimo", "P. Venta", "P. Compra", "Proveedor", "Vencimiento"])
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setStyleSheet(self.style_table)
        self.main_layout.addWidget(self.table)
        
    def setup_notification_panel(self):
        self.notification_panel = QFrame()
        self.notification_panel.setFixedWidth(0)
        self.notification_panel.setStyleSheet(f"background-color: {self.colores['panel_notificaciones']}; border-left: 2px solid {self.colores['cabecera']};")
        panel_layout = QVBoxLayout(self.notification_panel)
        title_label = QLabel("Notificaciones")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold; background: transparent;")
        panel_layout.addWidget(title_label)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; } QWidget { background: transparent; }")
        scroll_content = QWidget()
        self.notification_list_layout = QVBoxLayout(scroll_content)
        self.notification_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

    def toggle_notification_panel(self):
        current_width = self.notification_panel.width()
        target_width = 350 if current_width == 0 else 0
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setTargetObject(self.notification_panel)
        self.animation.setDuration(400)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

    def verificar_y_cargar_alertas(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            # Alertas de stock bajo
            q_stock = "SELECT nombre, stockActual, stockMinimo FROM producto WHERE stockActual <= stockMinimo AND stockActual > 0"
            cursor.execute(q_stock)
            alertas_stock = cursor.fetchall()
            
            # Alertas de vencimiento
            dias_vencer = 30
            fecha_limite = (datetime.now() + timedelta(days=dias_vencer)).strftime('%Y-%m-%d')
            q_vencimiento = "SELECT nombre, fVencimiento FROM producto WHERE fVencimiento BETWEEN CURDATE() AND %s"
            cursor.execute(q_vencimiento, (fecha_limite,))
            alertas_vencimiento = cursor.fetchall()
            
            cursor.close()

            # Limpiar notificaciones anteriores
            while self.notification_list_layout.count():
                child = self.notification_list_layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
            
            self.notification_count = 0

            # Crear tarjetas para stock bajo
            for alerta in alertas_stock:
                self.notification_count += 1
                desc = f"Quedan {alerta['stockActual']} unidades (Mínimo: {alerta['stockMinimo']})"
                card = NotificationCard("📦", alerta['nombre'], desc, alerta, color="#E67E22")
                card.dismissed.connect(self.handle_dismissal)
                card.send_email_requested.connect(self.handle_email_request_stock)
                self.notification_list_layout.addWidget(card)
            
            # Crear tarjetas para vencimiento
            for alerta in alertas_vencimiento:
                self.notification_count += 1
                fecha_vence = alerta['fVencimiento'].strftime('%d/%m/%Y')
                desc = f"Vence el {fecha_vence}"
                card = NotificationCard("⏳", alerta['nombre'], desc, alerta, color="#E74C3C")
                card.dismissed.connect(self.handle_dismissal)
                card.send_email_requested.connect(self.handle_email_request_vencimiento)
                self.notification_list_layout.addWidget(card)
            
            # Actualizar contador de la campana
            self.notification_button.setText(f"🔔 ({self.notification_count})")
            
        except Exception as e:
            QMessageBox.critical(self, "Error de Alertas", f"No se pudieron verificar las alertas: {e}")

    def handle_dismissal(self):
        """Oculta la tarjeta y actualiza el contador."""
        card = self.sender()
        if card:
            card.hide()
            self.notification_count -= 1
            self.notification_button.setText(f"🔔 ({self.notification_count})")

    def handle_email_request_stock(self, alert_data):
        asunto = f"🚨 Alerta de Stock Bajo: {alert_data['nombre']}"
        cuerpo = f"""
        <h1>Alerta de Inventario</h1>
        <p>El producto <strong>{alert_data['nombre']}</strong> ha alcanzado un nivel de stock bajo.</p>
        <ul>
            <li>Stock Actual: <strong>{alert_data['stockActual']}</strong></li>
            <li>Stock Mínimo: {alert_data['stockMinimo']}</li>
        </ul>
        <p>Por favor, considere realizar un nuevo pedido.</p>
        """
        self.send_email(asunto, cuerpo)
        
    def handle_email_request_vencimiento(self, alert_data):
        fecha_vence = alert_data['fVencimiento'].strftime('%d/%m/%Y')
        asunto = f"🚨 Alerta de Vencimiento: {alert_data['nombre']}"
        cuerpo = f"""
        <h1>Alerta de Inventario</h1>
        <p>El producto <strong>{alert_data['nombre']}</strong> está próximo a vencer.</p>
        <ul>
            <li>Fecha de Vencimiento: <strong>{fecha_vence}</strong></li>
        </ul>
        <p>Por favor, tome las acciones necesarias (promoción, rotación, etc.).</p>
        """
        self.send_email(asunto, cuerpo)

    def send_email(self, asunto, cuerpo_html):
        exito, mensaje = enviar_correo(asunto, cuerpo_html)
        if exito:
            QMessageBox.information(self, "Correo Enviado", mensaje)
        else:
            QMessageBox.critical(self, "Error de Envío", mensaje)

            
    def cargar_proveedores(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            cursor.execute("SELECT id, nombre, apellido FROM proveedor")
            self.proveedores = cursor.fetchall()
            
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
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
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
        
        self.table.setRowCount(0)
        
        for row_index, producto in enumerate(productos_mostrados):
            self.table.insertRow(row_index)
            
            id_item = QTableWidgetItem(str(producto['id']))
            self.table.setItem(row_index, 0, id_item)
            
            self.table.setItem(row_index, 1, QTableWidgetItem(producto['codigo']))
            self.table.setItem(row_index, 2, QTableWidgetItem(producto['nombre']))
            self.table.setItem(row_index, 3, QTableWidgetItem(producto['categoria']))
            self.table.setItem(row_index, 4, QTableWidgetItem(str(producto['stockActual'])))
            self.table.setItem(row_index, 5, QTableWidgetItem(str(producto['stockMinimo'])))
            self.table.setItem(row_index, 6, QTableWidgetItem(str(producto['precioVenta'])))
            self.table.setItem(row_index, 7, QTableWidgetItem(str(producto['precioCompra'])))
            
            proveedor_nombre = producto.get('proveedor_nombre', 'Sin proveedor')
            self.table.setItem(row_index, 8, QTableWidgetItem(proveedor_nombre))
            
            fecha_vencimiento = producto.get('fVencimiento', '')
            if fecha_vencimiento:
                if isinstance(fecha_vencimiento, datetime):
                    fecha_str = fecha_vencimiento.strftime('%Y-%m-%d')
                else:
                    fecha_str = str(fecha_vencimiento)
                self.table.setItem(row_index, 9, QTableWidgetItem(fecha_str))
            else:
                self.table.setItem(row_index, 9, QTableWidgetItem(""))
        
        self.table.setColumnHidden(0, True)

    def registrar_producto(self):
        dialog = ProductDialog(self, proveedores=self.proveedores)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            nuevo_producto = dialog.get_product_data()
            
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                query = """
                INSERT INTO producto (codigo, nombre, categoria, stockActual, stockMinimo,
                                      precioVenta, precioCompra, proveedor_id, fVencimiento, fRegistro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    nuevo_producto['codigo'], nuevo_producto['nombre'], nuevo_producto['categoria'],
                    nuevo_producto['stockActual'], nuevo_producto['stockMinimo'], nuevo_producto['precioVenta'],
                    nuevo_producto['precioCompra'], nuevo_producto['proveedor_id'], nuevo_producto['fVencimiento'],
                    nuevo_producto['fRegistro']
                )
                
                cursor.execute(query, valores)
                conexion.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto registrado correctamente")
                self.cargar_productos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al registrar producto: {str(e)}")

    def editar_producto(self):
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un producto para editar")
            return
        
        selected_row = selected_rows[0].row()
        producto_id = int(self.table.item(selected_row, 0).text())
        producto_seleccionado = next((p for p in self.productos if p['id'] == producto_id), None)
        
        if not producto_seleccionado:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el producto seleccionado")
            return
        
        dialog = ProductDialog(self, producto_seleccionado, self.proveedores)
        result = dialog.exec()
        
        if result == QDialog.DialogCode.Accepted:
            producto_editado = dialog.get_product_data()
            
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                query = """
                UPDATE producto
                SET codigo = %s, nombre = %s, categoria = %s, stockActual = %s, stockMinimo = %s,
                    precioVenta = %s, precioCompra = %s, proveedor_id = %s, fVencimiento = %s
                WHERE id = %s
                """
                valores = (
                    producto_editado['codigo'], producto_editado['nombre'], producto_editado['categoria'],
                    producto_editado['stockActual'], producto_editado['stockMinimo'], producto_editado['precioVenta'],
                    producto_editado['precioCompra'], producto_editado['proveedor_id'], producto_editado['fVencimiento'],
                    producto_id
                )
                
                cursor.execute(query, valores)
                conexion.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
                self.cargar_productos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al actualizar producto: {str(e)}")
    
    def eliminar_producto(self):
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Por favor seleccione un producto para eliminar")
            return
        
        selected_row = selected_rows[0].row()
        producto_id = int(self.table.item(selected_row, 0).text())
        nombre_producto = self.table.item(selected_row, 2).text()
        
        confirmation = QMessageBox.question(
            self, "Confirmar eliminación", 
            f"¿Está seguro que desea eliminar el producto '{nombre_producto}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                query = "DELETE FROM producto WHERE id = %s"
                cursor.execute(query, (producto_id,))
                conexion.commit()
                cursor.close()
                
                QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                self.cargar_productos()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar producto: {str(e)}")
    
    def limpiar_tabla(self):
        if self.table.rowCount() == 0:
            QMessageBox.information(self, "Información", "La tabla ya está vacía")
            return
        
        self.table.setRowCount(0)
        QMessageBox.information(self, "Éxito", "Tabla limpiada correctamente")
    
    def buscar_productos(self):
        nombre = self.nombre_input.text().strip()
        codigo = self.codigo_input.text().strip()
        categoria = self.categoria_input.text().strip()
        proveedor_id = self.proveedor_combo.currentData()
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            
            query = """
            SELECT p.*, CONCAT(prov.nombre, ' ', prov.apellido) as proveedor_nombre
            FROM producto p
            LEFT JOIN proveedor prov ON p.proveedor_id = prov.id
            WHERE 1=1
            """
            
            parametros = []
            
            if nombre:
                query += " AND p.nombre LIKE %s"
                parametros.append(f"%{nombre}%")
            if codigo:
                query += " AND p.codigo LIKE %s"
                parametros.append(f"%{codigo}%")
            if categoria:
                query += " AND p.categoria LIKE %s"
                parametros.append(f"%{categoria}%")
            if proveedor_id != -1:
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
        self.nombre_input.clear()
        self.codigo_input.clear()
        self.categoria_input.clear()
        self.proveedor_combo.setCurrentIndex(0)
        self.cargar_productos()
    
    def back(self):
        """Vuelve a mostrar la ventana principal que estaba oculta."""
        if self.parent_window:
            self.parent_window.show()
        self.close() 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventarioWindow()
    window.show()
    sys.exit(app.exec())
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QLineEdit, 
                             QVBoxLayout, QHBoxLayout, QWidget, QTableWidget, QTableWidgetItem, 
                             QDialog, QDateEdit, QMessageBox, QHeaderView, QComboBox, QFrame,
                             QScrollArea, QSizePolicy)
from PyQt6.QtCore import Qt, QDate, QPropertyAnimation, QEasingCurve, pyqtSignal, QRegularExpression
from PyQt6.QtGui import QPalette, QColor, QIcon, QIntValidator, QDoubleValidator, QRegularExpressionValidator, QFont
from datetime import datetime, timedelta
from .categorias_dialog import CategoriasDialog
from .noti2 import enviar_correo

import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conexion import ConexionBD
from reportes_inventario_final import ReportesInventarioWindow

# --- La clase ProductDialog permanece igual ---
class ProductDialog(QDialog):
    def __init__(self, parent=None, product_data=None, proveedores=None, categorias=None): # Añadido categorias
        super().__init__(parent)
        self.setWindowTitle("Registrar / Editar Producto")
        self.setMinimumSize(400, 500) # Un poco más alto para el nuevo campo
        
        self.layout = QVBoxLayout()
        self.proveedores = proveedores or []
        self.categorias = categorias or [] # Guardar lista de categorías

        # --- Campos del formulario ---
        self.codigo_label = QLabel("Código:")
        self.codigo_input = QLineEdit()
        self.nombre_label = QLabel("Nombre:")
        self.nombre_input = QLineEdit()
        name_regex = QRegularExpression(r"^[^\d]+$") # Regex: Start (^) + one or more non-digits ([^\d]+) + End ($)
        name_validator = QRegularExpressionValidator(name_regex, self)
        self.nombre_input.setValidator(name_validator)
        
        # Reemplazar QLineEdit por QComboBox para Categoría
        self.categoria_label = QLabel("Categoría:")
        self.categoria_combo = QComboBox()
        if self.categorias:
            for cat in self.categorias:
                self.categoria_combo.addItem(cat['nombre_categoria'], cat['id']) # Texto y ID
                
        self.stock_actual_label = QLabel("Stock Actual(Unidades Totales):")
        self.stock_actual_input = QLineEdit() # Añadir validación numérica luego
        int_validator_positive = QIntValidator(0, 999999, self) # Min 0, Max large number
        self.stock_actual_input.setValidator(int_validator_positive)
        self.layout.addSpacing(10) 
        
        cajas_layout = QHBoxLayout() # Layout for boxes and units fields
        
        self.cantidad_cajas_label = QLabel("Cantidad Cajas:")
        self.cantidad_cajas_input = QLineEdit()
        self.cantidad_cajas_input.setPlaceholderText("Ej: 5")
        self.cantidad_cajas_input.setValidator(int_validator_positive) # Reuse validator
        cajas_layout.addWidget(self.cantidad_cajas_label)
        cajas_layout.addWidget(self.cantidad_cajas_input)

        self.unidades_por_caja_label = QLabel("Unidades / Caja:")
        self.unidades_por_caja_input = QLineEdit()
        self.unidades_por_caja_input.setPlaceholderText("Ej: 100")
        self.unidades_por_caja_input.setValidator(int_validator_positive) # Reuse validator
        cajas_layout.addWidget(self.unidades_por_caja_label)
        cajas_layout.addWidget(self.unidades_por_caja_input)

        self.calcular_stock_btn = QPushButton("Calcular Unidades")
        self.calcular_stock_btn.setStyleSheet("background-color: #3498DB; color: white; padding: 5px; border-radius: 5px;")
        self.calcular_stock_btn.clicked.connect(self.calcular_stock_desde_cajas)    

        self.stock_minimo_label = QLabel("Stock Mínimo(Unidades Totales):")
        self.stock_minimo_input = QLineEdit() # Añadir validación numérica luego
        self.stock_minimo_input.setValidator(int_validator_positive)

        double_validator_positive = QDoubleValidator(0.0, 999999.99, 2, self)

        self.precio_venta_label = QLabel("Precio Venta(Unidades):")
        self.precio_venta_input = QLineEdit() # Añadir validación numérica luego
        self.precio_venta_input.setValidator(double_validator_positive)
        self.precio_compra_label = QLabel("Precio Compra(Unidades):")
        self.precio_compra_input = QLineEdit() # Añadir validación numérica luego
        self.precio_compra_input.setValidator(double_validator_positive)
        self.proveedor_label = QLabel("Proveedor:")
        self.proveedor_combo = QComboBox()
        if self.proveedores:
            for prov in self.proveedores:
                self.proveedor_combo.addItem(f"{prov['nombre']} ({prov['marca']})", prov['id'])
        self.vencimiento_label = QLabel("Fecha deVencimiento:")
        self.vencimiento_input = QDateEdit()
        self.vencimiento_input.setCalendarPopup(True)
        self.vencimiento_input.setDate(QDate.currentDate())
        
        self.product_id = None
        
        # Botones (sin cambios)
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
        self.layout.addWidget(self.categoria_combo) # Añadir el QComboBox
        self.layout.addWidget(self.stock_actual_label)
        self.layout.addWidget(self.stock_actual_input)

        self.layout.addLayout(cajas_layout) 
        self.layout.addWidget(self.calcular_stock_btn)
        self.layout.addSpacing(10)


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

    def calcular_stock_desde_cajas(self):
        """Calculates total units from boxes and units/box, updates Stock Actual field."""
        try:
            cajas_str = self.cantidad_cajas_input.text().strip()
            unidades_str = self.unidades_por_caja_input.text().strip()

            # Check if fields are empty
            if not cajas_str or not unidades_str:
                QMessageBox.warning(self, "Campos Vacíos", "Ingrese la cantidad de cajas y las unidades por caja.")
                return

            cantidad_cajas = int(cajas_str)
            unidades_por_caja = int(unidades_str)
            
            total_unidades = cantidad_cajas * unidades_por_caja
            
            # Update the Stock Actual field
            self.stock_actual_input.setText(str(total_unidades))
            
            # Optional: Clear the calculation fields after successful calculation
            self.cantidad_cajas_input.clear()
            self.unidades_por_caja_input.clear()

        except ValueError:
            QMessageBox.warning(self, "Error de Formato", "Asegúrese de que 'Cantidad Cajas' y 'Unidades / Caja' sean números enteros válidos.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Ocurrió un error al calcular: {e}")


    def accept(self):
        """Overrides the default accept behavior to add validation."""
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Campo Vacío", "El nombre del producto es obligatorio.")
            self.nombre_input.setFocus() # Focus the problematic field
            return # Stop the accept process
        if not self.nombre_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El nombre del producto no puede contener números.")
             self.nombre_input.setFocus()
             return
             
        if not self.stock_actual_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El Stock Actual debe ser un número entero positivo.")
             self.stock_actual_input.setFocus()
             return
             
        if not self.stock_minimo_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El Stock Mínimo debe ser un número entero positivo.")
             self.stock_minimo_input.setFocus()
             return

        if not self.precio_venta_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El Precio de Venta debe ser un número decimal positivo (ej: 12.50).")
             self.precio_venta_input.setFocus()
             return
             
        if not self.precio_compra_input.hasAcceptableInput():
             QMessageBox.warning(self, "Formato Incorrecto", "El Precio de Compra debe ser un número decimal positivo (ej: 10.00).")
             self.precio_compra_input.setFocus()
             return
        super().accept()



    def populate_form(self, product_data):
        self.product_id = product_data.get('id')
        self.codigo_input.setText(product_data.get('codigo', ''))
        self.nombre_input.setText(product_data.get('nombre', ''))
        
        # Seleccionar la categoría correcta en el ComboBox
        categoria_id = product_data.get('categoria_id')
        if categoria_id is not None:
            index = self.categoria_combo.findData(categoria_id)
            if index >= 0:
                self.categoria_combo.setCurrentIndex(index)
                
        self.stock_actual_input.setText(str(product_data.get('stockActual', '')))
        self.stock_minimo_input.setText(str(product_data.get('stockMinimo', '')))
        self.precio_venta_input.setText(str(product_data.get('precioVenta', '')))
        self.precio_compra_input.setText(str(product_data.get('precioCompra', '')))
        
        proveedor_id = product_data.get('proveedor_id')
        if proveedor_id is not None:
            index_prov = self.proveedor_combo.findData(proveedor_id)
            if index_prov >= 0:
                self.proveedor_combo.setCurrentIndex(index_prov)
        if 'fVencimiento' in product_data and product_data['fVencimiento']:
            try:
                date_obj = product_data['fVencimiento']
                if isinstance(date_obj, str):
                    date_obj = datetime.strptime(date_obj, '%Y-%m-%d')
                self.vencimiento_input.setDate(QDate(date_obj.year, date_obj.month, date_obj.day))
            except (ValueError, AttributeError):
                self.vencimiento_input.setDate(QDate.currentDate())

    def get_product_data(self):
        # Obtener el ID de la categoría seleccionada
        categoria_id = self.categoria_combo.currentData()
        proveedor_id = self.proveedor_combo.currentData()
        
        # Validaciones básicas (puedes añadir más)
        try:
            stock_actual = int(self.stock_actual_input.text() or 0)
            stock_minimo = int(self.stock_minimo_input.text() or 0)
            precio_venta = float(self.precio_venta_input.text() or 0.0)
            precio_compra = float(self.precio_compra_input.text() or 0.0)
        except ValueError:
             QMessageBox.warning(self, "Error de Formato", "Stock y Precios deben ser números válidos.")
             return None # Indica que los datos no son válidos

        return {
            'id': self.product_id,
            'codigo': self.codigo_input.text(), 'nombre': self.nombre_input.text(),
            'categoria_id': categoria_id, # Usar el ID de la categoría
            'stockActual': stock_actual,
            'stockMinimo': stock_minimo,
            'precioVenta': precio_venta,
            'precioCompra': precio_compra,
            'proveedor_id': proveedor_id,
            'fVencimiento': self.vencimiento_input.date().toString("yyyy-MM-dd") or None,
            'fRegistro': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def actualizar_lista_categorias(self, nuevas_categorias):
        """Limpia y rellena el ComboBox de categorías con datos actualizados."""
        # Guardar el ID de la categoría seleccionada actualmente (si hay alguna)
        current_id = self.categoria_combo.currentData()

        # Limpiar el ComboBox
        self.categoria_combo.clear()

        # Actualizar la lista interna y rellenar el ComboBox
        self.categorias = nuevas_categorias or []
        if self.categorias:
            for cat in self.categorias:
                self.categoria_combo.addItem(cat['nombre_categoria'], cat['id'])

        # Intentar volver a seleccionar la categoría que estaba seleccionada
        index = self.categoria_combo.findData(current_id)
        if index >= 0:
            self.categoria_combo.setCurrentIndex(index)


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
    def __init__(self, parent=None, cargo=None, show_notifications_on_start=False):
        super().__init__(parent)
        self.parent_window = parent
        self.cargo = cargo
        self.setWindowTitle("Módulo de Inventario")
        self.setMinimumSize(1200, 800)
        self.current_product_dialog = None
        self.colores = {
            "fondo": "#F8F9FA", "cabecera": "#0B6E4F",
            "texto_principal": "#212529", "texto_secundario": "#6C757D",
            "acento": "#3A9D5A", "borde": "#DEE2E6", "peligro": "#E53E3E",
            "panel_notificaciones": "#2D3748" 
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
        self.todos_los_productos = [] 
        self.proveedores = []
        self.categorias = [] # Lista para guardar las categorías
        self.notification_count = 0
        
        # Cargar datos auxiliares primero
        self.cargar_categorias() 
        self.cargar_proveedores()
        
        # Cargar datos principales
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

    # Reemplaza esta función completa en modules/inventario.py

    def setup_control_panel(self):
        control_frame = QFrame()
        control_frame.setObjectName("ControlFrame")
        control_frame.setStyleSheet(f"#ControlFrame {{ margin: 0 10px; }}")
        control_layout = QVBoxLayout(control_frame)
        control_layout.setSpacing(15)

        # --- Search Layout ---
        search_layout = QHBoxLayout()
        self.nombre_input = QLineEdit(); self.nombre_input.setPlaceholderText("Nombre de Producto")
        self.codigo_input = QLineEdit(); self.codigo_input.setPlaceholderText("Código")
        self.categoria_filtro_combo = QComboBox() # Llenado en cargar_categorias
        self.proveedor_combo = QComboBox() # Llenado en cargar_proveedores
        self.buscar_button = QPushButton("Buscar")
        self.listar_button = QPushButton("Mostrar Todo")

        self.nombre_input.setStyleSheet(self.style_input_field)
        self.codigo_input.setStyleSheet(self.style_input_field)
        self.categoria_filtro_combo.setStyleSheet(self.style_input_field)
        self.proveedor_combo.setStyleSheet(self.style_input_field)
        self.buscar_button.setStyleSheet(self.style_header_button)
        self.listar_button.setStyleSheet(self.style_header_button)

        search_layout.addWidget(self.nombre_input, 2)
        search_layout.addWidget(self.codigo_input, 1)
        search_layout.addWidget(self.categoria_filtro_combo, 1)
        search_layout.addWidget(self.proveedor_combo, 1)
        search_layout.addWidget(self.buscar_button)
        search_layout.addWidget(self.listar_button)
        control_layout.addLayout(search_layout)

        # --- Action Layout ---
        action_layout = QHBoxLayout()
        # Define botones y asigna a self.
        self.registrar_button = QPushButton("➕ Registrar Producto")
        self.editar_button = QPushButton("✏️ Editar Seleccionado")
        self.eliminar_button = QPushButton("❌ Eliminar Seleccionado")
        self.limpiar_button = QPushButton("🗑️ Limpiar Tabla")
        self.btn_reportes = QPushButton("📊 Ver Reportes")
        self.gestionar_categorias_btn = QPushButton("📁 Gestionar Categorías")
        # Aplica estilos
        self.registrar_button.setStyleSheet(self.style_primary_button)
        self.editar_button.setStyleSheet(self.style_header_button)
        self.eliminar_button.setStyleSheet(self.style_danger_button)
        self.limpiar_button.setStyleSheet(self.style_header_button)
        self.gestionar_categorias_btn.setStyleSheet(self.style_header_button)
        self.btn_reportes.setStyleSheet(self.style_primary_button)

        # Añade botones al action_layout
        action_layout.addWidget(self.registrar_button)
        action_layout.addWidget(self.editar_button)
        action_layout.addWidget(self.gestionar_categorias_btn)
        action_layout.addWidget(self.btn_reportes)
        action_layout.addStretch()
        action_layout.addWidget(self.limpiar_button)
        action_layout.addWidget(self.eliminar_button)
        control_layout.addLayout(action_layout) # Añade action_layout al control_layout

        # Añade todo el control_frame al layout principal de la ventana
        self.main_layout.addWidget(control_frame)

      
        self.registrar_button.clicked.connect(self.registrar_producto)
        self.editar_button.clicked.connect(self.editar_producto)
        self.eliminar_button.clicked.connect(self.eliminar_producto)
        self.limpiar_button.clicked.connect(self.limpiar_tabla_visual)
        self.gestionar_categorias_btn.clicked.connect(self.abrir_gestion_categorias)
        self.btn_reportes.clicked.connect(self.abrir_reportes_inventario)
        
        # Conexiones de botones/campos de búsqueda
        self.buscar_button.clicked.connect(self.buscar_productos_db)
        self.listar_button.clicked.connect(self.listar_todos)
        self.nombre_input.textChanged.connect(self.filtrar_tabla_dinamico)
        self.codigo_input.textChanged.connect(self.filtrar_tabla_dinamico)
        self.categoria_filtro_combo.currentIndexChanged.connect(self.filtrar_tabla_dinamico)
        self.proveedor_combo.currentIndexChanged.connect(self.filtrar_tabla_dinamico)
        if self.cargo == 'Empleado':
            print("DEBUG: Aplicando restricciones para Empleado en Inventario.") # Mensaje de depuración
          
            self.eliminar_button.hide() 
            self.gestionar_categorias_btn.hide()

    def abrir_reportes_inventario(self):
        self.ventana_reportes = ReportesInventarioWindow(self)
        self.ventana_reportes.show()
        self.hide()

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

    def cargar_categorias(self):
        """Carga las categorías desde la BD y las añade al ComboBox de filtro."""
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            # Asumiendo que tienes una columna 'estado' o 'activo' en tu tabla categoria
            cursor.execute("SELECT id, nombre_categoria FROM categoria WHERE estado = 1 ORDER BY nombre_categoria") 
            self.categorias = cursor.fetchall()
            
            self.categoria_filtro_combo.clear()
            self.categoria_filtro_combo.addItem("Todas las Categorías", -1) # Opción por defecto
            for cat in self.categorias:
                self.categoria_filtro_combo.addItem(cat['nombre_categoria'], cat['id'])
        except Exception as e:
            self.mostrar_alerta("Error", f"Error al cargar categorías: {e}", tipo="critical")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def cargar_proveedores(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            # ### <<< CAMBIO: Se reemplaza 'apellido' por 'marca' >>> ###
            cursor.execute("SELECT id, nombre, marca FROM proveedor WHERE activo = 1 ORDER BY nombre")
            self.proveedores = cursor.fetchall()
            
            self.proveedor_combo.clear()
            self.proveedor_combo.addItem("Todos los Proveedores", -1)
            for prov in self.proveedores:
                # ### <<< CAMBIO: Se muestra el nombre y la marca >>> ###
                self.proveedor_combo.addItem(f"{prov['nombre']} ({prov['marca']})", prov['id'])
        except Exception as e:
            self.mostrar_alerta("Error", f"Error al cargar proveedores: {e}", tipo="critical")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

# Reemplaza también esta función en modules/inventario.py

    def cargar_productos(self):
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
           
            query = """
            SELECT 
                p.*, 
                CONCAT(prov.nombre, ' (', prov.marca, ')') as proveedor_nombre,
                cat.nombre_categoria as categoria_nombre 
            FROM producto p
            LEFT JOIN proveedor prov ON p.proveedor_id = prov.id
            LEFT JOIN categoria cat ON p.categoria_id = cat.id 
            """
            cursor.execute(query)
            self.todos_los_productos = cursor.fetchall()
            self.actualizar_tabla(self.todos_los_productos)
        except Exception as e:
            self.mostrar_alerta("Error", f"Error al cargar productos: {e}", tipo="critical")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def filtrar_tabla_dinamico(self):
        """Filtra la lista localmente incluyendo categoría."""
        nombre_filtro = self.nombre_input.text().lower().strip()
        codigo_filtro = self.codigo_input.text().lower().strip()
        categoria_id_filtro = self.categoria_filtro_combo.currentData() # <-- Nuevo filtro
        proveedor_id_filtro = self.proveedor_combo.currentData()

        productos_filtrados = []
        for producto in self.todos_los_productos:
            nombre_match = nombre_filtro in producto.get('nombre', '').lower() if nombre_filtro else True
            codigo_match = codigo_filtro in producto.get('codigo', '').lower() if codigo_filtro else True
            categoria_match = (categoria_id_filtro == -1 or producto.get('categoria_id') == categoria_id_filtro) # <-- Nueva condición
            proveedor_match = (proveedor_id_filtro == -1 or producto.get('proveedor_id') == proveedor_id_filtro)

            if nombre_match and codigo_match and categoria_match and proveedor_match: # <-- Añadir categoria_match
                productos_filtrados.append(producto)
        
        self.actualizar_tabla(productos_filtrados)

    def buscar_productos_db(self):
        """Busca en la base de datos incluyendo filtro por categoría."""
        nombre = self.nombre_input.text().strip()
        codigo = self.codigo_input.text().strip()
        categoria_id = self.categoria_filtro_combo.currentData() # <-- Nuevo filtro
        proveedor_id = self.proveedor_combo.currentData()
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            # ### <<< CAMBIO: Añadir JOIN con categoria y filtro >>> ###
            query = """
            SELECT 
                p.*, 
                CONCAT(prov.nombre, ' ', prov.apellido) as proveedor_nombre,
                cat.nombre_categoria as categoria_nombre 
            FROM producto p
            LEFT JOIN proveedor prov ON p.proveedor_id = prov.id
            LEFT JOIN categoria cat ON p.categoria_id = cat.id 
            WHERE 1=1
            """
            parametros = []
            
            if nombre:
                query += " AND p.nombre LIKE %s"
                parametros.append(f"%{nombre}%")
            if codigo:
                query += " AND p.codigo LIKE %s"
                parametros.append(f"%{codigo}%")
            if categoria_id != -1: # Si no es "Todas"
                query += " AND p.categoria_id = %s"
                parametros.append(categoria_id)
            if proveedor_id != -1: # Si no es "Todos"
                query += " AND p.proveedor_id = %s"
                parametros.append(proveedor_id)
            
            cursor.execute(query, parametros)
            productos_filtrados = cursor.fetchall()
            
            if not productos_filtrados:
                self.mostrar_alerta("Búsqueda Sin Resultados", "No se encontraron productos...", tipo="information")
                self.actualizar_tabla([])
            else:
                self.actualizar_tabla(productos_filtrados)

        except Exception as e:
            self.mostrar_alerta("Error de Búsqueda", f"Error al buscar: {e}", tipo="critical")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def listar_todos(self):
        """Limpia filtros y muestra todos los productos."""
        self.nombre_input.clear()
        self.codigo_input.clear()
        self.categoria_filtro_combo.setCurrentIndex(0)
        self.proveedor_combo.setCurrentIndex(0)
        self.actualizar_tabla(self.todos_los_productos)



    def limpiar_tabla_visual(self):
        """Limpia solo la visualización de la tabla."""
        self.table.setRowCount(0)


    def mostrar_alerta(self, titulo, mensaje, tipo="information"):
        msgBox = QMessageBox(self)
        msgBox.setWindowTitle(titulo)
      
        if tipo == "critical":
            msgBox.setIcon(QMessageBox.Icon.Critical)
            border_color = self.colores['peligro']
        elif tipo == "warning":
            msgBox.setIcon(QMessageBox.Icon.Warning)
            border_color = self.colores['advertencia'] # Asumiendo que tienes 'advertencia' en tus colores
        else: # Information
            msgBox.setIcon(QMessageBox.Icon.Information)
            border_color = self.colores['acento']
        msgBox.setText(f"<b>{titulo}</b>")
        msgBox.setInformativeText(mensaje) 
            
        # Aplicar estilos
        msgBox.setStyleSheet(f"""
            QMessageBox {{
                background-color: {self.colores['fondo']}; /* Fondo principal de la ventana */
                border: 1px solid {self.colores['borde']};
                border-left: 5px solid {border_color}; /* Borde izquierdo con color semántico */
                border-radius: 5px;
            }}
            /* Etiqueta principal (Título) */
            QMessageBox QLabel#qt_msgbox_label {{ /* Selector específico */
                color: {self.colores['texto_principal']};
                font-size: 16px; 
                font-weight: bold;
                padding-bottom: 10px; 
            }}
             /* Etiqueta secundaria (Mensaje) */
            QMessageBox QLabel#qt_msgbox_informativelabel {{ /* Selector específico */
                color: {self.colores['texto_secundario']};
                font-size: 14px;
                padding-left: 20px; /* Indentación para claridad */
                min-width: 300px; /* Asegurar espacio para el texto */
            }}
            QPushButton {{
                background-color: {self.colores['acento']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 20px; /* Más padding horizontal */
                font-weight: bold;
                min-width: 90px; /* Ancho mínimo */
                margin-top: 10px; /* Espacio arriba del botón */
            }}
            QPushButton:hover {{
                background-color: {self.colores['cabecera']};
            }}
        """)
  
        msgBox.addButton(QMessageBox.StandardButton.Ok) 
        
        msgBox.exec()
    
    def abrir_gestion_categorias(self):
        """Abre el diálogo para gestionar categorías."""
        # Pasamos 'self' como padre para que herede estilos y pueda emitir la señal
        dialog = CategoriasDialog(parent=self) 
        # Conectamos la señal del diálogo a nuestra función de recarga
        dialog.categories_updated.connect(self.recargar_datos_categorias)
        dialog.exec() # Abre el diálogo de forma modal

    def recargar_datos_categorias(self):
        """Recarga la lista de categorías y actualiza los ComboBox."""
        print("DEBUG: Recargando categorías después de la actualización...")

        # Guardar el ID seleccionado actualmente en el filtro (si existe)
        current_filter_cat_id = self.categoria_filtro_combo.currentData()

        # Volver a cargar las categorías desde la BD
        self.cargar_categorias() # Esto actualiza self.categorias y self.categoria_filtro_combo

        # Intentar restaurar la selección del filtro
        index_filtro = self.categoria_filtro_combo.findData(current_filter_cat_id)
        if index_filtro >= 0:
            self.categoria_filtro_combo.setCurrentIndex(index_filtro)
        else:
            self.categoria_filtro_combo.setCurrentIndex(0) # Volver a "Todas" si ya no existe

        if self.current_product_dialog and self.current_product_dialog.isVisible():
            print("DEBUG: Actualizando ComboBox en ProductDialog abierto...")
            # Llamamos a la nueva función que crearemos en ProductDialog
            self.current_product_dialog.actualizar_lista_categorias(self.categorias) 
        # Forzar recarga visual de la tabla
        self.filtrar_tabla_dinamico()
    
    def actualizar_tabla(self, productos_a_mostrar=None):
        """Muestra los productos en la tabla, asegurando que todas las columnas se llenen."""
        productos_mostrados = productos_a_mostrar if productos_a_mostrar is not None else self.todos_los_productos
        
        self.table.setRowCount(0) 
        for row_index, producto in enumerate(productos_mostrados):
            self.table.insertRow(row_index)
            
            # --- Llenar Celdas ---
            # Columna 0: ID (Oculta)
            id_val = producto.get('id')
            id_item = QTableWidgetItem(str(id_val) if id_val is not None else "NO_ID")
            self.table.setItem(row_index, 0, id_item)
            
            # ### <<< CORRECCIÓN AQUÍ: Asegurar que la Columna 1 (Código) se llene >>> ###
            codigo_val = producto.get('codigo', '') # Obtener el valor del código
            codigo_item = QTableWidgetItem(str(codigo_val)) # Crear el item
            self.table.setItem(row_index, 1, codigo_item) # Añadirlo a la columna 1
            
            # Columna 2: Nombre
            self.table.setItem(row_index, 2, QTableWidgetItem(str(producto.get('nombre', ''))))
            # Columna 3: Categoría
            self.table.setItem(row_index, 3, QTableWidgetItem(str(producto.get('categoria_nombre', 'N/A'))))
            # Columna 4: Stock Actual
            self.table.setItem(row_index, 4, QTableWidgetItem(str(producto.get('stockActual', ''))))
            # Columna 5: Stock Mínimo
            self.table.setItem(row_index, 5, QTableWidgetItem(str(producto.get('stockMinimo', ''))))
            # Columna 6: Precio Venta
            self.table.setItem(row_index, 6, QTableWidgetItem(str(producto.get('precioVenta', ''))))
            # Columna 7: Precio Compra
            self.table.setItem(row_index, 7, QTableWidgetItem(str(producto.get('precioCompra', ''))))
            # Columna 8: Proveedor
            self.table.setItem(row_index, 8, QTableWidgetItem(str(producto.get('proveedor_nombre', 'N/A'))))
            # Columna 9: Vencimiento
            fecha_v = producto.get('fVencimiento')
            fecha_str = fecha_v.strftime('%Y-%m-%d') if fecha_v else ""
            self.table.setItem(row_index, 9, QTableWidgetItem(fecha_str))
            
        self.table.setColumnHidden(0, True) # Ocultar ID al final

    def registrar_producto(self):
        """Abre el diálogo pasando las categorías."""
       
        dialog = ProductDialog(self, proveedores=self.proveedores, categorias=self.categorias) 
        self.current_product_dialog = dialog

        if dialog.exec():
            nuevo_producto = dialog.get_product_data()
            if nuevo_producto is None: return # Si hubo error de validación en el diálogo
            
            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                
                # ### <<< CAMBIO: Usar categoria_id en INSERT >>> ###
                query = """
                INSERT INTO producto 
                (codigo, nombre, categoria_id, stockActual, stockMinimo, precioVenta, 
                 precioCompra, proveedor_id, fVencimiento, fRegistro)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                valores = (
                    nuevo_producto['codigo'], nuevo_producto['nombre'], nuevo_producto['categoria_id'],
                    nuevo_producto['stockActual'], nuevo_producto['stockMinimo'], nuevo_producto['precioVenta'],
                    nuevo_producto['precioCompra'], nuevo_producto['proveedor_id'], 
                    nuevo_producto['fVencimiento'], nuevo_producto['fRegistro']
                )
                
                cursor.execute(query, valores)
                conexion.commit()
                self.mostrar_alerta("Éxito", "Producto registrado correctamente.")
                self.cargar_productos() 
                self.verificar_y_cargar_alertas() 
            except Exception as e:
                self.mostrar_alerta("Error", f"Error al registrar: {e}", tipo="critical")
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    cursor.close()
                    conexion.close()
                self.current_product_dialog = None

    def editar_producto(self):
        selected_rows = self.table.selectedItems()
        
        if not selected_rows:
            self.mostrar_alerta("Sin Selección", "Por favor, seleccione un producto de la tabla para editar.", tipo="warning")
            return
        
        selected_row_index = selected_rows[0].row()
        
        # --- Obtener ID de forma segura ---
        codigo_item = self.table.item(selected_row_index, 1) # Columna del Código
        
        # <<< DEBUG: VER QUÉ SE LEE DE LA TABLA >>>
        print(f"DEBUG: Celda Código ({selected_row_index}, 1): {codigo_item}") 
        
        if codigo_item is None or not codigo_item.text():
             self.mostrar_alerta("Error Interno", "No se pudo obtener el código del producto seleccionado de la tabla.", tipo="critical")
             print("DEBUG: Falló al obtener codigo_item o su texto.") # <<< DEBUG >>>
             return
             
        # <<< CAMBIO: Usar .strip() para eliminar espacios >>>
        codigo_producto_seleccionado = codigo_item.text().strip() 
        print(f"DEBUG: Código leído de la tabla (limpio): '{codigo_producto_seleccionado}'") # <<< DEBUG >>>

       
        producto_seleccionado = next((p for p in self.todos_los_productos if p.get('codigo', '').strip() == codigo_producto_seleccionado), None)
        
        if not producto_seleccionado:
            self.mostrar_alerta("Error Interno", f"No se encontró el producto con código '{codigo_producto_seleccionado}' en los datos cargados.", tipo="critical")
            print(f"DEBUG: No se encontró producto con código '{codigo_producto_seleccionado}' en self.todos_los_productos.") # <<< DEBUG >>>
            return
            
        print(f"DEBUG: Producto encontrado: {producto_seleccionado}") # <<< DEBUG >>>
        
        # --- Verificación de datos mínimos ---
        producto_id = producto_seleccionado.get('id')
        if producto_id is None:
            self.mostrar_alerta("Error de Datos", "El producto seleccionado parece no tener un ID válido.", tipo="critical")
            print("DEBUG: Producto encontrado pero sin ID.") # <<< DEBUG >>>
            return
            
  
        dialog = ProductDialog(self, producto_seleccionado, self.proveedores, self.categorias)
        self.current_product_dialog = dialog
        if dialog.exec():
            producto_editado = dialog.get_product_data()
            if producto_editado is None: return

            try:
                conexion = ConexionBD.obtener_conexion()
                cursor = conexion.cursor()
                query = """UPDATE producto SET 
                           codigo=%s, nombre=%s, categoria_id=%s, stockActual=%s, stockMinimo=%s, 
                           precioVenta=%s, precioCompra=%s, proveedor_id=%s, fVencimiento=%s 
                           WHERE id=%s"""
                fecha_vencimiento = producto_editado['fVencimiento'] if producto_editado['fVencimiento'] else None
                valores = (
                    producto_editado['codigo'], producto_editado['nombre'], producto_editado['categoria_id'],
                    producto_editado['stockActual'], producto_editado['stockMinimo'],
                    producto_editado['precioVenta'], producto_editado['precioCompra'],
                    producto_editado['proveedor_id'], fecha_vencimiento,
                    producto_id
                )
                cursor.execute(query, valores)
                conexion.commit()
                self.mostrar_alerta("Éxito", "Producto actualizado correctamente.")
                self.cargar_productos() 
                self.verificar_y_cargar_alertas()
            except Exception as e:
                self.mostrar_alerta("Error de Base de Datos", f"Error al actualizar:\n{e}", tipo="critical")
            finally:
                if 'conexion' in locals() and conexion.is_connected():
                    cursor.close()
                    conexion.close()
                self.current_product_dialog = None
    
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
        """Limpia filtros y muestra todos los productos cargados."""
        self.nombre_input.clear()
        self.codigo_input.clear()
        
        self.proveedor_combo.setCurrentIndex(0) # Selecciona "Todos los Proveedores"
        self.actualizar_tabla(self.todos_los_productos) # Muestra la lista completa cacheada
    
    def back(self):
        """Vuelve a mostrar la ventana principal que estaba oculta."""
        if self.parent_window:
            self.parent_window.show()
        self.close() 

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Es útil tener una clase padre falsa para probar el botón 'back'
    class FakeParent(QWidget):
        def __init__(self): super().__init__(); self.cargo = "Gerente"
    
    window = InventarioWindow(parent=FakeParent())
    window.show()
    sys.exit(app.exec())

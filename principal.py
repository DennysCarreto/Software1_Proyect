import sys
from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QGridLayout, QApplication, QFrame, QScrollArea, QMessageBox)
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QPixmap, QGuiApplication 
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize 

# Importaciones de Módulos
from modules.proveedores import ProveedoresWindow
from modules.clientes import ClientesWindow
from modules.ventas import VentasWindow
from modules.inventario import InventarioWindow
from modules.RegistroUsuario import VentanaRegistro
from modules.ui_components import AnimatedModuleButton, NotificationCard
from modules.notification_manager import get_all_notifications
from modules.dashboard_data_access import DashboardDataAccess # Asegúrate de que este archivo exista
from datetime import datetime 

class MainWindow(QMainWindow):
    def __init__(self, cargo):
        super().__init__()
        self.cargo = cargo
        self.current_module = None
        self.current_theme = 'dark' # Iniciar en modo oscuro

        # Paletas de colores
        self.color_palettes = {
            'dark': {
                "fondo": "#1A202C", "fondo_secundario": "#2D3748",
                "texto_principal": "#E2E8F0", "texto_secundario": "#A0AEC0",
                "cabecera": "#0B6E4F", "acento": "#3A9D5A", 
                "borde": "#4A5568", "peligro": "#E53E3E", "advertencia": "#ED8936", "info": "#3182CE",
                "blanco": "#FFFFFF", "negro": "#000000" 
            },
            'light': {
                "fondo": "#F8F9FA", "fondo_secundario": "#FFFFFF",
                "texto_principal": "#212529", "texto_secundario": "#6C757D",
                "cabecera": "#0B6E4F", "acento": "#3A9D5A", 
                "borde": "#DEE2E6", "peligro": "#E53E3E", "advertencia": "#ED8936", "info": "#3182CE",
                 "blanco": "#FFFFFF", "negro": "#000000"
            }
        }
        
        # Cargar iconos de tema
        try:
            self.icon_sun = QIcon("images/sol.png") 
            self.icon_moon = QIcon("images/luna.png") 
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar los iconos de tema: {e}")
            self.icon_sun = QIcon() 
            self.icon_moon = QIcon()

        self.setWindowTitle("Farma PLUS - Dashboard Principal")
        self.setMinimumSize(1024, 768)
        
        # Configuración UI
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.overall_layout = QHBoxLayout(central_widget)
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setSpacing(0)

        main_content_widget = QWidget()
        self.overall_layout.addWidget(main_content_widget, 1)

        self.main_layout = QVBoxLayout(main_content_widget) 
        self.main_layout.setContentsMargins(40, 20, 40, 40)
        self.main_layout.setSpacing(20)

        # Orden de creación corregido
        self._create_stylesheets() 
        self.setup_notification_panel() 
        self.setup_ui_elements() 
        self.apply_theme() 

        self.overall_layout.addWidget(self.notification_panel)
        self.load_notifications()
 
    def _get_color(self, key):
        return self.color_palettes.get(self.current_theme, {}).get(key, "#FF00FF") 

    def adjust_color(self, color, amount):
        try:
            qcolor = QColor(color)
            factor = 1.0 + (amount / 100.0)
            r = max(0, min(255, int(qcolor.red() * factor)))
            g = max(0, min(255, int(qcolor.green() * factor)))
            b = max(0, min(255, int(qcolor.blue() * factor)))
            return QColor(r, g, b).name()
        except Exception as e:
            return color

    def create_top_button_style(self, color, text_color=None): 
         bg_color = color
         txt_color = text_color if text_color else self._get_color('blanco') 
         hover_color = self.adjust_color(bg_color, -20)
         return f"""
             QPushButton {{ 
                 background-color: {bg_color}; color: {txt_color}; border: none;
                 border-radius: 17px; padding: 0 15px; 
                 font-family: "Segoe UI", sans-serif; font-size: 10pt; font-weight: bold; 
                 min-height: 35px; text-align: center; 
             }}
             QPushButton:hover {{ background-color: {hover_color}; }}
         """
         
    def _create_stylesheets(self):
        """Genera y guarda los strings de estilos como atributos de la clase."""
        self.style_header_label = f"font-size: 28px; font-weight: bold; color: {self._get_color('acento')}; background: transparent;"
        
        self.style_module_button = f"""
            QPushButton#AnimatedModuleButton {{ 
                background-color: {self._get_color('fondo_secundario')};
                border: 1px solid {self._get_color('borde')}; border-radius: 15px; min-width: 220px; min-height: 180px;
            }}
            QPushButton#AnimatedModuleButton QLabel {{ color: {self._get_color('texto_principal')}; background: transparent; font-size: 16px; font-weight: bold; border: none; padding: 0; }}
            QPushButton#AnimatedModuleButton:hover {{ background-color: {self._get_color('acento')}; border: 1px solid {self._get_color('acento')}; }}
            QPushButton#AnimatedModuleButton:hover QLabel {{ color: {self._get_color('blanco')}; }}
        """
        self.style_notification_panel = f"background-color: {self._get_color('fondo_secundario')}; border-left: 2px solid {self._get_color('acento')};"
        self.style_notification_title = f"color: {self._get_color('texto_principal')}; font-size: 18px; font-weight: bold; padding-bottom: 5px; background: transparent;"
        self.style_notification_scroll = f"QScrollArea {{ border: none; background: transparent; }} QWidget {{ background: transparent; }}" 
        self.style_notification_card_placeholder = f"color: {self._get_color('texto_secundario')}; font-style: italic; background: transparent;"
        
        # ### <<< CAMBIO: Estilos de KPI mejorados >>> ###
        self.style_kpi_section_title = f"font-size: 18px; font-weight: bold; color: {self._get_color('texto_principal')}; padding-bottom: 5px;"
        self.style_kpi_card_base = f"""
            QFrame {{ 
                background-color: {self._get_color('fondo_secundario')}; 
                border-radius: 8px; 
                padding: 10px; 
                margin: 5px;
            }}
        """
        self.style_kpi_value = f"font-size: 28px; font-weight: bold;" # Más grande
        self.style_kpi_label = f"font-size: 14px; color: {self._get_color('texto_secundario')}; font-weight: bold;" # Más claro y legible
        # ### <<< FIN CAMBIO >>> ###

    # --- Aplicación de Tema ---
    def apply_theme(self):
        """Aplica los colores y estilos del tema actual a la ventana."""
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self._get_color('fondo')))
        self.setPalette(palette)
        self.setStyleSheet(f"QMainWindow {{ background-color: {self._get_color('fondo')}; }} QWidget {{ color: {self._get_color('texto_principal')}; }}") 

        self._create_stylesheets() 
        
        if hasattr(self, 'title_label'): self.title_label.setStyleSheet(self.style_header_label)
        
        if hasattr(self, 'notification_panel'):
             self.notification_panel.setStyleSheet(self.style_notification_panel)
             if hasattr(self, 'notification_panel_title'): self.notification_panel_title.setStyleSheet(self.style_notification_title)
             if hasattr(self, 'notification_scroll_area'): self.notification_scroll_area.setStyleSheet(self.style_notification_scroll)
             
        if hasattr(self, 'register_button') and self.register_button: 
            self.register_button.setStyleSheet(self.create_top_button_style(color=self._get_color('acento')))
        if hasattr(self, 'notification_button'): 
            self.notification_button.setStyleSheet(self.create_top_button_style(color=self._get_color('advertencia'), text_color=self._get_color('blanco')))
        if hasattr(self, 'logout_button'): 
             self.logout_button.setStyleSheet(self.create_top_button_style(color=self._get_color('peligro')))
             
        if hasattr(self, 'theme_toggle_button'):
             self.theme_toggle_button.setIcon(self.icon_sun if self.current_theme == 'dark' else self.icon_moon)
             icon_color = self._get_color('texto_principal') 
             hover_bg = self.adjust_color(self._get_color('fondo_secundario'), 10 if self.current_theme=='dark' else -10)
             self.theme_toggle_button.setStyleSheet(f"""
                 QPushButton {{ background-color: transparent; border: none; padding: 5px; color: {icon_color}; border-radius: 17px; min-height: 35px;}}
                 QPushButton:hover {{ background-color: {hover_bg}; }}
             """)

        if hasattr(self, 'module_buttons'):
            for btn in self.module_buttons:
                btn.setStyleSheet(self.style_module_button) 
        
        if hasattr(self, 'kpi_container'):
             self.kpi_container.setStyleSheet(f"QFrame#KpiOverview {{ border-bottom: 2px solid {self._get_color('borde')}; padding-bottom: 15px; }}")
             self.load_kpi_data() # Recargar datos y re-aplicar estilos internos

        self.load_notifications() 
        self.update() 

    def toggle_theme(self):
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        print(f"DEBUG: Cambiando a tema: {self.current_theme}")
        self.apply_theme() 

    # --- Métodos de Construcción de UI ---
    def setup_ui_elements(self):
        """Llama a las funciones que construyen la interfaz en el orden correcto."""
        self.setup_top_bar(self.main_layout)
        
        # ### <<< CAMBIO: Poner KPIs ARRIBA de los módulos (solo para Gerente) >>> ###
        if self.cargo == 'Gerente':
            self.main_layout.addSpacing(15)
            self.setup_kpi_overview() # <-- Mover aquí
            self.main_layout.addSpacing(15) 
        
        self.setup_modules_grid(self.main_layout)

    def setup_top_bar(self, main_layout): 
        top_layout = QHBoxLayout()
        self.title_label = QLabel("FARMA PLUS +") 
        self.title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        
        self.register_button = None 
        if self.cargo == "Gerente":
            self.register_button = self.create_button("👤 Registrar Usuario")
            self.register_button.clicked.connect(self.register_user)

        self.notification_button = self.create_button("🔔 (0)") 
        self.notification_button.clicked.connect(self.toggle_notification_panel)
        
        self.theme_toggle_button = QPushButton("") 
        self.theme_toggle_button.setIconSize(QSize(24, 24)) 
        self.theme_toggle_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_toggle_button.setToolTip("Cambiar Tema Claro/Oscuro") 
        self.theme_toggle_button.clicked.connect(self.toggle_theme)

        self.logout_button = self.create_button("Cerrar Sesión") 
        self.logout_button.clicked.connect(self.logout)

        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        if self.register_button: top_layout.addWidget(self.register_button)
        top_layout.addWidget(self.notification_button)
        top_layout.addWidget(self.theme_toggle_button)
        top_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(top_layout)
        
    def setup_modules_grid(self, main_layout):
        """Configura y añade la parrilla de módulos al layout principal."""
        grid_layout = QGridLayout()
        grid_layout.setSpacing(40)
        
        ventas_module = AnimatedModuleButton("VENTAS", "images/venta.png")
        clientes_module = AnimatedModuleButton("CLIENTES", "images/cliente.png")
        inventario_module = AnimatedModuleButton("INVENTARIO", "images/inventario.png")
        proveedores_module = AnimatedModuleButton("PROVEEDORES", "images/proveedor.png")
        
        self.module_buttons = [ventas_module, clientes_module, inventario_module, proveedores_module] 

        grid_layout.addWidget(ventas_module, 0, 0, Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(clientes_module, 0, 1, Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(inventario_module, 1, 0, Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(proveedores_module, 1, 1, Qt.AlignmentFlag.AlignCenter)

        ventas_module.clicked.connect(lambda: self.open_module("ventas"))
        clientes_module.clicked.connect(lambda: self.open_module("clientes"))
        inventario_module.clicked.connect(lambda: self.open_module("inventario"))
        proveedores_module.clicked.connect(lambda: self.open_module("proveedores"))
        
        main_layout.addLayout(grid_layout)
        main_layout.addStretch() 

    # --- Sección de KPIs (Nueva Funcionalidad) ---
    def setup_kpi_overview(self):
        """Crea la sección de KPIs visibles solo para el Gerente."""
        
        # ### <<< NUEVO TÍTULO DE SECCIÓN >>> ###
        self.kpi_title_label = QLabel("Resumen Gerencial")
        self.kpi_title_label.setStyleSheet(self.style_kpi_section_title)
        self.kpi_title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.kpi_title_label) # Añadirlo al main_layout
        # ### <<< FIN DE TÍTULO >>> ###

        self.kpi_container = QFrame()
        self.kpi_container.setObjectName("KpiOverview")
        
        kpi_layout = QHBoxLayout(self.kpi_container)
        kpi_layout.setContentsMargins(0, 5, 0, 5) # Ajustar márgenes
        
        self.kpi_cards = {}
        kpi_data_points = [
            ("Ventas del Día", self._get_color('acento')),
            ("Productos Críticos", self._get_color('peligro')),
            ("Vencimiento (30 Días)", self._get_color('advertencia')),
            ("Top Cliente (30 Días)", self._get_color('info')),
        ]

        for label, color in kpi_data_points:
            card = self._create_kpi_card_ui(label, color)
            kpi_layout.addWidget(card)
            self.kpi_cards[label] = card.findChild(QLabel, 'kpi_value')
        
        self.main_layout.addWidget(self.kpi_container)
        self.load_kpi_data() # Cargar datos reales

    def _create_kpi_card_ui(self, label_text, color_accent):
        """Crea un widget QFrame para un solo KPI."""
        card = QFrame()
        card.setStyleSheet(self.style_kpi_card_base) 
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        # ### <<< CAMBIO: Usar estilos mejorados >>> ###
        value_label = QLabel("...")
        value_label.setObjectName("kpi_value") 
        value_label.setStyleSheet(self.style_kpi_value + f"color: {color_accent};")
        
        label = QLabel(label_text)
        label.setStyleSheet(self.style_kpi_label) # Usar el nuevo estilo
        # ### <<< FIN CAMBIO >>> ###
        
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        return card

    def load_kpi_data(self):
        """Carga los datos de la BD y actualiza los recuadros KPI."""
        if self.cargo != 'Gerente' or not hasattr(self, 'kpi_cards'):
            return
            
        try:
            kpis = DashboardDataAccess.get_kpis_resumen()

            self.kpi_cards["Ventas del Día"].setText(f"Q {kpis.get('ventas_dia', 0.0):,.2f}")
            self.kpi_cards["Productos Críticos"].setText(str(kpis.get('productos_criticos', 0)))
            self.kpi_cards["Vencimiento (30 Días)"].setText(str(kpis.get('proximos_a_vencer', 0)))
            self.kpi_cards["Top Cliente (30 Días)"].setText(kpis.get('top_cliente', "N/A"))

            # Re-aplicar estilos para asegurar consistencia en recargas/cambios de tema
            if hasattr(self, 'kpi_title_label'):
                self.kpi_title_label.setStyleSheet(self.style_kpi_section_title)
            self.kpi_container.setStyleSheet(f"QFrame#KpiOverview {{ border-bottom: 2px solid {self._get_color('borde')}; padding-bottom: 15px; margin: 0 10px; }}")

            for label, card_label in self.kpi_cards.items():
                card_widget = card_label.parentWidget()
                card_widget.setStyleSheet(self.style_kpi_card_base)
                card_label.setStyleSheet(self.style_kpi_value + f"color: {self._get_color_for_kpi(label)};")
                # Encontrar la otra etiqueta (el título del KPI) y aplicar su estilo
                card_widget.findChild(QLabel).setStyleSheet(self.style_kpi_label)

        except Exception as e:
            print(f"Error al cargar datos de KPIs: {e}")
            for key in self.kpi_cards:
                 if hasattr(self.kpi_cards[key], 'setText'):
                     self.kpi_cards[key].setText("ERROR")

    def _get_color_for_kpi(self, kpi_label):
        """Auxiliar para obtener el color correcto del KPI al recargar."""
        if kpi_label == "Ventas del Día": return self._get_color('acento')
        if kpi_label == "Productos Críticos": return self._get_color('peligro')
        if kpi_label == "Vencimiento (30 Días)": return self._get_color('advertencia')
        if kpi_label == "Top Cliente (30 Días)": return self._get_color('info')
        return self._get_color('texto_principal')

    # --- Resto de Métodos ---
    def create_button(self, text):
         button = QPushButton(text)
         button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
         button.setCursor(Qt.CursorShape.PointingHandCursor)
         return button

    def setup_notification_panel(self):
        self.notification_panel = QFrame()
        self.notification_panel.setFixedWidth(0) 
        panel_layout = QVBoxLayout(self.notification_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10); panel_layout.setSpacing(10)
        self.notification_panel_title = QLabel("Centro de Notificaciones") 
        panel_layout.addWidget(self.notification_panel_title)
        self.notification_scroll_area = QScrollArea() 
        self.notification_scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        self.notification_list_layout = QVBoxLayout(scroll_content)
        self.notification_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.notification_scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(self.notification_scroll_area)

    def toggle_notification_panel(self):
        current_width = self.notification_panel.width()
        target_width = 350 if current_width == 0 else 0
        self.animation = QPropertyAnimation(self.notification_panel, b"maximumWidth")
        self.animation.setDuration(400)
        self.animation.setStartValue(current_width)
        self.animation.setEndValue(target_width)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self.animation.start()

    def load_notifications(self):
        if not hasattr(self, 'notification_list_layout'): return 
        while self.notification_list_layout.count():
            child = self.notification_list_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        
        try:
             notifications = get_all_notifications()
             if hasattr(self, 'notification_button'):
                 self.notification_button.setText(f"🔔 ({len(notifications)})")
        except Exception as e:
             print(f"Error cargando notificaciones: {e}")
             notifications = []
             if hasattr(self, 'notification_button'): self.notification_button.setText("🔔 (?)")

        if not notifications:
            no_alerts_label = QLabel("No hay notificaciones nuevas.")
            if hasattr(self, 'style_notification_card_placeholder'):
                 no_alerts_label.setStyleSheet(self.style_notification_card_placeholder)
            no_alerts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notification_list_layout.addWidget(no_alerts_label)
            return

        for alert in notifications:
            card = None
            color_warn = self._get_color('advertencia')
            color_dang = self._get_color('peligro')
            text_color_card = self._get_color('blanco')

            if alert['type'] == 'inventory_stock':
                desc = f"Quedan {alert['stockActual']} (Mín: {alert['stockMinimo']})"
                card = NotificationCard("📦", alert['nombre'], desc, alert, color=color_warn)
            elif alert['type'] == 'inventory_expiry':
                fecha_obj = alert.get('fVencimiento')
                if isinstance(fecha_obj, datetime): fecha = fecha_obj.strftime('%d/%m/%Y')
                elif isinstance(fecha_obj, str):
                     try: fecha = datetime.strptime(fecha_obj, '%Y-%m-%d').strftime('%d/%m/%Y')
                     except ValueError: fecha = fecha_obj 
                else: fecha = 'N/A'
                desc = f"Vence el {fecha}"
                card = NotificationCard("⏳", alert['nombre'], desc, alert, color=color_dang)
            
            if card:
                card.setStyleSheet(f"{card.styleSheet()} QLabel {{ color: {text_color_card}; background: transparent; }}") 
                card.clicked.connect(self.handle_notification_click)
                self.notification_list_layout.addWidget(card)

    def handle_notification_click(self, alert_data):
        alert_type = alert_data.get('type', '')
        if alert_type.startswith('inventory'):
            self.open_module("inventario", showAlerts=True)
 
    def open_module(self, module_name, showAlerts=False):
        if self.current_module:
             try: self.current_module.close()
             except Exception as e: print(f"Error cerrando módulo anterior: {e}")
        self.current_module = None 
        
        window_class = None
        if module_name == "ventas": window_class = VentasWindow
        elif module_name == "clientes": window_class = ClientesWindow
        elif module_name == "inventario": window_class = InventarioWindow
        elif module_name == "proveedores": window_class = ProveedoresWindow
        # El dashboard ya no se abre como un módulo separado
        
        if window_class:
             try:
                # Pasar 'cargo' a los módulos que lo necesitan
                if module_name in ["inventario", "proveedores"]:
                    if module_name == "inventario": 
                        self.current_module = InventarioWindow(parent=self, cargo=self.cargo, show_notifications_on_start=showAlerts)
                    else:
                        self.current_module = window_class(parent=self, cargo=self.cargo)
                else: 
                     self.current_module = window_class(parent=self) # Para Ventas
                
                if self.current_module:
                    self.current_module.show()
                    self.hide()
             except Exception as e:
                  print(f"Error abriendo módulo '{module_name}': {e}")
                  QMessageBox.critical(self, "Error", f"No se pudo abrir el módulo: {module_name}\n{e}")
                  self.current_module = None 
                  self.show()

    def register_user(self):
        if not hasattr(self, 'register_window') or not self.register_window.isVisible():
            self.register_window = VentanaRegistro()
            self.register_window.show()

    def logout(self):
        from login import LoginWindow 
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def closeEvent(self, event): 
        if self.current_module:
            try: self.current_module.close()
            except Exception as e: print(f"Error cerrando módulo actual al salir: {e}")
        event.accept()

# --- Bloque de Ejecución Principal ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_win = MainWindow(cargo="Gerente") 
    main_win.show()
    sys.exit(app.exec())
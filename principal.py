import sys
from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QGridLayout, QApplication, QFrame, QScrollArea, QMessageBox)
# Make sure all necessary imports from QtGui and QtCore are present
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette, QPixmap 
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize 

# Importaciones de Módulos
from modules.proveedores import ProveedoresWindow
from modules.clientes import ClientesWindow
from modules.ventas import VentasWindow
from modules.inventario import InventarioWindow
from modules.RegistroUsuario import VentanaRegistro
from modules.ui_components import AnimatedModuleButton, NotificationCard # Ensure this file exists and is correct
from modules.notification_manager import get_all_notifications # Ensure this file exists and is correct
from datetime import datetime # Needed for load_notifications date formatting

class MainWindow(QMainWindow):
    def __init__(self, cargo):
        super().__init__()
        self.cargo = cargo
        self.current_module = None
        self.current_theme = 'dark' # Start with dark mode

        # ### <<< PALETAS DE COLORES PARA TEMAS >>> ###
        self.color_palettes = {
            'dark': {
                "fondo": "#1A202C", "fondo_secundario": "#2D3748",
                "texto_principal": "#E2E8F0", "texto_secundario": "#A0AEC0",
                "cabecera": "#0B6E4F", "acento": "#3A9D5A", 
                "borde": "#4A5568", 
                "peligro": "#E53E3E", "advertencia": "#ED8936", "info": "#3182CE",
                "blanco": "#FFFFFF", "negro": "#000000" 
            },
            'light': {
                "fondo": "#F8F9FA", "fondo_secundario": "#FFFFFF",
                "texto_principal": "#212529", "texto_secundario": "#6C757D",
                "cabecera": "#0B6E4F", "acento": "#3A9D5A", 
                "borde": "#DEE2E6",
                "peligro": "#E53E3E", "advertencia": "#ED8936", "info": "#3182CE",
                 "blanco": "#FFFFFF", "negro": "#000000"
            }
        }
        # ### <<< FIN PALETAS >>> ###
        
        # Load theme icons (ensure paths are correct)
        try:
            # Use specific filenames you have, e.g., 'sun.png', 'moon.png'
            self.icon_sun = QIcon("images/sol.png") # Or your actual sun icon filename
            self.icon_moon = QIcon("images/luna.png") # Or your actual moon icon filename
        except Exception as e:
            print(f"Advertencia: No se pudieron cargar los iconos de tema (sun.png/moon.png): {e}")
            self.icon_sun = QIcon() 
            self.icon_moon = QIcon()

        self.setWindowTitle("Farma PLUS - Dashboard Principal")
        self.setMinimumSize(1024, 768)
        
        # --- Initial UI Setup ---
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

        # Create notification panel structure (styling applied later)
        self.setup_notification_panel() 
        
        # --- Build UI Elements FIRST ---
        self.setup_ui_elements() 
        
        # --- Apply Initial Theme AFTER elements are created ---
        self.apply_theme() 

        # Add notification panel to the overall layout
        self.overall_layout.addWidget(self.notification_panel)
        self.load_notifications() # Load notifications after panel is added

    # --- Helper Methods (Define BEFORE use in __init__ or apply_theme) ---
    def _get_color(self, key):
        """Helper method to get the color for the current theme."""
        # Added .get() with a default for safety
        return self.color_palettes.get(self.current_theme, {}).get(key, "#FF00FF") # Magenta default on error

    def adjust_color(self, color, amount):
        """Lightens or darkens a color."""
        try:
            qcolor = QColor(color)
            # Use RGB manipulation for better dark/light adjustment
            factor = 1.0 + (amount / 100.0)
            r = max(0, min(255, int(qcolor.red() * factor)))
            g = max(0, min(255, int(qcolor.green() * factor)))
            b = max(0, min(255, int(qcolor.blue() * factor)))
            return QColor(r, g, b).name()
        except Exception as e:
            print(f"Error adjusting color '{color}': {e}")
            return color # Return original color on error

    # --- Stylesheet Generation ---
    def _create_stylesheets(self):
        """Generates stylesheets using the current theme's palette."""
        self.style_header_label = f"font-size: 28px; font-weight: bold; color: {self._get_color('acento')}; background: transparent;"
        
        # Style for AnimatedModuleButton (applied externally in apply_theme)
        # Ensure AnimatedModuleButton does NOT set its own stylesheet internally
        self.style_module_button = f"""
            QPushButton#AnimatedModuleButton {{ 
                background-color: {self._get_color('fondo_secundario')};
                border: 1px solid {self._get_color('borde')};
                border-radius: 15px; 
                min-width: 220px; 
                min-height: 180px;
            }}
            QPushButton#AnimatedModuleButton QLabel {{ 
                 color: {self._get_color('texto_principal')};
                 background: transparent; 
                 font-size: 16px; 
                 font-weight: bold;
                 border: none; 
                 padding: 0; 
            }}
            QPushButton#AnimatedModuleButton:hover {{ 
                background-color: {self._get_color('acento')}; 
                border: 1px solid {self._get_color('acento')};
            }}
             QPushButton#AnimatedModuleButton:hover QLabel {{ 
                 color: {self._get_color('blanco')}; 
            }}
        """
        self.style_notification_panel = f"background-color: {self._get_color('fondo_secundario')}; border-left: 2px solid {self._get_color('acento')};"
        self.style_notification_title = f"color: {self._get_color('texto_principal')}; font-size: 18px; font-weight: bold; padding-bottom: 5px; background: transparent;"
        self.style_notification_scroll = f"QScrollArea {{ border: none; background: transparent; }} QWidget {{ background: transparent; }}" 
        self.style_notification_card_placeholder = f"color: {self._get_color('texto_secundario')}; font-style: italic; background: transparent;"
        # Add styles for NotificationCard itself if needed (or apply in load_notifications)

    # --- Theme Application ---
    def apply_theme(self):
        """Applies colors and styles of the current theme to the window."""
        # 1. Apply main background color
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self._get_color('fondo')))
        self.setPalette(palette)
        self.setStyleSheet(f"QMainWindow {{ background-color: {self._get_color('fondo')}; }} QWidget {{ color: {self._get_color('texto_principal')}; }}") # Base style

        # 2. Regenerate theme-specific stylesheets
        self._create_stylesheets() 
        
        # 3. Re-apply styles to key widgets (check if they exist first)
        if hasattr(self, 'title_label'): self.title_label.setStyleSheet(self.style_header_label)
        
        if hasattr(self, 'notification_panel'):
             self.notification_panel.setStyleSheet(self.style_notification_panel)
             if hasattr(self, 'notification_panel_title'): self.notification_panel_title.setStyleSheet(self.style_notification_title)
             if hasattr(self, 'notification_scroll_area'): self.notification_scroll_area.setStyleSheet(self.style_notification_scroll)
             
        # Apply styles to top bar buttons dynamically
        if hasattr(self, 'register_button') and self.register_button: 
            self.register_button.setStyleSheet(self.create_top_button_style(color=self._get_color('acento')))
        if hasattr(self, 'notification_button'): 
            self.notification_button.setStyleSheet(self.create_top_button_style(color=self._get_color('advertencia'), text_color=self._get_color('blanco')))
        if hasattr(self, 'logout_button'): 
             self.logout_button.setStyleSheet(self.create_top_button_style(color=self._get_color('peligro')))
             
        # Update theme toggle button icon and style
        if hasattr(self, 'theme_toggle_button'):
             self.theme_toggle_button.setIcon(self.icon_sun if self.current_theme == 'dark' else self.icon_moon)
             icon_color = self._get_color('texto_principal') 
             hover_bg = self.adjust_color(self._get_color('fondo_secundario'), 10 if self.current_theme=='dark' else -10)
             self.theme_toggle_button.setStyleSheet(f"""
                 QPushButton {{ background-color: transparent; border: none; padding: 5px; color: {icon_color}; border-radius: 17px; min-height: 35px;}}
                 QPushButton:hover {{ background-color: {hover_bg}; }}
             """)

        # Update module button styles
        if hasattr(self, 'module_buttons'):
            for btn in self.module_buttons:
                btn.setStyleSheet(self.style_module_button) 
        
        # Reload notifications to apply theme colors to cards/placeholder
        self.load_notifications() 

        self.update() # Force repaint

    def toggle_theme(self):
        """Switches between light and dark mode."""
        self.current_theme = 'light' if self.current_theme == 'dark' else 'dark'
        print(f"DEBUG: Switching to theme: {self.current_theme}")
        self.apply_theme() 

    # --- UI Construction Methods ---
    def setup_ui_elements(self):
        """Calls the functions that build the UI sections."""
        self.setup_top_bar(self.main_layout)
        self.setup_modules_grid(self.main_layout)

    def setup_top_bar(self, main_layout): 
        top_layout = QHBoxLayout()
        # Create and store references to widgets first
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

        # Add widgets to layout
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        if self.register_button: top_layout.addWidget(self.register_button)
        top_layout.addWidget(self.notification_button)
        top_layout.addWidget(self.theme_toggle_button)
        top_layout.addWidget(self.logout_button)
        
        main_layout.addLayout(top_layout)
        
    def setup_modules_grid(self, main_layout):
        """Sets up and adds the module buttons grid to the main layout."""
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

    # --- Helper function for top buttons ---
    def create_button(self, text):
         """Creates a QPushButton for the top bar."""
         button = QPushButton(text)
         # Set font and cursor once
         button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
         button.setCursor(Qt.CursorShape.PointingHandCursor)
         # Styles are applied dynamically by apply_theme
         return button

    # Function to generate the stylesheet string for top buttons
    def create_top_button_style(self, color, text_color=None): 
         bg_color = color
         txt_color = text_color if text_color else self._get_color('blanco') 
         hover_color = self.adjust_color(bg_color, -20)
         # Ensure consistent font properties and min-height
         return f"""
             QPushButton {{ 
                 background-color: {bg_color}; color: {txt_color}; border: none;
                 border-radius: 17px; padding: 0 15px; 
                 font-family: "Segoe UI", sans-serif; font-size: 10pt; font-weight: bold; 
                 min-height: 35px; text-align: center; 
             }}
             QPushButton:hover {{ background-color: {hover_color}; }}
         """

    # --- Notification Panel Methods ---
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
        # Styles applied in apply_theme

    def toggle_notification_panel(self):
        current_width = self.notification_panel.width()
        target_width = 350 if current_width == 0 else 0
        self.animation = QPropertyAnimation(self.notification_panel, b"maximumWidth") # Target notification_panel
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
             # Update button text only if the button exists
             if hasattr(self, 'notification_button'):
                 self.notification_button.setText(f"🔔 ({len(notifications)})")
        except Exception as e:
             print(f"Error cargando notificaciones: {e}")
             notifications = []
             if hasattr(self, 'notification_button'): self.notification_button.setText("🔔 (?)")

        if not notifications:
            no_alerts_label = QLabel("No hay notificaciones nuevas.")
            # Apply style using the stored stylesheet string
            if hasattr(self, 'style_notification_card_placeholder'):
                 no_alerts_label.setStyleSheet(self.style_notification_card_placeholder)
            no_alerts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notification_list_layout.addWidget(no_alerts_label)
            return

        for alert in notifications:
            card = None
            color_warn = self._get_color('advertencia')
            color_dang = self._get_color('peligro')
            text_color_card = self._get_color('blanco') # Assuming white text on colored cards

            if alert['type'] == 'inventory_stock':
                desc = f"Quedan {alert['stockActual']} (Mín: {alert['stockMinimo']})"
                card = NotificationCard("📦", alert['nombre'], desc, alert, color=color_warn)
            elif alert['type'] == 'inventory_expiry':
                # Handle potential date string format if not datetime object
                fecha_obj = alert.get('fVencimiento')
                if isinstance(fecha_obj, datetime):
                    fecha = fecha_obj.strftime('%d/%m/%Y')
                elif isinstance(fecha_obj, str):
                     try: # Attempt to parse if it's a string like 'YYYY-MM-DD'
                          fecha = datetime.strptime(fecha_obj, '%Y-%m-%d').strftime('%d/%m/%Y')
                     except ValueError:
                          fecha = fecha_obj # Use the string as is if parsing fails
                else:
                    fecha = 'N/A'
                desc = f"Vence el {fecha}"
                card = NotificationCard("⏳", alert['nombre'], desc, alert, color=color_dang)
            
            if card:
                # Apply text color for labels inside the card
                card.setStyleSheet(f"{card.styleSheet()} QLabel {{ color: {text_color_card}; background: transparent; }}") 
                card.clicked.connect(self.handle_notification_click)
                self.notification_list_layout.addWidget(card)

    def handle_notification_click(self, alert_data):
        alert_type = alert_data.get('type', '')
        if alert_type.startswith('inventory'):
            self.open_module("inventario", showAlerts=True)
 
    # --- Module Navigation and Other Methods ---
    def open_module(self, module_name, showAlerts=False):
        """Opens a module and hides the main window."""
        self.current_module = None
        # Close previous module if open
        if self.current_module:
             try:
                  self.current_module.close()
             except Exception as e:
                  print(f"Error closing previous module: {e}")
             self.current_module = None # Clear reference
        
        # Create new module instance
        window_class = None
        if module_name == "ventas": window_class = VentasWindow
        elif module_name == "clientes": window_class = ClientesWindow
        elif module_name == "inventario": window_class = InventarioWindow
        elif module_name == "proveedores": window_class = ProveedoresWindow
        
        if window_class:
             try:
                  # Pass parent=self for proper window management
                  if module_name == "inventario":
                       self.current_module = InventarioWindow(parent=self, cargo=self.cargo, show_notifications_on_start=showAlerts)
                  else:
                       self.current_module = window_class(parent=self)
                  
                  if self.current_module:
                    self.current_module.show()
                    self.hide()
             except Exception as e:
                  print(f"Error opening module '{module_name}': {e}")
                  QMessageBox.critical(self, "Error", f"No se pudo abrir el módulo: {module_name}\n{e}")
                  self.current_module = None # Ensure it's None if creation failed
                  self.show() # Show main window again if module failed to open

    def register_user(self):
        # Prevent opening multiple registration windows
        if not hasattr(self, 'register_window') or not self.register_window.isVisible():
            self.register_window = VentanaRegistro()
            self.register_window.show()

    def logout(self):
        # This correctly closes the current window and opens the login window
        from login import LoginWindow 
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close() # Close the MainWindow

    def closeEvent(self, event): 
        """Ensure any open module is closed when the main window closes."""
        if self.current_module:
            try:
                self.current_module.close()
            except Exception as e:
                 print(f"Error closing current module on exit: {e}")
        event.accept()

# --- Main Execution Block ---
if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Ensure fonts are loaded if you use custom ones
    # QFontDatabase.addApplicationFont("fonts/Roboto-Regular.ttf") 
    main_win = MainWindow(cargo="Gerente") # Simulate login for testing
    main_win.show()
    sys.exit(app.exec())
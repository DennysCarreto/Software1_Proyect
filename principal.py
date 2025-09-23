import sys
from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QGridLayout, QApplication, QFrame, QScrollArea)
from PyQt6.QtGui import QFont, QIcon, QColor
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve

# ### <<< INICIO: NUEVAS IMPORTACIONES ESTRUCTURADAS >>> ###
from modules.proveedores import ProveedoresWindow
from modules.clientes import ClientesWindow
from modules.ventas import VentasWindow
from modules.inventario import InventarioWindow
from modules.RegistroUsuario import VentanaRegistro
# Componentes de UI personalizados
from modules.ui_components import AnimatedModuleButton, NotificationCard
# Gestor central de notificaciones
from modules.notification_manager import get_all_notifications
# ### <<< FIN: NUEVAS IMPORTACIONES ESTRUCTURADAS >>> ###


class MainWindow(QMainWindow):
    def __init__(self, cargo):
        super().__init__()
        self.cargo = cargo

        # ### <<< INICIO: NUEVO DISEÑO Y PALETA DE COLORES >>> ###
        self.setWindowTitle("Farma PLUS - Dashboard Principal")
        self.setMinimumSize(1024, 768)
        self.setStyleSheet("background-color: #1F2833;") # Fondo oscuro y moderno

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout general con espacio para el panel de notificaciones
        self.overall_layout = QHBoxLayout(central_widget)
        self.overall_layout.setContentsMargins(0, 0, 0, 0)
        self.overall_layout.setSpacing(0)

        # Contenedor principal para la UI del dashboard
        main_content_widget = QWidget()
        self.overall_layout.addWidget(main_content_widget, 1)

        # Layout vertical para el contenido
        main_layout = QVBoxLayout(main_content_widget)
        main_layout.setContentsMargins(40, 20, 40, 40)
        main_layout.setSpacing(20)

        # Creamos el panel de notificaciones (estará oculto al inicio)
        self.setup_notification_panel()
        self.overall_layout.addWidget(self.notification_panel)
        # ### <<< FIN: NUEVO DISEÑO Y PALETA DE COLORES >>> ###

        # --- Barra superior ---
        top_layout = QHBoxLayout()
        title_label = QLabel("FARMA PLUS +")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #66FCF1;") # Color turquesa vibrante
        top_layout.addWidget(title_label)
        top_layout.addStretch()

        if self.cargo == "Gerente":
            register_button = self.create_top_button("👤 Registrar Usuario")
            register_button.clicked.connect(self.register_user)
            top_layout.addWidget(register_button)

        # Botón de campana para notificaciones
        self.notification_button = self.create_top_button("🔔 (0)", color="#66FCF1", text_color="#1F2833")
        self.notification_button.clicked.connect(self.toggle_notification_panel)
        top_layout.addWidget(self.notification_button)
        
        logout_button = self.create_top_button("Cerrar Sesión", color="#d9534f")
        logout_button.clicked.connect(self.logout)
        top_layout.addWidget(logout_button)
        
        main_layout.addLayout(top_layout)

        # --- Grid para los módulos ---
        grid_layout = QGridLayout()
        grid_layout.setSpacing(40)
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        # Usamos nuestros nuevos botones animados
        ventas_module = AnimatedModuleButton("VENTAS", "images/venta.png")
        clientes_module = AnimatedModuleButton("CLIENTES", "images/cliente.png")
        inventario_module = AnimatedModuleButton("INVENTARIO", "images/inventario.png")
        proveedores_module = AnimatedModuleButton("PROVEEDORES", "images/proveedor.png")

        grid_layout.addWidget(ventas_module, 0, 0, Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(clientes_module, 0, 1, Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(inventario_module, 1, 0, Qt.AlignmentFlag.AlignCenter)
        grid_layout.addWidget(proveedores_module, 1, 1, Qt.AlignmentFlag.AlignCenter)

        ventas_module.clicked.connect(lambda: self.open_module("ventas"))
        clientes_module.clicked.connect(lambda: self.open_module("clientes"))
        inventario_module.clicked.connect(lambda: self.open_module("inventario"))
        proveedores_module.clicked.connect(lambda: self.open_module("proveedores"))

        # Cargar notificaciones al iniciar
        self.load_notifications()

    def create_top_button(self, text, color="#5cb85c", text_color="white"):
        button = QPushButton(text)
        button.setMinimumHeight(35)
        button.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: {text_color};
                border: none;
                border-radius: 17px;
                padding-left: 15px;
                padding-right: 15px;
            }}
            QPushButton:hover {{
                background-color: {self.adjust_color(color, -20)};
            }}
        """)
        
        return button
    def adjust_color(self, color, amount):
        color = QColor(color)
        h, s, l, a = color.getHsl()
        l = max(0, min(255, l + amount))
        color.setHsl(h, s, l, a)
        return color.name()

    # ### <<< INICIO: FUNCIONES PARA EL CENTRO DE NOTIFICACIONES >>> ###
    def setup_notification_panel(self):
        self.notification_panel = QFrame()
        self.notification_panel.setFixedWidth(0) # Inicia oculto
        self.notification_panel.setStyleSheet("background-color: #1F2833; border-left: 2px solid #66FCF1;")
        
        panel_layout = QVBoxLayout(self.notification_panel)
        panel_layout.setContentsMargins(10, 10, 10, 10)
        panel_layout.setSpacing(10)
        
        title_label = QLabel("Centro de Notificaciones")
        title_label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; padding-bottom: 5px;")
        panel_layout.addWidget(title_label)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_content = QWidget()
        self.notification_list_layout = QVBoxLayout(scroll_content)
        self.notification_list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(scroll_content)
        panel_layout.addWidget(scroll_area)

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
        # Limpiar notificaciones anteriores
        while self.notification_list_layout.count():
            child = self.notification_list_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        notifications = get_all_notifications()
        self.notification_button.setText(f"🔔 ({len(notifications)})")

        if not notifications:
            no_alerts_label = QLabel("No hay notificaciones nuevas.")
            no_alerts_label.setStyleSheet("color: #C5C6C7; font-style: italic;")
            no_alerts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notification_list_layout.addWidget(no_alerts_label)
            return

        for alert in notifications:
            card = None
            if alert['type'] == 'inventory_stock':
                desc = f"Quedan {alert['stockActual']} (Mínimo: {alert['stockMinimo']})"
                card = NotificationCard("📦", alert['nombre'], desc, alert, color="#E67E22")
            elif alert['type'] == 'inventory_expiry':
                fecha = alert['fVencimiento'].strftime('%d/%m/%Y')
                desc = f"Vence el {fecha}"
                card = NotificationCard("⏳", alert['nombre'], desc, alert, color="#E74C3C")
            
            if card:
                card.clicked.connect(self.handle_notification_click)
                self.notification_list_layout.addWidget(card)

    def handle_notification_click(self, alert_data):
        """Decide qué hacer al hacer clic en una notificación."""
        alert_type = alert_data.get('type', '')
        if alert_type.startswith('inventory'):
            # El parámetro 'showAlerts' le dirá a la ventana de inventario que se abra con el panel ya visible
            self.open_module("inventario", showAlerts=True)
    # ### <<< FIN: FUNCIONES PARA EL CENTRO DE NOTIFICACIONES >>> ###

    def open_module(self, module_name, showAlerts=False):
        """Abre un módulo y OCULTA la ventana principal."""
        
      
        self.current_module = None
        
        if module_name == "ventas":
            self.current_module = VentasWindow(parent=self)
        elif module_name == "clientes":
            self.current_module = ClientesWindow(parent=self)
        elif module_name == "inventario":
            self.current_module = InventarioWindow(parent=self, show_notifications_on_start=showAlerts)
        elif module_name == "proveedores":
            self.current_module = ProveedoresWindow(parent=self)
        
        if self.current_module:
            self.current_module.show()
            self.hide() 

    def register_user(self):
        self.register_window = VentanaRegistro()
        self.register_window.show()

    def logout(self):
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # Simula un inicio de sesión como Gerente para ver todos los botones
    main_win = MainWindow(cargo="Gerente") 
    main_win.show()
    sys.exit(app.exec())
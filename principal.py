from PyQt6.QtWidgets import (QMainWindow, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QWidget, QGridLayout, QApplication)
from PyQt6.QtGui import QFont, QIcon, QPixmap
from PyQt6.QtCore import Qt, QSize
from modules.proveedores import ProveedoresWindow
from modules.clientes import ClientesWindow
from modules.ventas import VentasWindow
from modules.inventario import InventarioWindow
from modules.RegistroUsuario import VentanaRegistro

class MainWindow(QMainWindow):
    def __init__(self,cargo):
        super().__init__()
        self.cargo = cargo

        # Configuración de la ventana principal
        self.setWindowTitle("Farma PLUS - Principal")
        self.setFixedSize(800, 600)
        self.setStyleSheet("background-color: #17A398;")  # Color turquesa
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal vertical
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Layout superior para el botón de registar Usuario
        top_layout = QHBoxLayout()
        if self.cargo == "Gerente":
            # Botón de registrar usuario (a la izquierda)
            register_button = QPushButton("Registrar usuario")
            register_button.setFixedSize(140, 35)
            register_button.setStyleSheet("""
                QPushButton {
                    background-color: #5cb85c;
                    color: white;
                    border-radius: 5px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4cae4c;
                }
            """)
            register_button.clicked.connect(self.register_user)  # Método que debes definir
            top_layout.addWidget(register_button)

        top_layout.addStretch()  # Espacio entre el botón izquierdo y el botón derecho

        logout_button = QPushButton("Cerrar sesión")
        logout_button.setFixedSize(120, 35)
        logout_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                border-radius: 5px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        logout_button.clicked.connect(self.logout)
        top_layout.addWidget(logout_button)

        # Agrega el layout superior al layout principal
        main_layout.addLayout(top_layout)

        # Título FARMA PLUS+
        title_label = QLabel("FARMA PLUS +")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 28, QFont.Weight.Bold))
        title_label.setStyleSheet("color: black;")
        main_layout.addWidget(title_label)

        # Grid para las 4 secciones
        grid_layout = QGridLayout()
        grid_layout.setSpacing(30)
        
        # Estilo común para los módulos
        module_style = """
            QWidget {
                background-color: #17A398;
                border-radius: 10px;
            }
            QLabel {
                color: black;
                font-weight: bold;
            }
        """
        
        # Función para crear un módulo
        def create_module(title, icon_path, row, col):
            module_widget = QWidget()
            module_widget.setFixedSize(250, 200)
            module_widget.setStyleSheet(module_style)
            module_widget.setCursor(Qt.CursorShape.PointingHandCursor)  # Cambia el cursor al pasar por encima
            
            module_layout = QVBoxLayout(module_widget)
            module_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Título del módulo
            title_label = QLabel(title)
            title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            title_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
            module_layout.addWidget(title_label)
            
            # Icono del módulo
            icon_label = QLabel()
            icon_pixmap = QPixmap(icon_path)
            if not icon_pixmap.isNull():
                icon_label.setPixmap(icon_pixmap.scaled(80, 80, Qt.AspectRatioMode.KeepAspectRatio))
            else:
                # Si no hay icono disponible, mostrar un placeholder
                icon_label.setText("🔍")
                icon_label.setFont(QFont("Arial", 40))
                icon_label.setStyleSheet("color: black;")
            
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            module_layout.addWidget(icon_label)
            
            grid_layout.addWidget(module_widget, row, col)
            
            return module_widget
        
        # Crear los cuatro módulos
        ventas_module = create_module("VENTAS", "images/venta.png", 0, 0)
        clientes_module = create_module("CLIENTES", "images/cliente.png", 0, 1)
        inventario_module = create_module("INVENTARIO", "images/inventario.png", 1, 0)
        proveedores_module = create_module("PROVEEDORES", "images/proveedor.png", 1, 1)
        
        # Conectar eventos de clic (se pueden implementar después)
        ventas_module.mousePressEvent = lambda event: self.open_module("ventas")
        clientes_module.mousePressEvent = lambda event: self.open_module("clientes")
        inventario_module.mousePressEvent = lambda event: self.open_module("inventario")
        proveedores_module.mousePressEvent = lambda event: self.open_module("proveedores")
        
        # Agregar el grid al layout principal
        main_layout.addLayout(grid_layout)
        main_layout.addStretch()

        # Almacena referencias a las ventanas de módulos
        self.module_windows = {}

    def logout(self):
        """Cerrar sesión y volver al login"""
        from login import LoginWindow  # Importación dentro de la función para evitar el ciclo
        
        # Cerrar todas las ventanas de módulos abiertas
        for window_name, window in list(self.module_windows.items()):
            if window:
                window.parent_window = None  # Desconectar la referencia al padre
                window.close()
                window.deleteLater()  # Programar la destrucción del objeto
                self.module_windows[window_name] = None
        
        # Limpiar diccionario
        self.module_windows.clear()
        
        # Crear y mostrar la ventana de login
        self.login_window = LoginWindow()
        self.login_window.show()
        
        # Cerrar la ventana principal
        self.close()
        
    def open_module(self, module_name):
        if module_name == "ventas":
            self.ventas_window = VentasWindow()
            self.ventas_window.show()
        elif module_name == "clientes":
            self.clientes_window = ClientesWindow()
            self.clientes_window.show()

        elif module_name == "inventario":
            from modules.inventario import InventarioWindow
            self.inventario_window = InventarioWindow()
            self.inventario_window.show()
            # Cerrar la ventana de principal
            self.close()

        elif module_name == "proveedores":
            self.proveedores_window = ProveedoresWindow()
            self.proveedores_window.show()
        """Abre el módulo seleccionado"""
        print(f"Abriendo módulo: {module_name}")

    def register_user(self):
        """Abrir ventana para registrar un nuevo usuario"""
        print("Registrar usuario clicado")
        self.clientes_window = VentanaRegistro()
        self.clientes_window.show()
# modules/ui_components.py

from PyQt6.QtWidgets import QFrame, QPushButton, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import pyqtSignal, QPropertyAnimation, QEasingCurve, QSize, Qt
from PyQt6.QtGui import QIcon, QPixmap, QFont

class NotificationCard(QFrame):
    """Una tarjeta individual para el centro de notificaciones."""
    # Señal que se emite cuando se hace clic en la tarjeta, enviando sus datos
    clicked = pyqtSignal(dict)

    def __init__(self, icon, title, description, alert_data, color="#34495E"):
        super().__init__()
        self.alert_data = alert_data
        
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setObjectName("NotificationCard")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(f"""
            #NotificationCard {{
                background-color: {color};
                border-radius: 8px;
            }}
            #NotificationCard:hover {{
                background-color: #4A6580;
            }}
        """)
        
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(15, 10, 15, 10)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 20px; color: white;")
        main_layout.addWidget(icon_label)
        
        text_layout = QVBoxLayout()
        text_layout.setSpacing(0)
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: white;")
        
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 11px; color: #EAECEE;")
        
        text_layout.addWidget(title_label)
        text_layout.addWidget(desc_label)
        main_layout.addLayout(text_layout, 1)

    def mousePressEvent(self, event):
        """Emite la señal 'clicked' cuando se presiona la tarjeta."""
        self.clicked.emit(self.alert_data)
        super().mousePressEvent(event)


class AnimatedModuleButton(QPushButton):
    """Un botón con animación de hover para los módulos del menú principal. (Versión 2.0)"""
    def __init__(self, title, icon_path):
        super().__init__()
        
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(80, 80))
        self.setFixedSize(220, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("ModuleButton")
        self.setStyleSheet("""
            #ModuleButton {
                background-color: #2C3E50;
                border-radius: 15px;
            }
            #ModuleButton:hover {
                background-color: #34495E;
            }
        """)
        
        # Usamos un layout para posicionar una etiqueta (QLabel) para el texto
        # Esto es más estable que usar el texto nativo del botón para el estilo.
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)

        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #FFFFFF; background-color: transparent;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Agregamos espacios flexibles para centrar el texto verticalmente bajo el icono
        layout.addStretch()
        layout.addWidget(title_label)
        
        # Animaciones
        self.animation_size = QPropertyAnimation(self, b"iconSize")
        self.animation_size.setDuration(200)
        self.animation_size.setEasingCurve(QEasingCurve.Type.InOutCubic)

    def enterEvent(self, event):
        self.animation_size.setStartValue(self.iconSize())
        self.animation_size.setEndValue(QSize(90, 90))
        self.animation_size.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation_size.setStartValue(self.iconSize())
        self.animation_size.setEndValue(QSize(80, 80))
        self.animation_size.start()
        super().leaveEvent(event)
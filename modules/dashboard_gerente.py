import sys
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QWidget, 
                             QGridLayout, QFrame, QScrollArea, QMessageBox, QApplication)
from PyQt6.QtGui import QPalette, QColor, QFont
from PyQt6.QtCore import Qt, QSize
from .dashboard_data_access import DashboardDataAccess

# --- Matplotlib Integration ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import pandas as pd
from datetime import datetime
class DashboardGerente(QMainWindow):
    def __init__(self, parent=None, cargo=None):
        super().__init__(parent)
        self.parent_window = parent
        self.cargo = cargo
        self.setWindowTitle("Farmaplus - Dashboard de Gerencia")
        self.setMinimumSize(1280, 800)

        # Heredar paleta de colores del padre
        self.colores = parent.color_palettes.get(parent.current_theme) if parent and hasattr(parent, 'color_palettes') else {
            "fondo": "#1A202C", "fondo_secundario": "#2D3748", "texto_principal": "#E2E8F0", 
            "acento": "#3A9D5A", "cabecera": "#0B6E4F", "peligro": "#E53E3E", "advertencia": "#ED8936",
            "info": "#3182CE", "blanco": "#FFFFFF", "negro": "#000000", "borde": "#4A5568"
        }
        self.current_theme = parent.current_theme if parent and hasattr(parent, 'current_theme') else 'dark'
        
        self._create_stylesheets()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colores.get('fondo')))
        self.setPalette(palette)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0,0,0,0)
        
        self._setup_header_bar()
        self._setup_content_scroll() 
        
        self.df_ventas = pd.DataFrame() # DataFrame para guardar datos de ventas
        self._cargar_datos_y_construir_dashboard()

    # --- Helper Methods ---
    def _get_color(self, key):
        return self.colores.get(key, "#FF00FF")

    def _create_stylesheets(self):
        """Define los estilos de la ventana."""
        self.style_header_label = f"font-size: 22px; font-weight: bold; color: {self._get_color('blanco')};"
        self.style_card = f"""
            QFrame {{ 
                background-color: {self._get_color('fondo_secundario')}; 
                border-radius: 10px; 
                padding: 15px; 
                color: {self._get_color('texto_principal')};
            }}
        """
        self.style_kpi_value = f"font-size: 36px; font-weight: bold; color: {self._get_color('acento')};"
        self.style_kpi_label = f"font-size: 14px; color: {self._get_color('texto_secundario')};"

    def _setup_header_bar(self):
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {self._get_color('cabecera')};")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)

        back_button = QPushButton("Regresar")
        back_button.setStyleSheet(f"background-color: {self._get_color('fondo_secundario')}; color: {self._get_color('texto_principal')}; border-radius: 5px; padding: 8px 12px; font-weight: bold;")
        back_button.clicked.connect(self.back_to_main)
        
        title_label = QLabel("Dashboard de Gerencia")
        title_label.setStyleSheet(self.style_header_label)

        header_layout.addWidget(back_button)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        self.main_layout.addWidget(header_frame)

    def _setup_content_scroll(self):
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        
        self.scroll_content = QWidget()
        self.content_layout = QVBoxLayout(self.scroll_content)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.content_layout.setSpacing(20)
        self.content_layout.setContentsMargins(20, 20, 20, 20)
        
        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

    def _cargar_datos_y_construir_dashboard(self):
        """Obtiene datos y llama a los métodos de construcción."""
        self.kpis = DashboardDataAccess.get_kpis_resumen()
        self.ventas_mensuales = DashboardDataAccess.get_ventas_por_mes()
        self.top_productos = DashboardDataAccess.get_top_productos_vendidos()
        
        self._setup_kpi_section()
        self._setup_charts_section()
        self._setup_ranking_section()

    def _setup_kpi_section(self):
        """Sección de Indicadores Clave."""
        kpi_grid = QGridLayout()
        
        # --- Tarjeta Venta del Día ---
        kpi_grid.addWidget(self._create_kpi_card("Ventas del Día", f"Q {self.kpis['ventas_dia']:,.2f}", self._get_color('acento')), 0, 0)
        
        # --- Tarjeta Productos Críticos ---
        kpi_grid.addWidget(self._create_kpi_card("Productos Críticos", f"{self.kpis['productos_criticos']}", self._get_color('peligro')), 0, 1)

        # --- Tarjeta Próximos a Vencer ---
        kpi_grid.addWidget(self._create_kpi_card("Próximos a Vencer (30 Días)", f"{self.kpis['proximos_a_vencer']}", self._get_color('advertencia')), 0, 2)
        
        # --- Tarjeta Top Cliente ---
        kpi_grid.addWidget(self._create_kpi_card("Top Cliente (30 Días)", self.kpis['top_cliente'], self._get_color('info')), 0, 3)

        self.content_layout.addLayout(kpi_grid)

    def _create_kpi_card(self, label, value, value_color):
        """Crea un QFrame estilizado para un KPI."""
        card = QFrame()
        card.setStyleSheet(self.style_card)
        layout = QVBoxLayout(card)
        
        value_label = QLabel(str(value))
        value_label.setStyleSheet(self.style_kpi_value.replace(self._get_color('acento'), value_color)) # Usar color dinámico
        
        label_kpi = QLabel(label)
        label_kpi.setStyleSheet(self.style_kpi_label)
        
        layout.addWidget(label_kpi)
        layout.addWidget(value_label)
        return card

    def _setup_charts_section(self):
        """Prepara los contenedores de los gráficos."""
        charts_container = QFrame()
        charts_container.setStyleSheet(self.style_card)
        charts_layout = QVBoxLayout(charts_container)
        
        charts_layout.addWidget(QLabel("Tendencia de Ventas Mensuales (Últimos 12 meses)", 
                                       styleSheet=f"font-size: 18px; font-weight: bold; color: {self._get_color('acento')};"))
        
        # 1. Crear el canvas de Matplotlib
        self.figure, self.ax = plt.subplots(facecolor=self._get_color('fondo_secundario'))
        self.canvas = FigureCanvas(self.figure)
        
        # 2. Dibujar el gráfico
        self.draw_sales_trend_chart() 
        
        # 3. Añadirlo al layout
        charts_layout.addWidget(self.canvas)
        
        # 4. Añadir el contenedor al layout principal
        self.content_layout.addWidget(charts_container)
        
    def draw_sales_trend_chart(self):
        """Dibuja el gráfico de tendencia de ventas (Línea)."""
        
        if self.df_ventas.empty:
            self.ax.text(0.5, 0.5, "No hay datos de ventas disponibles.", 
                         ha='center', va='center', 
                         color=self._get_color('texto_secundario'),
                         transform=self.ax.transAxes)
            self.canvas.draw()
            return
            
        # Limpiar el eje actual
        self.ax.clear()
        
        # Preparar los datos
        fechas = self.df_ventas['mes_anio'].tolist()
        ventas = self.df_ventas['ventas_mensuales'].tolist()

# Dibuja la línea de ventas (Change: Line Chart)
        self.ax.plot(fechas, ventas, 
                    marker='o', 
                    linestyle='-', 
                    color=self._get_color('acento'), 
                    linewidth=2)

        self.ax.tick_params(axis='x', colors=self._get_color('texto_secundario'), rotation=45) 
        # Usar tight_layout para asegurar que los elementos encajen
        self.figure.tight_layout(pad=2.0) 
        # Esta función ajusta los parámetros de la figura para un mejor ajuste de las fechas
        self.figure.autofmt_xdate(rotation=45) 

        self.ax.set_title("Ventas Agregadas por Mes", color=self._get_color('texto_principal'), fontsize=14) # Aumentar fuente
        self.ax.set_xlabel("Mes", color=self._get_color('texto_secundario'), labelpad=10)
        self.ax.set_ylabel("Ventas (Q)", color=self._get_color('texto_secundario'), labelpad=10)

        # Estilo de los ticks y bordes
        self.ax.tick_params(axis='x', colors=self._get_color('texto_secundario'), rotation=45)
        self.ax.tick_params(axis='y', colors=self._get_color('texto_secundario'))

        # --- INICIO: CORRECCIÓN DE CONTRASTE ---

        # 1. Fondo del ÁREA del plot (fondo_secundario)
        self.ax.set_facecolor(self._get_color('fondo_secundario')) 

        # 2. Fondo de la Figura completa (Usar un color ligeramente distinto para la figura)
        self.figure.set_facecolor(self._get_color('fondo_secundario')) 

        # 3. Añadir una cuadrícula (Grid) para facilitar la lectura de los valores
        self.ax.grid(True, linestyle='--', alpha=0.3, color=self._get_color('texto_secundario'))

        # 4. Asegurar que la línea de color de la marca sea visible (Color: acento)
        # La línea de plot ya usa self._get_color('acento')
        # --- FIN: CORRECCIÓN DE CONTRASTE ---

        # Redibuja el canvas para actualizar la interfaz
        self.figure.tight_layout(pad=2.0) # Asegurar el padding final
        self.canvas.draw()
    # ### <<< FIN: FUNCIÓN PRINCIPAL DE GRÁFICO >>> ###
        
    def _setup_ranking_section(self):
        """Sección para el ranking de productos."""
        ranking_container = QFrame()
        ranking_container.setStyleSheet(self.style_card)
        ranking_layout = QVBoxLayout(ranking_container)
        
        ranking_layout.addWidget(QLabel("Top 5 Productos Vendidos (30 Días)", styleSheet=f"font-size: 18px; font-weight: bold; color: {self._get_color('acento')};"))
        
        # Mostrar los resultados del top 5 en una lista simple
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)
        
        for i, prod in enumerate(self.top_productos):
            color = self._get_color('peligro') if i < 2 else self._get_color('acento')
            item_label = QLabel(f"#{i+1}: {prod['producto_nombre']} - {prod['cantidad_vendida']} unidades")
            item_label.setStyleSheet(f"font-size: 16px; font-weight: bold; padding: 5px; border-bottom: 1px solid {self._get_color('borde')}; color: {color};")
            list_layout.addWidget(item_label)
            
        ranking_layout.addWidget(list_widget)
        self.content_layout.addWidget(ranking_container)


    def _cargar_datos_y_construir_dashboard(self):
        """Obtiene datos y llama a los métodos de construcción."""
        self.kpis = DashboardDataAccess.get_kpis_resumen()
        
        # Cargar ventas mensuales en el DataFrame
        ventas_data = DashboardDataAccess.get_ventas_por_mes()
        if ventas_data:
            self.df_ventas = pd.DataFrame(ventas_data)
        
        self.top_productos = DashboardDataAccess.get_top_productos_vendidos()
        
        self._setup_kpi_section()
        self._setup_charts_section() # Llama al gráfico
        self._setup_ranking_section()

    def back_to_main(self):
        if self.parent_window:
            self.parent_window.show()
        self.close()
# Bloque principal para pruebas
if __name__ == '__main__':
    app = QApplication(sys.argv)
    class FakeParent(QWidget):
        def __init__(self): 
            super().__init__()
            self.colores = { "fondo": "#1A202C", "fondo_secundario": "#2D3748", "texto_principal": "#E2E8F0", "acento": "#3A9D5A", "borde": "#4A5568", "peligro": "#E53E3E", "advertencia": "#ED8936", "info": "#3182CE", "blanco": "#FFFFFF", "negro": "#000000" }
            self.color_palettes = {'dark': self.colores, 'light': {**self.colores, "fondo": "#F8F9FA", "texto_principal": "#212529"}}
            self.current_theme = 'dark'
            self.cargo = "Gerente" # Asegurar que tiene permisos
    
    window = DashboardGerente(parent=FakeParent())
    window.show()
    sys.exit(app.exec())
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QTableWidget, QMessageBox,
                             QTableWidgetItem, QHeaderView, QFrame, QLineEdit,
                             QComboBox, QGridLayout, QFileDialog)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QTextDocument
import mysql.connector
from datetime import datetime, timedelta
import sys
import os

# Añadir la ruta del directorio padre para importar ConexionBD
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from conexion import ConexionBD


class ReportesInventarioWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Reportes de Inventario")
        self.setMinimumSize(1200, 700)

        # Colores del diseño
        self.colores = {
            "fondo": "#F8F9FA",
            "cabecera": "#0B6E4F",
            "texto_principal": "#212529",
            "acento": "#3A9D5A",
            "borde": "#DEE2E6",
            "azul_claro": "#7B9EB7",
            "peligro": "#E53E3E"
        }

        self._create_stylesheets()

        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(self.colores["fondo"]))
        self.setPalette(palette)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        self._setup_header_bar()
        self._setup_filter_panel()
        self._setup_table()
        self._setup_summary_panel()
        self._setup_action_buttons()

        # Cargar datos al inicio
        self.cargar_categorias()
        self.cargar_proveedores()
        self.generar_reporte()

    def _create_stylesheets(self):
        """Define todos los estilos de la ventana."""
        self.style_header_label = "font-size: 22px; font-weight: bold; color: white;"

        self.style_header_button = f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {self.colores['texto_principal']};
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: #E2E8F0;
            }}
        """

        self.style_primary_button = f"""
            QPushButton {{
                background-color: {self.colores['acento']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 13px;
            }}
            QPushButton:hover {{
                background-color: {self.colores['cabecera']};
            }}
        """

        self.style_filter_frame = f"""
            QFrame {{
                background-color: white;
                border: 1px solid {self.colores['borde']};
                border-radius: 8px;
                padding: 10px;
            }}
        """

        self.style_input = f"""
            QLineEdit, QComboBox {{
                border: 1px solid {self.colores['borde']};
                border-radius: 5px;
                padding: 6px;
                font-size: 12px;
                background-color: white;
            }}
        """

        self.style_table = f"""
            QTableWidget {{
                border: 1px solid {self.colores['borde']};
                gridline-color: {self.colores['borde']};
                font-size: 13px;
                background-color: white;
            }}
            QHeaderView::section {{
                background-color: {self.colores['azul_claro']};
                color: white;
                padding: 10px;
                border: 1px solid {self.colores['azul_claro']};
                font-weight: bold;
                font-size: 13px;
            }}
            QTableWidget::item:selected {{
                background-color: {self.colores['acento']};
                color: white;
            }}
        """

    def _setup_header_bar(self):
        """Crea la barra de cabecera."""
        header_frame = QFrame()
        header_frame.setStyleSheet(f"background-color: {self.colores['cabecera']}; padding: 5px;")
        header_layout = QHBoxLayout(header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)

        back_button = QPushButton("← Regresar")
        back_button.setStyleSheet(self.style_header_button)
        back_button.clicked.connect(self.back_to_main)

        title_label = QLabel("Módulo Inventario - Reportes")
        title_label.setStyleSheet(self.style_header_label)

        header_layout.addWidget(back_button)
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.main_layout.addWidget(header_frame)

    def _setup_filter_panel(self):
        """Crea el panel de filtros compacto."""
        filter_container = QWidget()
        filter_container.setStyleSheet("margin: 0 15px;")
        filter_layout = QVBoxLayout(filter_container)

        filter_frame = QFrame()
        filter_frame.setStyleSheet(self.style_filter_frame)
        filter_grid = QGridLayout(filter_frame)
        filter_grid.setSpacing(8)
        filter_grid.setContentsMargins(10, 8, 10, 8)

        # Etiqueta de sección
        filter_label = QLabel("FILTROS APLICADOS")
        filter_label.setStyleSheet(f"font-weight: bold; color: {self.colores['azul_claro']}; font-size: 12px;")
        filter_grid.addWidget(filter_label, 0, 0, 1, 6)

        # Labels con estilo visible
        label_style = f"color: {self.colores['texto_principal']}; font-size: 11px; font-weight: bold;"

        # Primera fila: Nombre y Código
        lbl_nombre = QLabel("Nombre:")
        lbl_nombre.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_nombre, 1, 0)

        self.filtro_nombre = QLineEdit()
        self.filtro_nombre.setPlaceholderText("Nombre...")
        self.filtro_nombre.setStyleSheet(self.style_input)
        self.filtro_nombre.setMaximumWidth(150)
        filter_grid.addWidget(self.filtro_nombre, 1, 1)

        lbl_codigo = QLabel("Código:")
        lbl_codigo.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_codigo, 1, 2)

        self.filtro_codigo = QLineEdit()
        self.filtro_codigo.setPlaceholderText("Código...")
        self.filtro_codigo.setStyleSheet(self.style_input)
        self.filtro_codigo.setMaximumWidth(100)
        filter_grid.addWidget(self.filtro_codigo, 1, 3)

        # Segunda fila: Categoría, Proveedor y Stock
        lbl_categoria = QLabel("Categoría:")
        lbl_categoria.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_categoria, 2, 0)

        self.combo_categoria = QComboBox()
        self.combo_categoria.setStyleSheet(self.style_input)
        self.combo_categoria.setMaximumWidth(150)
        filter_grid.addWidget(self.combo_categoria, 2, 1)

        lbl_proveedor = QLabel("Proveedor:")
        lbl_proveedor.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_proveedor, 2, 2)

        self.combo_proveedor = QComboBox()
        self.combo_proveedor.setStyleSheet(self.style_input)
        self.combo_proveedor.setMaximumWidth(150)
        filter_grid.addWidget(self.combo_proveedor, 2, 3)

        lbl_stock = QLabel("Stock:")
        lbl_stock.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_stock, 2, 4)

        self.combo_stock = QComboBox()
        self.combo_stock.addItem("Todos", "todos")
        self.combo_stock.addItem("Stock Bajo", "bajo")
        self.combo_stock.addItem("Stock Normal", "normal")
        self.combo_stock.setStyleSheet(self.style_input)
        self.combo_stock.setMaximumWidth(120)
        filter_grid.addWidget(self.combo_stock, 2, 5)

        # Botones de acción
        btn_filtrar = QPushButton("🔍 Generar Reporte")
        btn_filtrar.setStyleSheet(self.style_primary_button)
        btn_filtrar.clicked.connect(self.generar_reporte)
        btn_filtrar.setMaximumWidth(160)
        filter_grid.addWidget(btn_filtrar, 3, 0, 1, 2)

        btn_limpiar = QPushButton("✨ Limpiar")
        btn_limpiar.setStyleSheet(self.style_header_button)
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        btn_limpiar.setMaximumWidth(100)
        filter_grid.addWidget(btn_limpiar, 3, 2)

        filter_grid.setColumnStretch(6, 1)

        filter_layout.addWidget(filter_frame)
        self.main_layout.addWidget(filter_container)

    def _setup_table(self):
        """Crea la tabla de productos."""
        table_container = QWidget()
        table_container.setStyleSheet("margin: 0 15px;")
        table_layout = QVBoxLayout(table_container)

        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "ID", "Código", "Nombre", "Categoría", "Stock",
            "Mínimo", "P. Venta", "P. Compra", "Proveedor", "Vencimiento"
        ])

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)

        self.table.setStyleSheet(self.style_table)
        self.table.setMinimumHeight(300)

        table_layout.addWidget(self.table)
        self.main_layout.addWidget(table_container)

    def _setup_summary_panel(self):
        """Crea el panel de resumen con estadísticas."""
        summary_container = QWidget()
        summary_container.setStyleSheet("margin: 0 15px;")
        summary_layout = QHBoxLayout(summary_container)
        summary_layout.setSpacing(15)

        # Total de Productos
        self.summary_total = self._create_summary_box(
            "Total Productos", "0", self.colores['azul_claro']
        )

        # Valor Total Inventario
        self.summary_valor = self._create_summary_box(
            "Valor Total", "Q 0.00", self.colores['azul_claro']
        )

        # Productos Stock Bajo
        self.summary_stock_bajo = self._create_summary_box(
            "Stock Bajo", "0", self.colores['peligro']
        )

        # Productos Próximos a Vencer
        self.summary_por_vencer = self._create_summary_box(
            "Por Vencer (30d)", "0", self.colores['acento']
        )

        summary_layout.addWidget(self.summary_total)
        summary_layout.addWidget(self.summary_valor)
        summary_layout.addWidget(self.summary_stock_bajo)
        summary_layout.addWidget(self.summary_por_vencer)

        self.main_layout.addWidget(summary_container)

    def _create_summary_box(self, titulo, valor, color):
        """Crea una caja de resumen individual."""
        frame = QFrame()
        frame.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {color};
                border-radius: 5px;
                padding: 12px;
            }}
        """)

        layout = QVBoxLayout(frame)
        layout.setSpacing(5)

        label_titulo = QLabel(titulo)
        label_titulo.setStyleSheet(f"color: {self.colores['texto_principal']}; font-size: 11px;")

        label_valor = QLabel(valor)
        label_valor.setStyleSheet(f"color: {color}; font-size: 22px; font-weight: bold;")
        label_valor.setObjectName("valor")

        layout.addWidget(label_titulo)
        layout.addWidget(label_valor)

        return frame

    def _setup_action_buttons(self):
        """Crea los botones de acción."""
        button_container = QWidget()
        button_container.setStyleSheet("margin: 0 15px 15px 15px;")
        button_layout = QHBoxLayout(button_container)

        btn_imprimir = QPushButton("🖨️ Imprimir")
        btn_imprimir.setStyleSheet(self.style_primary_button)
        btn_imprimir.clicked.connect(self.imprimir_reporte)

        btn_exportar = QPushButton("📄 Exportar PDF")
        btn_exportar.setStyleSheet(self.style_primary_button)
        btn_exportar.clicked.connect(self.exportar_pdf)

        button_layout.addStretch()
        button_layout.addWidget(btn_imprimir)
        button_layout.addWidget(btn_exportar)

        self.main_layout.addWidget(button_container)

    def cargar_categorias(self):
        """Carga las categorías en el combo box."""
        self.combo_categoria.clear()
        self.combo_categoria.addItem("Todas", None)

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre_categoria FROM categoria WHERE estado = 1 ORDER BY nombre_categoria")
            categorias = cursor.fetchall()

            for cat in categorias:
                self.combo_categoria.addItem(cat['nombre_categoria'], cat['id'])

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al cargar categorías: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def cargar_proveedores(self):
        """Carga los proveedores en el combo box."""
        self.combo_proveedor.clear()
        self.combo_proveedor.addItem("Todos", None)

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT id, nombre, marca FROM proveedor WHERE activo = 1 ORDER BY nombre")
            proveedores = cursor.fetchall()

            for prov in proveedores:
                nombre_completo = f"{prov['nombre']} ({prov['marca']})"
                self.combo_proveedor.addItem(nombre_completo, prov['id'])

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al cargar proveedores: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.filtro_nombre.clear()
        self.filtro_codigo.clear()
        self.combo_categoria.setCurrentIndex(0)
        self.combo_proveedor.setCurrentIndex(0)
        self.combo_stock.setCurrentIndex(0)
        self.generar_reporte()

    def generar_reporte(self):
        """Genera el reporte con los filtros aplicados."""
        nombre = self.filtro_nombre.text().strip()
        codigo = self.filtro_codigo.text().strip()
        categoria_id = self.combo_categoria.currentData()
        proveedor_id = self.combo_proveedor.currentData()
        estado_stock = self.combo_stock.currentData()

        self.table.setRowCount(0)

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)

            # Construir la consulta con filtros
            query = """
                SELECT 
                    p.id,
                    p.codigo,
                    p.nombre,
                    c.nombre_categoria as categoria,
                    p.stockActual,
                    p.stockMinimo,
                    p.precioVenta,
                    p.precioCompra,
                    CONCAT(pr.nombre, ' (', pr.marca, ')') as proveedor,
                    p.fVencimiento
                FROM producto p
                LEFT JOIN categoria c ON p.categoria_id = c.id
                LEFT JOIN proveedor pr ON p.proveedor_id = pr.id
                WHERE 1=1
            """

            params = []

            if nombre:
                query += " AND p.nombre LIKE %s"
                params.append(f"%{nombre}%")

            if codigo:
                query += " AND p.codigo LIKE %s"
                params.append(f"%{codigo}%")

            if categoria_id:
                query += " AND p.categoria_id = %s"
                params.append(categoria_id)

            if proveedor_id:
                query += " AND p.proveedor_id = %s"
                params.append(proveedor_id)

            if estado_stock == "bajo":
                query += " AND p.stockActual <= p.stockMinimo"
            elif estado_stock == "normal":
                query += " AND p.stockActual > p.stockMinimo"

            query += " ORDER BY p.nombre"

            cursor.execute(query, params)
            productos = cursor.fetchall()

            # Llenar la tabla
            self.table.setRowCount(len(productos))

            valor_total = 0
            stock_bajo_count = 0
            por_vencer_count = 0
            fecha_limite = datetime.now() + timedelta(days=30)

            for i, prod in enumerate(productos):
                self.table.setItem(i, 0, QTableWidgetItem(str(prod['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(prod['codigo'] or ''))
                self.table.setItem(i, 2, QTableWidgetItem(prod['nombre'] or ''))
                self.table.setItem(i, 3, QTableWidgetItem(prod['categoria'] or 'N/A'))

                stock_actual = prod['stockActual'] or 0
                stock_minimo = prod['stockMinimo'] or 0
                self.table.setItem(i, 4, QTableWidgetItem(str(stock_actual)))
                self.table.setItem(i, 5, QTableWidgetItem(str(stock_minimo)))

                precio_venta = prod['precioVenta'] or 0
                precio_compra = prod['precioCompra'] or 0
                self.table.setItem(i, 6, QTableWidgetItem(f"Q {precio_venta:.2f}"))
                self.table.setItem(i, 7, QTableWidgetItem(f"Q {precio_compra:.2f}"))

                self.table.setItem(i, 8, QTableWidgetItem(prod['proveedor'] or 'N/A'))

                fecha_v = prod['fVencimiento']
                fecha_str = fecha_v.strftime('%d/%m/%Y') if fecha_v else 'N/A'
                self.table.setItem(i, 9, QTableWidgetItem(fecha_str))

                # Calcular estadísticas
                valor_total += stock_actual * precio_compra

                if stock_actual <= stock_minimo and stock_actual > 0:
                    stock_bajo_count += 1

                if fecha_v and fecha_v <= fecha_limite:
                    por_vencer_count += 1

            # Actualizar resumen
            total_productos = len(productos)
            self._actualizar_resumen(total_productos, valor_total, stock_bajo_count, por_vencer_count)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def _actualizar_resumen(self, total, valor, stock_bajo, por_vencer):
        """Actualiza los valores del panel de resumen."""
        valor_label = self.summary_total.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(total))

        valor_label = self.summary_valor.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(f"Q {valor:,.2f}")

        valor_label = self.summary_stock_bajo.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(stock_bajo))

        valor_label = self.summary_por_vencer.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(por_vencer))

    def imprimir_reporte(self):
        """Imprime el reporte."""
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QPrintDialog.DialogCode.Accepted:
            self._pintar_reporte(printer)

    def exportar_pdf(self):
        """Exporta el reporte a PDF."""
        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte",
            f"Reporte_Inventario_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            "PDF Files (*.pdf)"
        )

        if filename:
            printer = QPrinter(QPrinter.PrinterMode.HighResolution)
            printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
            printer.setOutputFileName(filename)
            self._pintar_reporte(printer)
            QMessageBox.information(self, "Éxito", f"Reporte exportado exitosamente a:\n{filename}")

    def _pintar_reporte(self, printer):
        """Pinta el reporte en el dispositivo de impresión."""
        html = self._generar_html_reporte()
        document = QTextDocument()
        document.setHtml(html)
        document.print(printer)

    def _generar_html_reporte(self):
        """Genera el HTML del reporte con escala optimizada para PDF."""
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        nombre_filtro = self.filtro_nombre.text() or "Todos"
        codigo_filtro = self.filtro_codigo.text() or "Todos"
        categoria_filtro = self.combo_categoria.currentText()
        proveedor_filtro = self.combo_proveedor.currentText()
        stock_filtro = self.combo_stock.currentText()

        # Obtener resúmenes
        total = self.summary_total.findChild(QLabel, "valor").text()
        valor = self.summary_valor.findChild(QLabel, "valor").text()
        stock_bajo = self.summary_stock_bajo.findChild(QLabel, "valor").text()
        por_vencer = self.summary_por_vencer.findChild(QLabel, "valor").text()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{ 
                    margin: 15mm 12mm; 
                    size: letter landscape;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0;
                    font-size: 10pt;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 15px;
                    border-bottom: 3px solid #7B9EB7;
                    padding-bottom: 10px;
                }}
                .header h1 {{ 
                    font-size: 20pt; 
                    margin: 3px 0; 
                    font-weight: bold;
                    color: #0B6E4F;
                }}
                .header h2 {{ 
                    font-size: 16pt; 
                    margin: 3px 0; 
                    font-weight: bold;
                    color: #333;
                }}
                .company-info {{ 
                    text-align: right; 
                    font-size: 9pt; 
                    color: #666; 
                    margin-bottom: 10px;
                    line-height: 1.3;
                }}
                .info-box {{ 
                    background-color: #f5f5f5; 
                    padding: 10px 12px; 
                    margin-bottom: 12px; 
                    border-left: 4px solid #7B9EB7;
                    font-size: 9pt;
                }}
                .info-row {{ 
                    margin: 5px 0;
                    overflow: hidden;
                }}
                .info-row span {{
                    display: inline-block;
                }}
                .info-row span:first-child {{
                    float: left;
                }}
                .info-row span:last-child {{
                    float: right;
                }}
                .info-label {{ 
                    font-weight: bold;
                    color: #333;
                }}
                h3 {{ 
                    margin: 6px 0; 
                    color: #7B9EB7; 
                    font-size: 11pt; 
                    font-weight: bold;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 12px; 
                    font-size: 9pt;
                }}
                th {{ 
                    background-color: #7B9EB7; 
                    color: white; 
                    padding: 8px 5px;
                    text-align: left; 
                    font-size: 9.5pt;
                    font-weight: bold;
                }}
                td {{ 
                    padding: 6px 5px;
                    border-bottom: 1px solid #ddd;
                    vertical-align: middle;
                }}
                tr:nth-child(even) {{ 
                    background-color: #f9f9f9; 
                }}
                .summary {{ 
                    margin-top: 15px;
                    page-break-inside: avoid;
                }}
                .summary-container {{
                    display: table;
                    width: 100%;
                    table-layout: fixed;
                }}
                .summary-box {{ 
                    display: table-cell;
                    text-align: center; 
                    padding: 10px; 
                    border-left: 4px solid #7B9EB7; 
                    background-color: #f5f5f5;
                    width: 25%;
                }}
                .summary-box:not(:last-child) {{
                    border-right: 1px solid #ddd;
                }}
                .summary-box .title {{ 
                    font-size: 9pt; 
                    margin-bottom: 6px; 
                    font-weight: bold;
                    color: #555;
                }}
                .summary-box .value {{ 
                    font-size: 20pt; 
                    font-weight: bold; 
                    color: #3A9D5A;
                    line-height: 1;
                }}
                .footer {{ 
                    margin-top: 30px; 
                    text-align: center; 
                    font-size: 9pt;
                    page-break-inside: avoid;
                }}
                .footer-signatures {{
                    margin-top: 40px;
                    display: table;
                    width: 100%;
                }}
                .signature-block {{
                    display: table-cell;
                    width: 40%;
                    text-align: center;
                }}
                .signature-block:first-child {{
                    text-align: left;
                }}
                .signature-block:last-child {{
                    text-align: right;
                }}
                .footer-line {{ 
                    display: inline-block; 
                    width: 180px; 
                    border-bottom: 2px solid black;
                    margin-bottom: 5px;
                }}
            </style>
        </head>
        <body>
            <div class="company-info">
                <div><strong>NIT:</strong> xxxx-xxxx-x</div>
                <div><strong>Tel:</strong> (xxx) xxxx-xxxx</div>
            </div>

            <div class="header">
                <h1>Módulo Inventario</h1>
                <h2>REPORTE DE PRODUCTOS</h2>
            </div>

            <div class="info-box">
                <div class="info-row">
                    <span><span class="info-label">Fecha de Emisión:</span> {fecha_actual}</span>
                    <span><span class="info-label">Hora:</span> {hora_actual}</span>
                </div>
                <div class="info-row">
                    <span><span class="info-label">Usuario:</span> Sistema</span>
                    <span><span class="info-label">Reporte No.:</span> INV-{datetime.now().strftime('%Y%m%d-%H%M%S')}</span>
                </div>
            </div>

            <div class="info-box">
                <h3>FILTROS APLICADOS</h3>
                <div class="info-row">
                    <span><span class="info-label">Nombre:</span> {nombre_filtro}</span>
                    <span><span class="info-label">Código:</span> {codigo_filtro}</span>
                </div>
                <div class="info-row">
                    <span><span class="info-label">Categoría:</span> {categoria_filtro}</span>
                    <span><span class="info-label">Proveedor:</span> {proveedor_filtro}</span>
                </div>
                <div class="info-row">
                    <span><span class="info-label">Estado Stock:</span> {stock_filtro}</span>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 7%;">Código</th>
                        <th style="width: 18%;">Nombre</th>
                        <th style="width: 12%;">Categoría</th>
                        <th style="width: 6%;">Stock</th>
                        <th style="width: 6%;">Mín.</th>
                        <th style="width: 9%;">P. Venta</th>
                        <th style="width: 9%;">P. Compra</th>
                        <th style="width: 23%;">Proveedor</th>
                        <th style="width: 10%;">Vencimiento</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Agregar filas de la tabla (omitir columna ID)
        for row in range(self.table.rowCount()):
            html += "<tr>"
            for col in range(1, self.table.columnCount()):  # Empezar desde 1 para omitir ID
                item = self.table.item(row, col)
                texto = item.text() if item else ''
                html += f"<td>{texto}</td>"
            html += "</tr>"

        html += f"""
                </tbody>
            </table>

            <div class="summary">
                <div class="summary-container">
                    <div class="summary-box">
                        <div class="title">Total<br/>Productos</div>
                        <div class="value">{total}</div>
                    </div>
                    <div class="summary-box">
                        <div class="title">Valor<br/>Total</div>
                        <div class="value" style="font-size: 16pt;">{valor}</div>
                    </div>
                    <div class="summary-box">
                        <div class="title">Stock<br/>Bajo</div>
                        <div class="value" style="color: #E53E3E;">{stock_bajo}</div>
                    </div>
                    <div class="summary-box">
                        <div class="title">Por Vencer<br/>(30 días)</div>
                        <div class="value" style="color: #3A9D5A;">{por_vencer}</div>
                    </div>
                </div>
            </div>

            <div class="footer">
                <div class="footer-signatures">
                    <div class="signature-block">
                        <div class="footer-line"></div>
                        <div>Elaborado por</div>
                    </div>
                    <div class="signature-block" style="width: 20%;"></div>
                    <div class="signature-block">
                        <div class="footer-line"></div>
                        <div>Revisado por</div>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """

        return html

    def back_to_main(self):
        """Regresa a la ventana principal."""
        if self.parent_window:
            self.parent_window.show()
        self.close()
from PyQt6.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QWidget, QTableWidget, QMessageBox,
                             QTableWidgetItem, QHeaderView, QFrame, QLineEdit,
                             QGridLayout, QFileDialog)
from PyQt6.QtGui import QPalette, QColor
from PyQt6.QtCore import Qt
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog
from PyQt6.QtGui import QTextDocument
import mysql.connector
from datetime import datetime

from conexion import ConexionBD


class ReportesProveedoresWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setWindowTitle("Módulo de Reportes de Proveedores")
        self.setMinimumSize(1200, 700)

        # Colores del diseño
        self.colores = {
            "fondo": "#F8F9FA",
            "cabecera": "#0B6E4F",
            "texto_principal": "#212529",
            "acento": "#3A9D5A",
            "borde": "#DEE2E6",
            "azul_claro": "#7B9EB7"
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

        # Cargar proveedores al inicio
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
            QLineEdit {{
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

        self.style_summary_box = f"""
            QFrame {{
                background-color: white;
                border-left: 4px solid {self.colores['azul_claro']};
                border-radius: 5px;
                padding: 15px;
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

        title_label = QLabel("Módulo Proveedores - Reportes")
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

        # Primera fila: Nombre y Marca
        lbl_nombre = QLabel("Buscar por Nombre:")
        lbl_nombre.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_nombre, 1, 0)

        self.filtro_nombre = QLineEdit()
        self.filtro_nombre.setPlaceholderText("Nombre del proveedor...")
        self.filtro_nombre.setStyleSheet(self.style_input)
        self.filtro_nombre.setMaximumWidth(200)
        filter_grid.addWidget(self.filtro_nombre, 1, 1)

        lbl_marca = QLabel("Buscar por Marca:")
        lbl_marca.setStyleSheet(label_style)
        filter_grid.addWidget(lbl_marca, 1, 2)

        self.filtro_marca = QLineEdit()
        self.filtro_marca.setPlaceholderText("Marca...")
        self.filtro_marca.setStyleSheet(self.style_input)
        self.filtro_marca.setMaximumWidth(150)
        filter_grid.addWidget(self.filtro_marca, 1, 3)

        # Botones de acción
        btn_filtrar = QPushButton("🔍 Generar Reporte")
        btn_filtrar.setStyleSheet(self.style_primary_button)
        btn_filtrar.clicked.connect(self.generar_reporte)
        btn_filtrar.setMaximumWidth(160)
        filter_grid.addWidget(btn_filtrar, 1, 4)

        btn_limpiar = QPushButton("✨ Limpiar")
        btn_limpiar.setStyleSheet(self.style_header_button)
        btn_limpiar.clicked.connect(self.limpiar_filtros)
        btn_limpiar.setMaximumWidth(100)
        filter_grid.addWidget(btn_limpiar, 1, 5)

        filter_grid.setColumnStretch(6, 1)

        filter_layout.addWidget(filter_frame)
        self.main_layout.addWidget(filter_container)

    def _setup_table(self):
        """Crea la tabla de proveedores."""
        table_container = QWidget()
        table_container.setStyleSheet("margin: 0 15px;")
        table_layout = QVBoxLayout(table_container)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "ID", "Nombre", "Marca Principal", "Teléfono"
        ])

        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)

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

        # Total de Proveedores
        self.summary_total = self._create_summary_box(
            "Total Proveedores", "0", self.colores['azul_claro']
        )

        # Con Teléfono
        self.summary_con_telefono = self._create_summary_box(
            "Con Teléfono", "0", self.colores['azul_claro']
        )

        # Marcas Únicas
        self.summary_marcas = self._create_summary_box(
            "Marcas Diferentes", "0", self.colores['azul_claro']
        )

        # Datos Completos
        self.summary_completos = self._create_summary_box(
            "Datos Completos", "0", self.colores['acento']
        )

        summary_layout.addWidget(self.summary_total)
        summary_layout.addWidget(self.summary_con_telefono)
        summary_layout.addWidget(self.summary_marcas)
        summary_layout.addWidget(self.summary_completos)

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

        btn_imprimir = QPushButton("🖨️ Imprimir Reporte")
        btn_imprimir.setStyleSheet(self.style_primary_button)
        btn_imprimir.clicked.connect(self.imprimir_reporte)

        btn_exportar = QPushButton("📄 Exportar PDF")
        btn_exportar.setStyleSheet(self.style_primary_button)
        btn_exportar.clicked.connect(self.exportar_pdf)

        button_layout.addStretch()
        button_layout.addWidget(btn_imprimir)
        button_layout.addWidget(btn_exportar)

        self.main_layout.addWidget(button_container)

    def limpiar_filtros(self):
        """Limpia todos los filtros."""
        self.filtro_nombre.clear()
        self.filtro_marca.clear()
        self.generar_reporte()

    def generar_reporte(self):
        """Genera el reporte con los filtros aplicados."""
        nombre = self.filtro_nombre.text().strip()
        marca = self.filtro_marca.text().strip()

        self.table.setRowCount(0)

        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)

            # Construir la consulta con filtros
            query = """
                SELECT 
                    id,
                    nombre,
                    marca,
                    telefono
                FROM proveedor
                WHERE activo = 1
            """

            params = []

            if nombre:
                query += " AND nombre LIKE %s"
                params.append(f"%{nombre}%")

            if marca:
                query += " AND marca LIKE %s"
                params.append(f"%{marca}%")

            query += " ORDER BY nombre"

            cursor.execute(query, params)
            proveedores = cursor.fetchall()

            # Llenar la tabla
            self.table.setRowCount(len(proveedores))

            con_telefono = 0
            marcas_unicas = set()
            completos = 0

            for i, prov in enumerate(proveedores):
                self.table.setItem(i, 0, QTableWidgetItem(str(prov['id'])))
                self.table.setItem(i, 1, QTableWidgetItem(prov['nombre'] or ''))
                self.table.setItem(i, 2, QTableWidgetItem(prov['marca'] or ''))

                telefono = prov['telefono'] or ''
                self.table.setItem(i, 3, QTableWidgetItem(telefono))

                # Calcular estadísticas
                if telefono:
                    con_telefono += 1

                if prov['marca']:
                    marcas_unicas.add(prov['marca'])

                # Datos completos = tiene nombre, marca y teléfono
                if prov['nombre'] and prov['marca'] and telefono:
                    completos += 1

            # Actualizar resumen
            total_proveedores = len(proveedores)
            num_marcas = len(marcas_unicas)
            self._actualizar_resumen(total_proveedores, con_telefono, num_marcas, completos)

        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Error al generar reporte: {err}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()

    def _actualizar_resumen(self, total, con_telefono, marcas, completos):
        """Actualiza los valores del panel de resumen."""
        # Total de Proveedores
        valor_label = self.summary_total.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(total))

        # Con Teléfono
        valor_label = self.summary_con_telefono.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(con_telefono))

        # Marcas Únicas
        valor_label = self.summary_marcas.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(marcas))

        # Datos Completos
        valor_label = self.summary_completos.findChild(QLabel, "valor")
        if valor_label:
            valor_label.setText(str(completos))

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
            f"Reporte_Proveedores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
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
        """Genera el HTML del reporte con escala optimizada."""
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        hora_actual = datetime.now().strftime("%H:%M:%S")

        nombre_filtro = self.filtro_nombre.text() or "Todos"
        marca_filtro = self.filtro_marca.text() or "Todas"

        # Obtener resúmenes
        total = self.summary_total.findChild(QLabel, "valor").text()
        con_telefono = self.summary_con_telefono.findChild(QLabel, "valor").text()
        marcas = self.summary_marcas.findChild(QLabel, "valor").text()
        completos = self.summary_completos.findChild(QLabel, "valor").text()

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @page {{ 
                    margin: 15mm 12mm; 
                    size: letter;
                }}
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 0; 
                    padding: 0;
                    font-size: 11pt;
                }}
                .header {{ 
                    text-align: center; 
                    margin-bottom: 20px;
                    border-bottom: 3px solid #7B9EB7;
                    padding-bottom: 15px;
                }}
                .header h1 {{ 
                    font-size: 22pt; 
                    margin: 5px 0; 
                    font-weight: bold;
                    color: #0B6E4F;
                }}
                .header h2 {{ 
                    font-size: 18pt; 
                    margin: 5px 0; 
                    font-weight: bold;
                    color: #333;
                }}
                .company-info {{ 
                    text-align: right; 
                    font-size: 10pt; 
                    color: #666; 
                    margin-bottom: 15px;
                    line-height: 1.4;
                }}
                .info-box {{ 
                    background-color: #f5f5f5; 
                    padding: 12px 15px; 
                    margin-bottom: 15px; 
                    border-left: 4px solid #7B9EB7;
                    font-size: 10pt;
                }}
                .info-row {{ 
                    margin: 6px 0;
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
                    margin: 8px 0; 
                    color: #7B9EB7; 
                    font-size: 12pt; 
                    font-weight: bold;
                }}
                table {{ 
                    width: 100%; 
                    border-collapse: collapse; 
                    margin-top: 15px; 
                    font-size: 10pt;
                }}
                th {{ 
                    background-color: #7B9EB7; 
                    color: white; 
                    padding: 10px 8px;
                    text-align: left; 
                    font-size: 11pt;
                    font-weight: bold;
                }}
                td {{ 
                    padding: 8px;
                    border-bottom: 1px solid #ddd;
                    vertical-align: middle;
                }}
                tr:nth-child(even) {{ 
                    background-color: #f9f9f9; 
                }}
                .summary {{ 
                    margin-top: 20px;
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
                    padding: 12px; 
                    border-left: 4px solid #7B9EB7; 
                    background-color: #f5f5f5;
                    width: 25%;
                }}
                .summary-box:not(:last-child) {{
                    border-right: 1px solid #ddd;
                }}
                .summary-box .title {{ 
                    font-size: 10pt; 
                    margin-bottom: 8px; 
                    font-weight: bold;
                    color: #555;
                }}
                .summary-box .value {{ 
                    font-size: 24pt; 
                    font-weight: bold; 
                    color: #3A9D5A;
                    line-height: 1;
                }}
                .footer {{ 
                    margin-top: 40px; 
                    text-align: center; 
                    font-size: 10pt;
                    page-break-inside: avoid;
                }}
                .footer-signatures {{
                    margin-top: 50px;
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
                    width: 200px; 
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
                <h1>Módulo Proveedores</h1>
                <h2>REPORTE DE PROVEEDORES</h2>
            </div>

            <div class="info-box">
                <div class="info-row">
                    <span><span class="info-label">Fecha de Emisión:</span> {fecha_actual}</span>
                    <span><span class="info-label">Hora:</span> {hora_actual}</span>
                </div>
                <div class="info-row">
                    <span><span class="info-label">Usuario:</span> Sistema</span>
                    <span><span class="info-label">Reporte No.:</span> PROV-{datetime.now().strftime('%Y%m%d-%H%M%S')}</span>
                </div>
            </div>

            <div class="info-box">
                <h3>FILTROS APLICADOS</h3>
                <div class="info-row">
                    <span><span class="info-label">Nombre:</span> {nombre_filtro}</span>
                    <span><span class="info-label">Marca:</span> {marca_filtro}</span>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 8%;">ID</th>
                        <th style="width: 38%;">Nombre</th>
                        <th style="width: 34%;">Marca Principal</th>
                        <th style="width: 20%;">Teléfono</th>
                    </tr>
                </thead>
                <tbody>
        """

        # Agregar filas de la tabla
        for row in range(self.table.rowCount()):
            html += "<tr>"
            for col in range(self.table.columnCount()):
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
                        <div class="title">Total<br/>Proveedores</div>
                        <div class="value">{total}</div>
                    </div>
                    <div class="summary-box">
                        <div class="title">Con<br/>Teléfono</div>
                        <div class="value">{con_telefono}</div>
                    </div>
                    <div class="summary-box">
                        <div class="title">Marcas<br/>Diferentes</div>
                        <div class="value">{marcas}</div>
                    </div>
                    <div class="summary-box">
                        <div class="title">Datos<br/>Completos</div>
                        <div class="value" style="color: #3A9D5A;">{completos}</div>
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
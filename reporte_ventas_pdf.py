from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from datetime import datetime
import mysql.connector
from conexion import ConexionBD



class ReporteVentasPDF:
    """
    Clase para generar reportes de ventas en PDF con diseño profesional
    """

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._crear_estilos_personalizados()

    def _crear_estilos_personalizados(self):
        """Crea estilos personalizados para el documento"""

        # Estilo para el título principal
        self.styles.add(ParagraphStyle(
            name='TituloReporte',
            parent=self.styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#212529'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))

        # Estilo para subtítulos
        self.styles.add(ParagraphStyle(
            name='Subtitulo',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#6C757D'),
            spaceAfter=12,
            alignment=TA_LEFT,
            fontName='Helvetica-Bold'
        ))

        # Estilo para texto normal
        self.styles.add(ParagraphStyle(
            name='TextoNormal',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#212529'),
            alignment=TA_LEFT
        ))

        # Estilo para información de cabecera
        self.styles.add(ParagraphStyle(
            name='InfoCabecera',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#6C757D'),
            alignment=TA_RIGHT
        ))

    def _agregar_encabezado(self, canvas, doc, datos_empresa, numero_reporte):
        """Agrega el encabezado personalizado en cada página"""
        canvas.saveState()

        # Información de la empresa (esquina superior derecha)
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.HexColor('#6C757D'))
        canvas.drawRightString(
            letter[0] - 50,
            letter[1] - 30,
            f"NIT: {datos_empresa.get('nit', 'xxxx-xxxx-x')}"
        )
        canvas.drawRightString(
            letter[0] - 50,
            letter[1] - 45,
            f"Tel: {datos_empresa.get('telefono', '(xxx) xxxx-xxxx')}"
        )

        # Nombre de la empresa (esquina superior izquierda)
        canvas.setFont('Helvetica-Bold', 10)
        canvas.setFillColor(colors.HexColor('#0B6E4F'))
        canvas.drawString(50, letter[1] - 35, datos_empresa.get('nombre', 'XXXXXXXXXXXXXXXXXXXX'))

        #canvas.restoreOverrideCursor()

    def generar_reporte(self, filtros=None, nombre_archivo=None):
        """
        Genera el reporte de ventas en PDF

        Args:
            filtros (dict): Diccionario con filtros de búsqueda
                - fecha_inicio: fecha de inicio del rango
                - fecha_fin: fecha final del rango
                - cliente: nombre del cliente a filtrar
                - usuario: nombre del usuario a filtrar
            nombre_archivo (str): Ruta del archivo PDF a generar

        Returns:
            str: Ruta del archivo generado
        """

        if nombre_archivo is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nombre_archivo = f"reporte_ventas_{timestamp}.pdf"

        # Obtener datos de la base de datos
        ventas_data = self._obtener_datos_ventas(filtros)

        if not ventas_data['ventas']:
            raise ValueError("No se encontraron ventas con los filtros especificados")

        # Crear el documento PDF
        doc = SimpleDocTemplate(
            nombre_archivo,
            pagesize=letter,
            rightMargin=50,
            leftMargin=50,
            topMargin=80,
            bottomMargin=50
        )

        # Contenido del documento
        elementos = []

        # Datos de la empresa (puedes cargarlos desde BD o configuración)
        datos_empresa = {
            'nombre': 'TU EMPRESA S.A.',
            'nit': '1234-5678-9',
            'telefono': '(502) 1234-5678'
        }

        # Título del reporte
        numero_reporte = f"VEN-{datetime.now().strftime('%Y%m')}-{ventas_data['total_ventas']:04d}"
        titulo = Paragraph("REPORTE DE VENTAS", self.styles['TituloReporte'])
        elementos.append(titulo)
        elementos.append(Spacer(1, 0.2 * inch))

        # Información general del reporte
        elementos.extend(self._crear_info_general(ventas_data, numero_reporte))
        elementos.append(Spacer(1, 0.3 * inch))

        # Filtros aplicados
        if filtros:
            elementos.extend(self._crear_seccion_filtros(filtros))
            elementos.append(Spacer(1, 0.2 * inch))

        # Tabla de ventas
        elementos.append(self._crear_tabla_ventas(ventas_data['ventas']))
        elementos.append(Spacer(1, 0.3 * inch))

        # Resumen estadístico
        elementos.extend(self._crear_resumen_estadistico(ventas_data))
        elementos.append(Spacer(1, 0.5 * inch))

        # Firmas
        elementos.extend(self._crear_seccion_firmas())

        # Construir el PDF con encabezado personalizado
        doc.build(
            elementos,
            onFirstPage=lambda c, d: self._agregar_encabezado(c, d, datos_empresa, numero_reporte),
            onLaterPages=lambda c, d: self._agregar_encabezado(c, d, datos_empresa, numero_reporte)
        )

        return nombre_archivo

    def _obtener_datos_ventas(self, filtros):
        """Obtiene los datos de ventas desde la base de datos"""
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)

            # Query principal
            query = """
            SELECT 
                v.id,
                v.fechaVenta as fecha,
                v.total,
                COALESCE(CONCAT(c.nombre, ' ', c.apellido), 'Consumidor Final') as cliente,
                COALESCE(CONCAT(u.nombre, ' ', u.apellido), 'Sistema') as usuario,
                v.cliente_id,
                v.usuario_id
            FROM ventas v
            LEFT JOIN cliente c ON v.cliente_id = c.id
            LEFT JOIN usuario u ON v.usuario_id = u.id
            WHERE 1=1
            """

            params = []

            if filtros:
                if filtros.get('fecha_inicio'):
                    query += " AND DATE(v.fechaVenta) >= %s"
                    params.append(filtros['fecha_inicio'])

                if filtros.get('fecha_fin'):
                    query += " AND DATE(v.fechaVenta) <= %s"
                    params.append(filtros['fecha_fin'])

                if filtros.get('cliente'):
                    query += " AND (c.nombre LIKE %s OR c.apellido LIKE %s)"
                    params.extend([f"%{filtros['cliente']}%", f"%{filtros['cliente']}%"])

                if filtros.get('usuario'):
                    query += " AND (u.nombre LIKE %s OR u.apellido LIKE %s)"
                    params.extend([f"%{filtros['usuario']}%", f"%{filtros['usuario']}%"])

            query += " ORDER BY v.fechaVenta DESC, v.id DESC"

            cursor.execute(query, params)
            ventas = cursor.fetchall()

            # Obtener cantidad de productos por venta
            for venta in ventas:
                cursor.execute("""
                    SELECT COUNT(*) as total_productos
                    FROM detalle_venta
                    WHERE ventas_id = %s
                """, (venta['id'],))

                result = cursor.fetchone()
                venta['total_productos'] = result['total_productos'] if result else 0

            # Calcular estadísticas
            total_facturado = sum(float(v['total']) for v in ventas)
            total_productos_vendidos = sum(v['total_productos'] for v in ventas)
            venta_promedio = total_facturado / len(ventas) if ventas else 0

            cursor.close()
            conexion.close()

            return {
                'ventas': ventas,
                'total_ventas': len(ventas),
                'total_facturado': total_facturado,
                'total_productos': total_productos_vendidos,
                'venta_promedio': venta_promedio
            }

        except mysql.connector.Error as error:
            raise Exception(f"Error al obtener datos: {error}")

    def _crear_info_general(self, ventas_data, numero_reporte):
        """Crea la sección de información general del reporte"""
        elementos = []

        # Crear tabla para información general (2 columnas)
        fecha_emision = datetime.now().strftime("%d/%m/%Y")
        hora_emision = datetime.now().strftime("%H:%M:%S")
        usuario_actual = "xxxxxxxxxxxxxxxxxxxxx"  # Obtener del sistema de login

        info_data = [
            ['Fecha de Emisión:', fecha_emision, 'Hora:', hora_emision],
            ['Usuario:', usuario_actual, 'Reporte No.:', numero_reporte]
        ]

        info_table = Table(info_data, colWidths=[1.5 * inch, 2 * inch, 1 * inch, 1.5 * inch])
        info_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
            ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
            ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#212529')),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        elementos.append(info_table)

        return elementos

    def _crear_seccion_filtros(self, filtros):
        """Crea la sección de filtros aplicados"""
        elementos = []

        # Título de la sección
        titulo = Paragraph("FILTROS APLICADOS", self.styles['Subtitulo'])
        elementos.append(titulo)

        # Crear tabla de filtros
        filtros_data = []

        if filtros.get('fecha_inicio') and filtros.get('fecha_fin'):
            filtros_data.append([
                'Fecha Desde:',
                filtros['fecha_inicio'],
                'Fecha Hasta:',
                filtros['fecha_fin']
            ])

        if filtros.get('cliente'):
            filtros_data.append([
                'Cliente:',
                filtros['cliente'],
                '',
                ''
            ])

        if filtros.get('usuario'):
            filtros_data.append([
                'Usuario:',
                filtros['usuario'],
                '',
                ''
            ])

        if filtros_data:
            filtros_table = Table(filtros_data, colWidths=[1.5 * inch, 2.5 * inch, 1.5 * inch, 2.5 * inch])
            filtros_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 9),
                ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 9),
                ('FONT', (2, 0), (2, -1), 'Helvetica-Bold', 9),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#495057')),
                ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (2, 0), (2, -1), 'RIGHT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('LEFTPADDING', (0, 0), (-1, -1), 10),
                ('RIGHTPADDING', (0, 0), (-1, -1), 10),
            ]))

            elementos.append(filtros_table)

        return elementos

    def _crear_tabla_ventas(self, ventas):
        """Crea la tabla principal de ventas"""

        # Encabezados de la tabla
        headers = ['ID Venta', 'Fecha/Hora', 'Cliente', 'Usuario', 'Total', 'Productos']
        data = [headers]

        # Agregar datos de ventas
        for venta in ventas:
            fecha_formateada = venta['fecha'].strftime('%d/%m/%Y %H:%M')
            total_formateado = f"Q{float(venta['total']):,.2f}"

            fila = [
                str(venta['id']),
                fecha_formateada,
                venta['cliente'][:25] + '...' if len(venta['cliente']) > 25 else venta['cliente'],
                venta['usuario'][:20] + '...' if len(venta['usuario']) > 20 else venta['usuario'],
                total_formateado,
                str(venta['total_productos'])
            ]
            data.append(fila)

        # Crear tabla con anchos proporcionales
        tabla = Table(data, colWidths=[0.7 * inch, 1.3 * inch, 1.8 * inch, 1.5 * inch, 1 * inch, 0.7 * inch])

        # Aplicar estilos
        tabla.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7B92AA')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),

            # Contenido
            ('FONT', (0, 1), (-1, -1), 'Helvetica', 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.HexColor('#212529')),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # ID centrado
            ('ALIGN', (4, 1), (5, -1), 'RIGHT'),  # Total y Productos a la derecha
            ('VALIGN', (0, 1), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),

            # Bordes y líneas
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#DEE2E6')),
            ('LINEBELOW', (0, 0), (-1, 0), 2, colors.HexColor('#0B6E4F')),

            # Alternar colores de filas
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8F9FA')]),
        ]))

        return tabla

    def _crear_resumen_estadistico(self, ventas_data):
        """Crea la sección de resumen estadístico"""
        elementos = []

        # Crear tabla con 4 columnas para las estadísticas
        stats_data = [[
            'Total de Ventas',
            'Productos Vendidos',
            'Venta Promedio',
            'Total Facturado'
        ], [
            str(ventas_data['total_ventas']),
            str(ventas_data['total_productos']),
            f"Q{ventas_data['venta_promedio']:,.2f}",
            f"Q{ventas_data['total_facturado']:,.2f}"
        ]]

        stats_table = Table(stats_data, colWidths=[2 * inch, 2 * inch, 2 * inch, 2 * inch])
        stats_table.setStyle(TableStyle([
            # Encabezados
            ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 10),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#495057')),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Valores
            ('FONT', (0, 1), (2, 1), 'Helvetica-Bold', 16),
            ('FONT', (3, 1), (3, 1), 'Helvetica-Bold', 18),
            ('TEXTCOLOR', (0, 1), (2, 1), colors.HexColor('#7B92AA')),
            ('TEXTCOLOR', (3, 1), (3, 1), colors.HexColor('#27AE60')),
            ('ALIGN', (0, 1), (-1, 1), 'CENTER'),
            ('TOPPADDING', (0, 1), (-1, 1), 15),
            ('BOTTOMPADDING', (0, 1), (-1, 1), 15),

            # Bordes y fondos
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#DEE2E6')),
            ('LINEAFTER', (0, 0), (2, -1), 1, colors.HexColor('#DEE2E6')),
            ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ]))

        elementos.append(stats_table)

        return elementos

    def _crear_seccion_firmas(self):
        """Crea la sección de firmas"""
        elementos = []

        # Crear tabla para las firmas
        firma_data = [
            ['_' * 40, '_' * 40],
            ['Elaborado por', 'Revisado por']
        ]

        firma_table = Table(firma_data, colWidths=[3.5 * inch, 3.5 * inch])
        firma_table.setStyle(TableStyle([
            ('FONT', (0, 0), (-1, 0), 'Helvetica', 1),
            ('FONT', (0, 1), (-1, 1), 'Helvetica', 10),
            ('TEXTCOLOR', (0, 1), (-1, 1), colors.HexColor('#495057')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 1), (-1, 1), 5),
        ]))

        elementos.append(firma_table)

        return elementos


# Función auxiliar para integrar con VentasWindow
def generar_reporte_ventas_pdf(filtros=None, nombre_archivo=None):
    """
    Función de conveniencia para generar el reporte

    Args:
        filtros: Diccionario con los filtros aplicados
        nombre_archivo: Nombre del archivo PDF (opcional)

    Returns:
        str: Ruta del archivo generado
    """
    try:
        generador = ReporteVentasPDF()
        archivo = generador.generar_reporte(filtros, nombre_archivo)
        return archivo
    except Exception as e:
        raise Exception(f"Error al generar reporte: {str(e)}")


# Ejemplo de uso
if __name__ == "__main__":
    # Ejemplo 1: Reporte sin filtros
    try:
        archivo = generar_reporte_ventas_pdf()
        print(f"Reporte generado: {archivo}")
    except Exception as e:
        print(f"Error: {e}")

    # Ejemplo 2: Reporte con filtros
    try:
        filtros = {
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31',
            'cliente': 'García'
        }
        archivo = generar_reporte_ventas_pdf(filtros, "reporte_enero_2024.pdf")
        print(f"Reporte filtrado generado: {archivo}")
    except Exception as e:
        print(f"Error: {e}")
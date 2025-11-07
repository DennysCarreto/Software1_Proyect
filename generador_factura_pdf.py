from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
from conexion import ConexionBD
import mysql.connector


def generar_factura_venta_pdf(venta_id, nombre_archivo):
    """
    Genera una factura en PDF para una venta específica

    Args:
        venta_id: ID de la venta
        nombre_archivo: Ruta donde se guardará el PDF

    Returns:
        str: Ruta del archivo generado
    """
    try:
        # Obtener datos de la venta
        conexion = ConexionBD.obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Consulta principal de la venta
        cursor.execute("""
            SELECT 
                v.id,
                v.fechaVenta,
                v.total,
                COALESCE(CONCAT(c.nombre, ' ', c.apellido), 'Consumidor Final') as cliente_nombre,
                c.nit as cliente_nit,
                c.telefono as cliente_telefono,
                CONCAT(u.nombre, ' ', u.apellido) as vendedor
            FROM ventas v
            LEFT JOIN cliente c ON v.cliente_id = c.id
            LEFT JOIN usuario u ON v.usuario_id = u.id
            WHERE v.id = %s
        """, (venta_id,))

        venta = cursor.fetchone()

        if not venta:
            raise ValueError(f"No se encontró la venta con ID {venta_id}")

        # Obtener detalles de productos
        cursor.execute("""
            SELECT 
                p.codigo,
                p.nombre,
                cat.nombre_categoria as categoria,
                dv.cantidad,
                dv.precio_unitario,
                dv.subtotal
            FROM detalle_venta dv
            JOIN producto p ON dv.producto_id = p.id
            LEFT JOIN categoria cat ON p.categoria_id = cat.id
            WHERE dv.ventas_id = %s
            ORDER BY p.nombre
        """, (venta_id,))

        detalles = cursor.fetchall()
        cursor.close()
        conexion.close()

        # Crear el PDF
        doc = SimpleDocTemplate(nombre_archivo, pagesize=letter)
        elementos = []
        styles = getSampleStyleSheet()

        # Estilos personalizados
        estilo_titulo = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#000000'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        estilo_subtitulo = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#000000'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )

        estilo_info = ParagraphStyle(
            'Info',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#333333'),
            alignment=TA_RIGHT
        )

        estilo_normal = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#000000')
        )

        # ===== ENCABEZADO =====
        titulo = Paragraph("FARMAPLUS", estilo_titulo)
        elementos.append(titulo)

        # Información de la empresa
        info_empresa = [
            ["NIT: 1234-567890-123-4"],
            ["Tel: (502) 1234-5678"],
            ["Mazatenango, Suchitepéquez"]
        ]

        tabla_empresa = Table(info_empresa, colWidths=[6 * inch])
        tabla_empresa.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
        ]))
        elementos.append(tabla_empresa)
        elementos.append(Spacer(1, 0.3 * inch))

        # ===== TÍTULO FACTURA =====
        subtitulo = Paragraph("FACTURA DE VENTA", estilo_subtitulo)
        elementos.append(subtitulo)
        elementos.append(Spacer(1, 0.2 * inch))

        # ===== INFORMACIÓN DE LA VENTA =====
        fecha_formateada = venta['fechaVenta'].strftime('%d/%m/%Y')
        hora_formateada = venta['fechaVenta'].strftime('%H:%M')
        factura_numero = f"FAC-{venta['fechaVenta'].strftime('%Y%m%d')}-{venta['id']}"

        info_venta_data = [
            ["Fecha de Emisión:", fecha_formateada, "Hora:", hora_formateada],
            ["Vendedor:", venta['vendedor'], "Factura No.:", factura_numero],
            ["Cliente:", venta['cliente_nombre'], "", ""]
        ]

        tabla_info = Table(info_venta_data, colWidths=[1.2 * inch, 2 * inch, 1 * inch, 2.3 * inch])
        tabla_info.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#000000')),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elementos.append(tabla_info)
        elementos.append(Spacer(1, 0.3 * inch))

        # ===== DETALLE DE PRODUCTOS =====
        detalle_titulo = Paragraph("DETALLE DE PRODUCTOS", estilo_subtitulo)
        elementos.append(detalle_titulo)
        elementos.append(Spacer(1, 0.15 * inch))

        # Encabezado de la tabla de productos
        datos_productos = [['Código', 'Producto', 'Categoría', 'Cant.', 'Precio Unit.']]

        # Agregar productos
        for detalle in detalles:
            datos_productos.append([
                detalle.get('codigo', 'N/A'),
                detalle['nombre'],
                detalle.get('categoria', 'Sin categoría'),
                str(detalle['cantidad']),
                f"Q{float(detalle['precio_unitario']):.2f}"
            ])

        tabla_productos = Table(datos_productos, colWidths=[0.9 * inch, 2.2 * inch, 1.3 * inch, 0.7 * inch, 1.2 * inch])
        tabla_productos.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0B6E4F')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Contenido
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Código
            ('ALIGN', (1, 1), (2, -1), 'LEFT'),  # Producto y categoría
            ('ALIGN', (3, 1), (-1, -1), 'CENTER'),  # Cantidad y precio
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        elementos.append(tabla_productos)
        elementos.append(Spacer(1, 0.3 * inch))

        # ===== TOTALES =====
        subtotal = sum(float(d['subtotal']) for d in detalles)
        descuento = 0.00
        iva = 0.00
        total = float(venta['total'])

        datos_totales = [
            ["Subtotal", f"Q{subtotal:.2f}"],
            ["Descuento", f"{descuento:.2f}"],
            ["IVA", f"{iva:.2f}"],
            ["Total a Pagar", f"Q{total:.2f}"]
        ]

        tabla_totales = Table(datos_totales, colWidths=[4.8 * inch, 1.5 * inch])
        tabla_totales.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (-1, 2), 'Helvetica'),
            ('FONTNAME', (0, 3), (-1, 3), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 2), 10),
            ('FONTSIZE', (0, 3), (-1, 3), 12),
            ('TEXTCOLOR', (0, 0), (-1, 2), colors.HexColor('#333333')),
            ('TEXTCOLOR', (0, 3), (-1, 3), colors.HexColor('#000000')),
            ('LINEABOVE', (0, 3), (-1, 3), 1.5, colors.HexColor('#000000')),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elementos.append(tabla_totales)
        elementos.append(Spacer(1, 0.3 * inch))

        # ===== PIE DE PÁGINA =====
        metodo_pago = Paragraph("Método de pago: Efectivo", estilo_normal)
        elementos.append(metodo_pago)
        elementos.append(Spacer(1, 0.1 * inch))

        observaciones = Paragraph("Observaciones: No se aceptan devoluciones sin factura.", estilo_normal)
        elementos.append(observaciones)
        elementos.append(Spacer(1, 0.4 * inch))

        # Mensaje de agradecimiento
        estilo_gracias = ParagraphStyle(
            'Gracias',
            parent=styles['Normal'],
            fontSize=14,
            textColor=colors.HexColor('#000000'),
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        gracias = Paragraph("¡Gracias por su compra!", estilo_gracias)
        elementos.append(gracias)

        # Generar el PDF
        doc.build(elementos)
        return nombre_archivo

    except mysql.connector.Error as error:
        raise Exception(f"Error de base de datos: {error}")
    except Exception as e:
        raise Exception(f"Error al generar factura: {e}")
from conexion import ConexionBD
from datetime import datetime, timedelta
import mysql.connector

class DashboardDataAccess:
    """Clase para manejar todas las consultas de Business Intelligence (BI)."""
    
    def __init__(self):
        # El manager solo usa métodos estáticos o de clase para acceder a la BD
        pass

    @staticmethod
    def get_kpis_resumen():
        """Obtiene el estado actual de los indicadores clave."""
        kpis = {
            'ventas_dia': 0.0,
            'productos_criticos': 0,
            'proximos_a_vencer': 0,
            'top_cliente': 'N/A'
        }
        
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            hoy_str = datetime.now().strftime('%Y-%m-%d')
            
            # 1. Ventas del Día
            cursor.execute(f"SELECT SUM(total) as total_dia FROM ventas WHERE DATE(fechaVenta) = '{hoy_str}'")
            kpis['ventas_dia'] = cursor.fetchone()['total_dia'] or 0.0

            # 2. Productos Críticos (Stock Actual <= Stock Mínimo)
            cursor.execute("SELECT COUNT(id) as count FROM producto WHERE stockActual <= stockMinimo AND stockActual > 0")
            kpis['productos_criticos'] = cursor.fetchone()['count']

            # 3. Próximos a Vencer (30 días)
            fecha_limite = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
            cursor.execute("SELECT COUNT(id) as count FROM producto WHERE fVencimiento BETWEEN CURDATE() AND %s", (fecha_limite,))
            kpis['proximos_a_vencer'] = cursor.fetchone()['count']

            # 4. Top Cliente (Últimos 30 días)
            cursor.execute("""
                SELECT 
                    CONCAT(c.nombre, ' ', c.apellido) as cliente_nombre, SUM(v.total) as gasto_total
                FROM ventas v
                JOIN cliente c ON v.cliente_id = c.id
                WHERE v.fechaVenta >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) AND c.activo = 1
                GROUP BY v.cliente_id
                ORDER BY gasto_total DESC
                LIMIT 1
            """)
            top_client = cursor.fetchone()
            if top_client:
                kpis['top_cliente'] = top_client['cliente_nombre']

        except Exception as e:
            print(f"Error al cargar KPIs: {e}")
        finally:
            if 'conexion' in locals() and conexion.is_connected():
                cursor.close()
                conexion.close()
        
        return kpis

    @staticmethod
    def get_ventas_por_mes():
        """Obtiene el total de ventas por mes para un gráfico de tendencia."""
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    DATE_FORMAT(fechaVenta, '%Y-%m') as mes_anio,
                    SUM(total) as ventas_mensuales
                FROM ventas
                WHERE fechaVenta >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY mes_anio
                ORDER BY mes_anio
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al cargar ventas mensuales: {e}")
            return []

    @staticmethod
    def get_top_productos_vendidos():
        """Obtiene el top 5 de productos más vendidos (por cantidad) en los últimos 30 días."""
        try:
            conexion = ConexionBD.obtener_conexion()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT 
                    p.nombre as producto_nombre, SUM(dv.cantidad) as cantidad_vendida
                FROM detalle_venta dv
                JOIN ventas v ON dv.ventas_id = v.id
                JOIN producto p ON dv.producto_id = p.id
                WHERE v.fechaVenta >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY p.nombre
                ORDER BY cantidad_vendida DESC
                LIMIT 5
            """)
            return cursor.fetchall()
        except Exception as e:
            print(f"Error al cargar top productos: {e}")
            return []
# notification_manager.py
from datetime import datetime, timedelta
from conexion import ConexionBD

def get_inventory_alerts():
    """Busca y devuelve únicamente las alertas de inventario."""
    alerts = []
    try:
        conexion = ConexionBD.obtener_conexion()
        cursor = conexion.cursor(dictionary=True)

        # Alertas de stock bajo
        q_stock = "SELECT nombre, stockActual, stockMinimo FROM producto WHERE stockActual <= stockMinimo AND stockActual > 0"
        cursor.execute(q_stock)
        for item in cursor.fetchall():
            item['type'] = 'inventory_stock' # Añadimos un tipo para identificarla
            alerts.append(item)

        # Alertas de vencimiento
        dias_vencer = 30
        fecha_limite = (datetime.now() + timedelta(days=dias_vencer)).strftime('%Y-%m-%d')
        q_vencimiento = "SELECT nombre, fVencimiento FROM producto WHERE fVencimiento BETWEEN CURDATE() AND %s"
        cursor.execute(q_vencimiento, (fecha_limite,))
        for item in cursor.fetchall():
            item['type'] = 'inventory_expiry' # Otro tipo
            alerts.append(item)
            
        cursor.close()
    except Exception as e:
        print(f"Error al obtener alertas de inventario: {e}")
    
    return alerts

def get_all_notifications():
    """
    Función central que recolecta todas las notificaciones del sistema.
    Actualmente solo incluye las de inventario, pero se puede expandir fácilmente.
    """
    all_notifications = []
    
    #  llamamos a las de inventario
    all_notifications.extend(get_inventory_alerts())
    
    # --- FUTURO ---
    #  notificaciones de proveedores, solo tendrías que añadir:
    # all_notifications.extend(get_provider_alerts())
    
    # notificaciones de ventas, solo tendrías que añadir:
    # all_notifications.extend(get_sales_alerts())
    
    return all_notifications
# conexion.py
import mysql.connector
from mysql.connector import Error

class ConexionBD:
    _conexion = None

    @staticmethod
    def obtener_conexion():
        if ConexionBD._conexion is None or not ConexionBD._conexion.is_connected():
            try:
                ConexionBD._conexion = mysql.connector.connect(
                    host='localhost',
                    user='root',
                    password='admin',
                    database='farmaPlus'
                )
                print("✅ Conexión establecida.")
            except Error as e:
                print(f"❌ Error al conectar: {e}")
                ConexionBD._conexion = None
        return ConexionBD._conexion

    @staticmethod
    def cerrar_conexion():
        if ConexionBD._conexion and ConexionBD._conexion.is_connected():
            ConexionBD._conexion.close()
            print("🔌 Conexión cerrada.")
            ConexionBD._conexion = None

# """ Probar si la conexion es exitosa"""
# if __name__ == "__main__":
#     conexion = ConexionBD.obtener_conexion()
#     if conexion and conexion.is_connected():
#         print("Exitoso")
#         input('Press enter to continue...')
#     else: print("Fallida")

#     ConexionBD.cerrar_conexion()
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QFontDatabase
from login import LoginWindow
from login import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Farma PLUS")
    app.setOrganizationName("Farma PLUS")    
    # Icono a la aplicación
    # app.setWindowIcon(QIcon("icon.png"))
    
    # Iniciar ventana de login
    login = LoginWindow()
    login.show()
    
    sys.exit(app.exec())
    

if __name__ == "__main__":
    main()
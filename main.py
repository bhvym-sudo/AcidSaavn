from ui.gui import AcidSaavnGUI
import sys
from PyQt5.QtWidgets import QApplication

try:
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = AcidSaavnGUI()
    window.show()
    
    app.exec_()
    
except Exception as e:
    print(f"Application error: {e}")

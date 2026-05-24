import sys

from PySide6.QtWidgets import QApplication

from login import LoginWindow
from database import setup_database


# ================= CREATE APP =================
app = QApplication(sys.argv)

# ================= SETUP DATABASE =================
setup_database()

# ================= OPEN LOGIN =================
window = LoginWindow()
window.show()

# ================= RUN APP =================
sys.exit(app.exec())
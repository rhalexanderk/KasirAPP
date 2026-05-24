from PySide6.QtWidgets import *
from PySide6.QtCore import Qt

from dashboard import Dashboard
from database import connect


class LoginWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Login Kasir")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # ================= TITLE =================
        title = QLabel("LOGIN KASIR")

        title.setAlignment(Qt.AlignCenter)

        title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        # ================= USERNAME =================
        self.username = QLineEdit()

        self.username.setPlaceholderText(
            "Username"
        )

        layout.addWidget(self.username)

        # ================= PASSWORD =================
        self.password = QLineEdit()

        self.password.setPlaceholderText(
            "Password"
        )

        self.password.setEchoMode(
            QLineEdit.Password
        )

        # ENTER = LOGIN
        self.password.returnPressed.connect(
            self.login
        )

        layout.addWidget(self.password)

        # ================= BUTTON =================
        btn_login = QPushButton("Login")

        btn_login.clicked.connect(
            self.login
        )

        layout.addWidget(btn_login)

        layout.addStretch()

        self.setLayout(layout)

    # ================= LOGIN =================
    def login(self):

        username = self.username.text()
        password = self.password.text()

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT username, role
        FROM users
        WHERE username = ?
        AND password = ?
        """, (
            username,
            password
        ))

        user = cur.fetchone()

        conn.close()

        if user:

            role = user[1]

            self.dashboard = Dashboard(
                username,
                role
            )

            self.dashboard.show()

            self.close()

        else:

            QMessageBox.warning(
                self,
                "Error",
                "Username / Password salah"
            )
from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QTimer

from products import ProductWindow
from transaction import TransactionWindow
from report import ReportWindow
from database import connect
from users import UserWindow


class Dashboard(QMainWindow):

    def __init__(self, username, role):
        super().__init__()

        self.username = username
        self.role = role

        self.setWindowTitle("Aplikasi Kasir")
        self.resize(1200, 700)

        # ================= CENTRAL =================
        central = QWidget()

        self.setCentralWidget(central)

        main_layout = QHBoxLayout()

        central.setLayout(main_layout)

        # ================= SIDEBAR =================
        sidebar = QFrame()

        sidebar.setFixedWidth(230)

        sidebar.setStyleSheet("""
            background-color: #2c3e50;
            color: white;
        """)

        sidebar_layout = QVBoxLayout()

        # ================= TITLE =================
        title_sidebar = QLabel("WARUNG")

        title_sidebar.setAlignment(Qt.AlignCenter)

        title_sidebar.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            padding: 20px;
        """)

        sidebar_layout.addWidget(title_sidebar)

        # ================= USER INFO =================
        user_info = QLabel(f"""
User : {self.username}
Role : {self.role}
        """)

        user_info.setStyleSheet("""
            padding: 10px;
            font-size: 14px;
            color: #ecf0f1;
        """)

        sidebar_layout.addWidget(user_info)

        # ================= BUTTON =================
        btn_dashboard = QPushButton("Dashboard")
        btn_users = QPushButton("Manajemen User")
        btn_barang = QPushButton("Data Barang")
        btn_transaksi = QPushButton("Transaksi")
        btn_report = QPushButton("Laporan")
        btn_logout = QPushButton("Logout")

        buttons = [
            btn_dashboard,
            btn_users,
            btn_barang,
            btn_transaksi,
            btn_report,
            btn_logout
        ]

        # ================= ROLE ACCESS =================
        if self.role == "kasir":

            btn_barang.hide()
            btn_report.hide()

        elif self.role == "gudang":

            btn_transaksi.hide()
            btn_report.hide()

        if self.role != "owner":

            btn_users.hide()

        # ================= STYLE BUTTON =================
        for btn in buttons:

            btn.setFixedHeight(45)

            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    border: none;
                    color: white;
                    text-align: left;
                    padding-left: 15px;
                    font-size: 16px;
                    border-radius: 5px;
                }

                QPushButton:hover {
                    background-color: #1abc9c;
                }
            """)

            sidebar_layout.addWidget(btn)

        sidebar_layout.addStretch()

        sidebar.setLayout(sidebar_layout)

        # ================= CONTENT =================
        self.content = QWidget()

        self.content.setStyleSheet("""
            background-color: #ecf0f1;
        """)

        content_layout = QVBoxLayout()

        # ================= TITLE =================
        title = QLabel("Dashboard Kasir")

        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)

        content_layout.addWidget(title)

        # ================= CARD SECTION =================
        cards_layout = QHBoxLayout()

        self.card_barang = self.create_card(
            "Total Barang",
            "0"
        )

        self.card_transaksi = self.create_card(
            "Total Transaksi",
            "0"
        )

        self.card_omzet = self.create_card(
            "Total Pendapatan",
            "Rp 0"
        )

        cards_layout.addWidget(self.card_barang)
        cards_layout.addWidget(self.card_transaksi)
        cards_layout.addWidget(self.card_omzet)

        content_layout.addLayout(cards_layout)

        # ================= INFO =================
        info = QLabel(f"""
Selamat datang {self.username}

Role Anda : {self.role}
        """)

        info.setStyleSheet("""
            font-size: 16px;
            color: #2c3e50;
            padding-top: 20px;
        """)

        content_layout.addWidget(info)

        content_layout.addStretch()

        self.content.setLayout(content_layout)

        # ================= ADD TO MAIN =================
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.content)

        # ================= EVENT =================
        btn_users.clicked.connect(
            self.open_users
        )

        btn_barang.clicked.connect(
            self.open_products
        )

        btn_transaksi.clicked.connect(
            self.open_transaction
        )

        btn_report.clicked.connect(
            self.open_report
        )

        btn_logout.clicked.connect(
            self.logout
        )

        # ================= LOAD DATA =================
        self.load_dashboard_data()

        # ================= AUTO REFRESH =================
        self.timer = QTimer()

        self.timer.timeout.connect(
            self.load_dashboard_data
        )

        self.timer.start(2000)

    # ================= CREATE CARD =================
    def create_card(self, title, value):

        card = QFrame()

        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 15px;
                border: 1px solid #dcdcdc;
            }
        """)

        card.setMinimumHeight(170)

        layout = QVBoxLayout()

        layout.setContentsMargins(20, 20, 20, 20)

        # ================= TITLE =================
        title_label = QLabel(title)

        title_label.setStyleSheet("""
            font-size: 18px;
            color: gray;
            border: none;
            background: transparent;
        """)

        # ================= VALUE =================
        value_label = QLabel(value)

        value_label.setAlignment(Qt.AlignCenter)

        value_label.setStyleSheet("""
            font-size: 42px;
            font-weight: bold;
            color: #2c3e50;
            border: none;
            background: transparent;
        """)

        # save label reference
        card.value_label = value_label

        layout.addWidget(title_label)

        layout.addStretch()

        layout.addWidget(value_label)

        layout.addStretch()

        card.setLayout(layout)

        return card

    # ================= LOAD DASHBOARD =================
    def load_dashboard_data(self):

        try:

            conn = connect()

            cur = conn.cursor()

            # ================= TOTAL BARANG =================
            cur.execute("""
            SELECT COUNT(*)
            FROM products
            """)

            total_barang = cur.fetchone()[0]

            # ================= TOTAL TRANSAKSI =================
            cur.execute("""
            SELECT COUNT(*)
            FROM transactions
            """)

            total_transaksi = cur.fetchone()[0]

            # ================= TOTAL OMZET =================
            cur.execute("""
            SELECT COALESCE(SUM(total), 0)
            FROM transactions
            """)

            omzet = cur.fetchone()[0]

            conn.close()

            # ================= UPDATE CARD =================
            self.card_barang.value_label.setText(
                str(total_barang)
            )

            self.card_transaksi.value_label.setText(
                str(total_transaksi)
            )

            self.card_omzet.value_label.setText(
                f"Rp {omzet:,}"
            )

        except Exception as e:

            print("ERROR DASHBOARD:", e)

    # ================= OPEN USERS =================
    def open_users(self):

        if self.role != "owner":

            QMessageBox.warning(
                self,
                "Akses Ditolak",
                "Hanya owner yang bisa membuka menu user"
            )

            return

        self.users = UserWindow()

        self.users.show()

    # ================= OPEN PRODUCTS =================
    def open_products(self):

        if self.role not in ["owner", "gudang"]:

            QMessageBox.warning(
                self,
                "Akses Ditolak",
                "Anda tidak punya akses ke Data Barang"
            )

            return

        self.products = ProductWindow()

        self.products.show()

    # ================= OPEN TRANSACTION =================
    def open_transaction(self):

        if self.role not in ["owner", "kasir"]:

            QMessageBox.warning(
                self,
                "Akses Ditolak",
                "Anda tidak punya akses ke Transaksi"
            )

            return

        self.transaction = TransactionWindow()

        self.transaction.show()

    # ================= OPEN REPORT =================
    def open_report(self):

        if self.role != "owner":

            QMessageBox.warning(
                self,
                "Akses Ditolak",
                "Hanya owner yang bisa membuka laporan"
            )

            return

        self.report = ReportWindow()

        self.report.show()

    # ================= LOGOUT =================
    def logout(self):

        reply = QMessageBox.question(
            self,
            "Logout",
            "Yakin ingin logout?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            self.close()
from PySide6.QtWidgets import *
from database import connect


class UserWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.selected_id = None

        self.setWindowTitle("Manajemen User")

        self.resize(700, 500)

        layout = QVBoxLayout()

        # ================= FORM =================
        form = QFormLayout()

        self.username_input = QLineEdit()

        self.password_input = QLineEdit()

        self.role_combo = QComboBox()

        self.role_combo.addItems([
            "owner",
            "kasir",
            "gudang"
        ])

        form.addRow("Username", self.username_input)
        form.addRow("Password", self.password_input)
        form.addRow("Role", self.role_combo)

        layout.addLayout(form)

        # ================= BUTTON =================
        btn_layout = QHBoxLayout()

        self.btn_add = QPushButton("Tambah")
        self.btn_update = QPushButton("Update")
        self.btn_delete = QPushButton("Hapus")

        self.btn_add.clicked.connect(
            self.add_user
        )

        self.btn_update.clicked.connect(
            self.update_user
        )

        self.btn_delete.clicked.connect(
            self.delete_user
        )

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_update)
        btn_layout.addWidget(self.btn_delete)

        layout.addLayout(btn_layout)

        # ================= TABLE =================
        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Username",
            "Password",
            "Role"
        ])

        self.table.cellClicked.connect(
            self.select_row
        )

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    # ================= LOAD DATA =================
    def load_data(self):

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM users
        """)

        rows = cur.fetchall()

        conn.close()

        self.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):

            for col_index, data in enumerate(row_data):

                self.table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(data))
                )

    # ================= CLEAR =================
    def clear_form(self):

        self.username_input.clear()

        self.password_input.clear()

        self.role_combo.setCurrentIndex(0)

    # ================= ADD USER =================
    def add_user(self):

        username = self.username_input.text()

        password = self.password_input.text()

        role = self.role_combo.currentText()

        if username == "" or password == "":

            QMessageBox.warning(
                self,
                "Error",
                "Semua field wajib diisi"
            )

            return

        conn = connect()

        cur = conn.cursor()

        try:

            cur.execute("""
            INSERT INTO users
            (username, password, role)
            VALUES (?, ?, ?)
            """, (
                username,
                password,
                role
            ))

            conn.commit()

            QMessageBox.information(
                self,
                "Sukses",
                "User berhasil ditambahkan"
            )

        except Exception as e:

            QMessageBox.warning(
                self,
                "Error",
                str(e)
            )

        conn.close()

        self.load_data()

        self.clear_form()

    # ================= SELECT =================
    def select_row(self, row):

        self.selected_id = self.table.item(
            row,
            0
        ).text()

        self.username_input.setText(
            self.table.item(row, 1).text()
        )

        self.password_input.setText(
            self.table.item(row, 2).text()
        )

        role = self.table.item(row, 3).text()

        self.role_combo.setCurrentText(role)

    # ================= UPDATE =================
    def update_user(self):

        if not self.selected_id:
            return

        username = self.username_input.text()

        password = self.password_input.text()

        role = self.role_combo.currentText()

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        UPDATE users
        SET username=?,
            password=?,
            role=?
        WHERE id=?
        """, (
            username,
            password,
            role,
            self.selected_id
        ))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "User berhasil diupdate"
        )

        self.load_data()

        self.clear_form()

    # ================= DELETE =================
    def delete_user(self):

        if not self.selected_id:
            return

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        DELETE FROM users
        WHERE id=?
        """, (
            self.selected_id,
        ))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "User berhasil dihapus"
        )

        self.load_data()

        self.clear_form()
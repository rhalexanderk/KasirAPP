from PySide6.QtWidgets import *
from database import connect


class ProductWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.selected_id = None

        self.setWindowTitle("CRUD Barang")

        self.resize(950, 600)

        layout = QVBoxLayout()

        # ================= SEARCH =================
        search_layout = QHBoxLayout()

        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Cari nama / barcode..."
        )

        self.search_input.textChanged.connect(
            self.search_product
        )

        btn_reset = QPushButton("Reset")

        btn_reset.clicked.connect(
            self.reset_search
        )

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(btn_reset)

        layout.addLayout(search_layout)

        # ================= FORM =================
        form = QFormLayout()

        self.barcode_input = QLineEdit()

        self.name_input = QLineEdit()

        self.price_input = QLineEdit()

        self.stock_input = QLineEdit()

        form.addRow(
            "Barcode",
            self.barcode_input
        )

        form.addRow(
            "Nama Barang",
            self.name_input
        )

        form.addRow(
            "Harga",
            self.price_input
        )

        form.addRow(
            "Stok",
            self.stock_input
        )

        layout.addLayout(form)

        # ================= BUTTON =================
        btn_layout = QHBoxLayout()

        self.add_btn = QPushButton("Tambah")

        self.update_btn = QPushButton("Update")

        self.delete_btn = QPushButton("Hapus")

        self.add_btn.clicked.connect(
            self.add_product
        )

        self.update_btn.clicked.connect(
            self.update_product
        )

        self.delete_btn.clicked.connect(
            self.delete_product
        )

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.update_btn)
        btn_layout.addWidget(self.delete_btn)

        layout.addLayout(btn_layout)

        # ================= TABLE =================
        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Barcode",
            "Nama",
            "Harga",
            "Stok"
        ])

        self.table.cellClicked.connect(
            self.select_row
        )

        self.table.horizontalHeader().setStretchLastSection(
            True
        )

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
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
        FROM products
        ORDER BY id DESC
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

    # ================= SEARCH PRODUCT =================
    def search_product(self):

        keyword = self.search_input.text()

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT *
        FROM products
        WHERE barcode LIKE ?
        OR name LIKE ?
        OR CAST(price AS TEXT) LIKE ?
        OR CAST(stock AS TEXT) LIKE ?
        ORDER BY id DESC
        """, (
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%",
            f"%{keyword}%"
        ))

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

    # ================= RESET SEARCH =================
    def reset_search(self):

        self.search_input.clear()

        self.load_data()

    # ================= CLEAR FORM =================
    def clear_form(self):

        self.selected_id = None

        self.barcode_input.clear()

        self.name_input.clear()

        self.price_input.clear()

        self.stock_input.clear()

    # ================= ADD PRODUCT =================
    def add_product(self):

        barcode = self.barcode_input.text()

        name = self.name_input.text()

        price = self.price_input.text()

        stock = self.stock_input.text()

        # ================= VALIDATION =================
        if (
            barcode == ""
            or name == ""
            or price == ""
            or stock == ""
        ):

            QMessageBox.warning(
                self,
                "Error",
                "Semua field wajib diisi"
            )

            return

        try:

            price = int(price)

            stock = int(stock)

        except:

            QMessageBox.warning(
                self,
                "Error",
                "Harga dan stok harus angka"
            )

            return

        conn = connect()

        cur = conn.cursor()

        # ================= CEK BARCODE =================
        cur.execute("""
        SELECT *
        FROM products
        WHERE barcode=?
        """, (
            barcode,
        ))

        existing = cur.fetchone()

        if existing:

            QMessageBox.warning(
                self,
                "Error",
                "Barcode sudah digunakan"
            )

            conn.close()

            return

        # ================= INSERT =================
        cur.execute("""
        INSERT INTO products
        (barcode, name, price, stock)
        VALUES (?, ?, ?, ?)
        """, (
            barcode,
            name,
            price,
            stock
        ))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "Barang berhasil ditambahkan"
        )

        self.load_data()

        self.clear_form()

    # ================= SELECT ROW =================
    def select_row(self, row):

        self.selected_id = self.table.item(
            row,
            0
        ).text()

        self.barcode_input.setText(
            self.table.item(row, 1).text()
        )

        self.name_input.setText(
            self.table.item(row, 2).text()
        )

        self.price_input.setText(
            self.table.item(row, 3).text()
        )

        self.stock_input.setText(
            self.table.item(row, 4).text()
        )

    # ================= UPDATE PRODUCT =================
    def update_product(self):

        if not self.selected_id:

            QMessageBox.warning(
                self,
                "Error",
                "Pilih data terlebih dahulu"
            )

            return

        barcode = self.barcode_input.text()

        name = self.name_input.text()

        price = self.price_input.text()

        stock = self.stock_input.text()

        if (
            barcode == ""
            or name == ""
            or price == ""
            or stock == ""
        ):

            QMessageBox.warning(
                self,
                "Error",
                "Semua field wajib diisi"
            )

            return

        try:

            price = int(price)

            stock = int(stock)

        except:

            QMessageBox.warning(
                self,
                "Error",
                "Harga dan stok harus angka"
            )

            return

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        UPDATE products
        SET barcode=?,
            name=?,
            price=?,
            stock=?
        WHERE id=?
        """, (
            barcode,
            name,
            price,
            stock,
            self.selected_id
        ))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "Barang berhasil diupdate"
        )

        self.load_data()

        self.clear_form()

    # ================= DELETE PRODUCT =================
    def delete_product(self):

        if not self.selected_id:

            QMessageBox.warning(
                self,
                "Error",
                "Pilih data terlebih dahulu"
            )

            return

        reply = QMessageBox.question(
            self,
            "Konfirmasi",
            "Yakin ingin menghapus barang?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply != QMessageBox.Yes:
            return

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        DELETE FROM products
        WHERE id=?
        """, (
            self.selected_id,
        ))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "Barang berhasil dihapus"
        )

        self.load_data()

        self.clear_form()
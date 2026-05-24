from PySide6.QtWidgets import *
from database import connect


class TransactionDetailWindow(QWidget):

    def __init__(self, transaction_id):
        super().__init__()

        self.transaction_id = transaction_id

        self.setWindowTitle(
            f"Detail Transaksi #{transaction_id}"
        )

        self.resize(600, 400)

        layout = QVBoxLayout()

        # ================= TITLE =================
        title = QLabel(
            f"Detail Transaksi #{transaction_id}"
        )

        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        layout.addWidget(title)

        # ================= TABLE =================
        self.table = QTableWidget()

        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels([
            "Nama Barang",
            "Harga",
            "Qty",
            "Subtotal"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)

        self.setLayout(layout)

        self.load_data()

    # ================= LOAD DATA =================
    def load_data(self):

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT
            product_name,
            price,
            qty,
            subtotal
        FROM transaction_items
        WHERE transaction_id = ?
        """, (self.transaction_id,))

        rows = cur.fetchall()

        self.table.setRowCount(len(rows))

        for row_index, row_data in enumerate(rows):

            for col_index, data in enumerate(row_data):

                self.table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(data))
                )

        conn.close()
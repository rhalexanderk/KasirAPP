from PySide6.QtWidgets import *
from database import connect


class ReportWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Laporan Penjualan")
        self.resize(1000, 600)

        layout = QVBoxLayout()

        # ================= TABLE =================
        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Total",
            "Cash",
            "Kembalian",
            "Tanggal"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        # DOUBLE CLICK
        self.table.cellDoubleClicked.connect(
            self.show_detail
        )

        layout.addWidget(self.table)

        # ================= TOTAL =================
        self.total_label = QLabel(
            "Total Omzet: Rp 0"
        )

        self.total_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
        """)

        layout.addWidget(self.total_label)

        self.setLayout(layout)

        self.load_data()

    # ================= LOAD DATA =================
    def load_data(self):

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT
            id,
            total,
            cash,
            change,
            created_at
        FROM transactions
        ORDER BY id DESC
        """)

        rows = cur.fetchall()

        self.table.setRowCount(len(rows))

        total_all = 0

        for row_index, row_data in enumerate(rows):

            for col_index, data in enumerate(row_data):

                # format uang
                if col_index in [1, 2, 3]:

                    data = f"Rp {int(data):,}"

                self.table.setItem(
                    row_index,
                    col_index,
                    QTableWidgetItem(str(data))
                )

            total_all += row_data[1]

        conn.close()

        self.total_label.setText(
            f"Total Omzet: Rp {total_all:,}"
        )

    # ================= DETAIL =================
    def show_detail(self, row):

        transaction_id = self.table.item(
            row,
            0
        ).text()

        conn = connect()

        cur = conn.cursor()

        # ambil transaksi
        cur.execute("""
        SELECT
            id,
            total,
            cash,
            change,
            created_at
        FROM transactions
        WHERE id = ?
        """, (transaction_id,))

        trx = cur.fetchone()

        # ambil item
        cur.execute("""
        SELECT
            product_name,
            price,
            qty,
            subtotal
        FROM transaction_items
        WHERE transaction_id = ?
        """, (transaction_id,))

        items = cur.fetchall()

        conn.close()

        # ================= STRUK =================
        receipt = ""

        receipt += "================================\n"
        receipt += "        TOKO KASIR APP          \n"
        receipt += "================================\n\n"

        receipt += f"ID Transaksi : {trx[0]}\n"
        receipt += f"Tanggal      : {trx[4]}\n\n"

        receipt += "--------------------------------\n"
        receipt += "ITEM BELANJA\n"
        receipt += "--------------------------------\n"

        for item in items:

            name = item[0]
            price = item[1]
            qty = item[2]
            subtotal = item[3]

            receipt += f"{name}\n"
            receipt += f"   {qty} x Rp {price:,} = Rp {subtotal:,}\n\n"

        receipt += "--------------------------------\n"

        receipt += f"TOTAL ITEM : {len(items)}\n"
        receipt += f"TOTAL      : Rp {trx[1]:,}\n"
        receipt += f"CASH       : Rp {trx[2]:,}\n"
        receipt += f"KEMBALI    : Rp {trx[3]:,}\n"

        receipt += "--------------------------------\n"
        receipt += "   TERIMA KASIH SUDAH BELANJA   \n"
        receipt += "================================\n"

        # ================= POPUP =================
        dialog = QDialog(self)

        dialog.setWindowTitle(
            f"Detail Transaksi #{transaction_id}"
        )

        dialog.resize(500, 600)

        dialog_layout = QVBoxLayout()

        text = QTextEdit()

        text.setReadOnly(True)

        text.setText(receipt)

        dialog_layout.addWidget(text)

        dialog.setLayout(dialog_layout)

        dialog.exec()
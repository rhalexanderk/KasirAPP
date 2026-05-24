from PySide6.QtWidgets import *
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from PySide6.QtGui import QTextDocument
from datetime import datetime


class ReceiptWindow(QWidget):

    def __init__(self, transaksi, items, cash, change, transaction_id):
        super().__init__()

        self.setWindowTitle("Struk Pembelian")
        self.resize(350, 600)

        self.transaksi = transaksi
        self.items = items
        self.cash = cash
        self.change = change
        self.transaction_id = transaction_id

        layout = QVBoxLayout()

        self.text = QTextEdit()
        self.text.setReadOnly(True)

        layout.addWidget(self.text)

        btn_print = QPushButton("Print Struk")
        btn_print.clicked.connect(self.print_receipt)

        layout.addWidget(btn_print)

        self.setLayout(layout)

        self.generate_receipt()

    # ================= STRUK DESIGN =================
    def generate_receipt(self):

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        content = ""

        content += "================================\n"
        content += "        TOKO KASIR APP          \n"
        content += "================================\n\n"

        content += f"ID Transaksi : {self.transaction_id}\n"
        content += f"Tanggal      : {now}\n\n"

        content += "--------------------------------\n"
        content += "ITEM BELANJA\n"
        content += "--------------------------------\n"

        total_qty = 0

        for item in self.items:

            name = item["name"]
            qty = item["qty"]
            subtotal = item["subtotal"]

            content += f"{name}\n"
            content += f"   {qty} x = Rp {subtotal:,}\n\n"

            total_qty += qty

        content += "--------------------------------\n"

        content += f"TOTAL ITEM : {total_qty}\n"
        content += f"TOTAL      : Rp {self.transaksi['total']:,}\n"
        content += f"CASH       : Rp {self.cash:,}\n"
        content += f"KEMBALI    : Rp {self.change:,}\n"

        content += "--------------------------------\n"
        content += "   TERIMA KASIH SUDAH BELANJA   \n"
        content += "================================\n"

        self.text.setText(content)

    # ================= PRINT =================
    def print_receipt(self):

        printer = QPrinter()
        dialog = QPrintDialog(printer, self)

        if dialog.exec() == QDialog.Accepted:
            self.text.print(printer)
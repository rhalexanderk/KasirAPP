from PySide6.QtWidgets import *
from database import connect
from receipt import ReceiptWindow
import json


class TransactionWindow(QWidget):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Transaksi Kasir")
        self.resize(1000, 650)

        self.total = 0

        self.layout = QVBoxLayout()

        # ================= SEARCH / BARCODE =================
        self.search_input = QLineEdit()

        self.search_input.setPlaceholderText(
            "Scan barcode / cari barang..."
        )

        self.search_input.textChanged.connect(
            self.filter_products
        )

        self.search_input.returnPressed.connect(
            self.add_from_search
        )

        self.layout.addWidget(self.search_input)

        # ================= TOP =================
        top = QHBoxLayout()

        self.product_combo = QComboBox()

        self.product_combo.setEditable(True)

        self.product_combo.lineEdit().setReadOnly(True)

        self.qty_input = QSpinBox()

        self.qty_input.setMinimum(1)

        self.qty_input.lineEdit().returnPressed.connect(
            self.add_item
        )

        btn_add = QPushButton("Tambah")

        btn_add.clicked.connect(
            self.add_item
        )

        top.addWidget(QLabel("Barang"))
        top.addWidget(self.product_combo)

        top.addWidget(QLabel("Qty"))
        top.addWidget(self.qty_input)

        top.addWidget(btn_add)

        self.layout.addLayout(top)

        # ================= TABLE =================
        self.table = QTableWidget()

        self.table.setColumnCount(5)

        self.table.setHorizontalHeaderLabels([
            "ID",
            "Nama",
            "Harga",
            "Qty",
            "Subtotal"
        ])

        self.table.horizontalHeader().setStretchLastSection(True)

        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )

        self.table.setEditTriggers(
            QTableWidget.NoEditTriggers
        )

        header = self.table.horizontalHeader()

        header.setSectionResizeMode(
            QHeaderView.Stretch
        )

        self.layout.addWidget(self.table)

        # ================= TOTAL =================
        self.total_label = QLabel("Total: Rp 0")

        self.total_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
        """)

        self.layout.addWidget(self.total_label)

        # ================= CASH =================
        self.cash_input = QLineEdit()

        self.cash_input.setPlaceholderText(
            "Masukkan uang bayar"
        )

        self.cash_input.returnPressed.connect(
            self.pay
        )

        self.layout.addWidget(self.cash_input)

        # ================= BUTTON =================
        btn_layout = QHBoxLayout()

        self.btn_delete = QPushButton("Hapus Item")

        self.btn_minus = QPushButton("Kurangi Jumlah")

        self.btn_hold = QPushButton("Hold")

        self.btn_load_hold = QPushButton("Load Hold")

        self.btn_pay = QPushButton("Bayar")

        self.btn_delete.clicked.connect(
            self.delete_item
        )

        self.btn_minus.clicked.connect(
            self.minus_qty
        )

        self.btn_hold.clicked.connect(
            self.save_hold
        )

        self.btn_load_hold.clicked.connect(
            self.load_hold
        )

        self.btn_pay.clicked.connect(
            self.pay
        )

        btn_layout.addWidget(self.btn_delete)

        btn_layout.addWidget(self.btn_minus)

        btn_layout.addWidget(self.btn_hold)

        btn_layout.addWidget(self.btn_load_hold)

        btn_layout.addWidget(self.btn_pay)

        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)

        # ================= LOAD PRODUCTS =================
        self.load_products()

        self.search_input.setFocus()

    # ================= LOAD PRODUCTS =================
    def load_products(self):

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT id, barcode, name, price, stock
        FROM products
        ORDER BY name ASC
        """)

        self.products = cur.fetchall()

        conn.close()

        self.product_combo.clear()

        for p in self.products:

            barcode = p[1]
            name = p[2]
            price = p[3]
            stock = p[4]

            if stock <= 0:

                self.product_combo.addItem(
                    f"{barcode} | {name} - HABIS",
                    p
                )

            else:

                self.product_combo.addItem(
                    f"{barcode} | {name} - Rp {price:,} (Stok {stock})",
                    p
                )

    # ================= FILTER PRODUCTS =================
    def filter_products(self):

        keyword = self.search_input.text().lower()

        self.product_combo.clear()

        for p in self.products:

            barcode = str(p[1]).lower()

            name = p[2].lower()

            price = p[3]

            stock = p[4]

            if keyword in barcode or keyword in name:

                if stock <= 0:

                    self.product_combo.addItem(
                        f"{barcode} | {name} - HABIS",
                        p
                    )

                else:

                    self.product_combo.addItem(
                        f"{barcode} | {name} - Rp {price:,} (Stok {stock})",
                        p
                    )

    # ================= ADD FROM SEARCH =================
    def add_from_search(self):

        keyword = self.search_input.text().strip()

        if keyword == "":
            return

        if self.product_combo.count() <= 0:

            QMessageBox.warning(
                self,
                "Error",
                "Barang tidak ditemukan"
            )

            self.search_input.clear()

            return

        self.product_combo.setCurrentIndex(0)

        self.add_item()

    # ================= ADD ITEM =================
    def add_item(self):

        product = self.product_combo.currentData()

        if not product:

            QMessageBox.warning(
                self,
                "Error",
                "Barang tidak ditemukan"
            )

            return

        product_id = product[0]

        barcode = product[1]

        name = product[2]

        price = product[3]

        stock = product[4]

        qty = self.qty_input.value()

        # ================= VALIDASI STOK =================
        if stock <= 0:

            QMessageBox.warning(
                self,
                "Stok Habis",
                f"{name} stok habis"
            )

            return

        if qty > stock:

            QMessageBox.warning(
                self,
                "Stok Tidak Cukup",
                f"Stok hanya {stock}"
            )

            return

        subtotal = price * qty

        # ================= CEK DUPLIKAT =================
        for row in range(self.table.rowCount()):

            existing_id = int(
                self.table.item(row, 0).text()
            )

            if existing_id == product_id:

                old_qty = int(
                    self.table.item(row, 3).text()
                )

                total_qty = old_qty + qty

                # ================= VALIDASI TOTAL STOK =================
                if total_qty > stock:

                    QMessageBox.warning(
                        self,
                        "Stok Tidak Cukup",
                        f"Total pembelian melebihi stok ({stock})"
                    )

                    return

                old_subtotal = int(
                    self.table.item(
                        row,
                        4
                    ).text().replace(",", "")
                )

                new_subtotal = old_subtotal + subtotal

                self.table.setItem(
                    row,
                    3,
                    QTableWidgetItem(str(total_qty))
                )

                self.table.setItem(
                    row,
                    4,
                    QTableWidgetItem(f"{new_subtotal:,}")
                )

                self.total += subtotal

                self.update_total()

                self.qty_input.setValue(1)

                self.search_input.clear()

                self.search_input.setFocus()

                return

        # ================= INSERT BARU =================
        row = self.table.rowCount()

        self.table.insertRow(row)

        self.table.setItem(
            row,
            0,
            QTableWidgetItem(str(product_id))
        )

        self.table.setItem(
            row,
            1,
            QTableWidgetItem(name)
        )

        self.table.setItem(
            row,
            2,
            QTableWidgetItem(f"{price:,}")
        )

        self.table.setItem(
            row,
            3,
            QTableWidgetItem(str(qty))
        )

        self.table.setItem(
            row,
            4,
            QTableWidgetItem(f"{subtotal:,}")
        )

        self.total += subtotal

        self.update_total()

        self.qty_input.setValue(1)

        self.search_input.clear()

        self.search_input.setFocus()

    # ================= MINUS QTY =================
    def minus_qty(self):

        row = self.table.currentRow()

        if row < 0:
            return

        price = int(
            self.table.item(row, 2).text().replace(",", "")
        )

        qty = int(
            self.table.item(row, 3).text()
        )

        subtotal = int(
            self.table.item(row, 4).text().replace(",", "")
        )

        # jika qty tinggal 1 langsung hapus
        if qty <= 1:

            self.total -= subtotal

            self.table.removeRow(row)

            self.update_total()

            return

        # kurangi qty
        new_qty = qty - 1

        new_subtotal = price * new_qty

        # update table
        self.table.setItem(
            row,
            3,
            QTableWidgetItem(str(new_qty))
        )

        self.table.setItem(
            row,
            4,
            QTableWidgetItem(f"{new_subtotal:,}")
        )

        # update total
        self.total -= price

        self.update_total()

    # ================= DELETE ITEM =================
    def delete_item(self):

        row = self.table.currentRow()

        if row < 0:
            return

        subtotal = int(
            self.table.item(
                row,
                4
            ).text().replace(",", "")
        )

        self.total -= subtotal

        self.table.removeRow(row)

        self.update_total()

    # ================= UPDATE TOTAL =================
    def update_total(self):

        self.total_label.setText(
            f"Total: Rp {self.total:,}"
        )

    # ================= SAVE HOLD =================
    def save_hold(self):

        if self.table.rowCount() == 0:

            QMessageBox.warning(
                self,
                "Error",
                "Keranjang kosong"
            )

            return

        items = []

        for row in range(self.table.rowCount()):

            items.append({
                "id": self.table.item(row, 0).text(),
                "name": self.table.item(row, 1).text(),
                "price": self.table.item(row, 2).text(),
                "qty": self.table.item(row, 3).text(),
                "subtotal": self.table.item(row, 4).text().replace(",", "")
            })

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        INSERT INTO hold_transactions
        (items, total)
        VALUES (?, ?)
        """, (
            json.dumps(items),
            self.total
        ))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "Transaksi berhasil dihold"
        )

        # ================= RESET =================
        self.table.setRowCount(0)

        self.total = 0

        self.update_total()

        self.cash_input.clear()

    # ================= LOAD HOLD =================
    def load_hold(self):

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT id, total
        FROM hold_transactions
        ORDER BY id DESC
        """)

        holds = cur.fetchall()

        conn.close()

        if not holds:

            QMessageBox.warning(
                self,
                "Kosong",
                "Tidak ada hold transaksi"
            )

            return

        items_text = []

        for h in holds:

            items_text.append(
                f"HOLD #{h[0]} - Rp {h[1]:,}"
            )

        selected, ok = QInputDialog.getItem(
            self,
            "Load Hold",
            "Pilih Hold:",
            items_text,
            0,
            False
        )

        if not ok:
            return

        hold_id = int(
            selected.split("#")[1].split(" ")[0]
        )

        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        SELECT items, total
        FROM hold_transactions
        WHERE id = ?
        """, (hold_id,))

        hold = cur.fetchone()

        conn.close()

        if not hold:
            return

        items = json.loads(hold[0])

        self.table.setRowCount(0)

        self.total = hold[1]

        for item in items:

            row = self.table.rowCount()

            self.table.insertRow(row)

            self.table.setItem(
                row,
                0,
                QTableWidgetItem(item["id"])
            )

            self.table.setItem(
                row,
                1,
                QTableWidgetItem(item["name"])
            )

            self.table.setItem(
                row,
                2,
                QTableWidgetItem(item["price"])
            )

            self.table.setItem(
                row,
                3,
                QTableWidgetItem(item["qty"])
            )

            self.table.setItem(
                row,
                4,
                QTableWidgetItem(item["subtotal"])
            )

        self.update_total()

        # ================= DELETE HOLD =================
        conn = connect()

        cur = conn.cursor()

        cur.execute("""
        DELETE FROM hold_transactions
        WHERE id = ?
        """, (hold_id,))

        conn.commit()

        conn.close()

        QMessageBox.information(
            self,
            "Sukses",
            "Hold berhasil dimuat"
        )

    # ================= PAY =================
    def pay(self):

        if self.table.rowCount() == 0:

            QMessageBox.warning(
                self,
                "Error",
                "Keranjang masih kosong"
            )

            return

        try:

            cash = int(
                self.cash_input.text()
            )

        except:

            QMessageBox.warning(
                self,
                "Error",
                "Input uang tidak valid"
            )

            return

        if cash < self.total:

            QMessageBox.warning(
                self,
                "Error",
                "Uang tidak cukup"
            )

            return

        change = cash - self.total

        conn = connect()

        cur = conn.cursor()

        items = []

        # ================= INSERT TRANSACTION =================
        cur.execute("""
        INSERT INTO transactions
        (
            total,
            cash,
            change
        )
        VALUES (?, ?, ?)
        """, (
            self.total,
            cash,
            change
        ))

        transaction_id = cur.lastrowid

        # ================= LOOP ITEM =================
        for row in range(self.table.rowCount()):

            product_id = int(
                self.table.item(row, 0).text()
            )

            name = self.table.item(row, 1).text()

            price = int(
                self.table.item(
                    row,
                    2
                ).text().replace(",", "")
            )

            qty = int(
                self.table.item(row, 3).text()
            )

            subtotal = int(
                self.table.item(
                    row,
                    4
                ).text().replace(",", "")
            )

            # ================= INSERT ITEM =================
            cur.execute("""
            INSERT INTO transaction_items
            (
                transaction_id,
                product_name,
                price,
                qty,
                subtotal
            )
            VALUES (?, ?, ?, ?, ?)
            """, (
                transaction_id,
                name,
                price,
                qty,
                subtotal
            ))

            # ================= UPDATE STOCK =================
            cur.execute("""
            UPDATE products
            SET stock = stock - ?
            WHERE id = ?
            """, (
                qty,
                product_id
            ))

            items.append({
                "name": name,
                "qty": qty,
                "subtotal": subtotal
            })

        conn.commit()

        conn.close()

        # ================= STRUK =================
        self.receipt = ReceiptWindow(
            transaksi={
                "total": self.total
            },
            items=items,
            cash=cash,
            change=change,
            transaction_id=transaction_id
        )

        self.receipt.show()

        # ================= RESET =================
        self.table.setRowCount(0)

        self.total = 0

        self.update_total()

        self.cash_input.clear()

        self.search_input.clear()

        self.load_products()

        self.search_input.setFocus()
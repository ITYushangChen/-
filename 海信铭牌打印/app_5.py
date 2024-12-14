from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QCompleter, QHBoxLayout, QMessageBox
from PyQt5.QtCore import Qt
import sys
import pandas as pd
from datetime import datetime
import qrcode
import os
import io
from PyPDF2 import PdfWriter, PdfReader, PdfMerger
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
# import win32print
# import win32api
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QCompleter, QMessageBox
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtCore import QUrl
from PyQt5.QtPrintSupport import QPrinterInfo
from PyQt5.QtWidgets import QComboBox
# 获取当前日期
current_date = datetime.now()
# 以year/month/day的格式输出DATE
DATE = current_date.strftime("%Y/%m/%d")
nonSplitDate = DATE.replace("/", "")
SUPPILER = "青岛开拓隆海智控有限公司"

# 整合pdf
def merge_pdfs(pdf_list, output):
    merger = PdfMerger()
    for pdf in pdf_list:
        merger.append(pdf)
    merger.write(output)
    merger.close()

# 预览pdf
def preview_pdf(pdf_path):
    QDesktopServices.openUrl(QUrl.fromLocalFile(pdf_path))

# Function to load data
def load_data():
    df = pd.read_excel('海信物料编码.xlsx', engine='openpyxl')
    return df

# Function to generate QR code
def generate_qr(data, filename):
    qr_code = qrcode.make(data)
    qr_code.save(filename)
    return filename

class ProductSearchApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.df = load_data()
        self.product_code_list = [str(code) for code in self.df['物料编码'].unique()]
        self.product_describe_list = [str(code)[0:code.rfind('/')] for code in self.df['物料描述'].unique()]
        self.dictionary = dict(map(lambda x, y: [x, y], self.product_describe_list, self.product_code_list))
        self.quick_print_btn = QPushButton('快速打印', self)
        self.quick_print_btn.clicked.connect(self.onQuickPrint)

        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('Product Search App')
        self.setStyleSheet("background-color: #F5F5F5;")
        widget = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel('产品图号:')
        layout.addWidget(self.label)
        self.product_name_tc = QLineEdit(self)
        completer = QCompleter(self.product_describe_list)
        completer.setFilterMode(Qt.MatchContains)
        self.product_name_tc.setCompleter(completer)
        layout.addWidget(self.product_name_tc)

        self.quantity_label = QLabel('批次:')
        layout.addWidget(self.quantity_label)
        self.quantity_tc = QLineEdit(self)
        layout.addWidget(self.quantity_tc)

        self.products_per_batch_label = QLabel('数量/箱:')
        layout.addWidget(self.products_per_batch_label)
        self.products_per_batch_tc = QLineEdit(self)
        layout.addWidget(self.products_per_batch_tc)

        self.labels_per_box_label = QLabel('每箱铭牌数量:')
        layout.addWidget(self.labels_per_box_label)
        self.labels_per_box_tc = QLineEdit(self)
        layout.addWidget(self.labels_per_box_tc)

        self.printer_label = QLabel('选择打印机:')
        layout.addWidget(self.printer_label)
        self.printer_cb = QComboBox(self)
        self.printer_cb.addItems(QPrinterInfo.availablePrinterNames())
        layout.addWidget(self.printer_cb)

        hbox = QHBoxLayout()
        self.search_btn = QPushButton('添加', self)
        self.search_btn.clicked.connect(lambda: self.onSearch('pdfs'))
        hbox.addWidget(self.search_btn)

        self.preview_btn = QPushButton('预览', self)
        self.preview_btn.clicked.connect(self.onPreview)
        hbox.addWidget(self.preview_btn)

        self.delete_btn = QPushButton('清除', self)
        self.delete_btn.clicked.connect(self.onDelete)
        hbox.addWidget(self.delete_btn)

        layout.addLayout(hbox)

        hbox_print = QHBoxLayout()
        self.print_btn = QPushButton('打印', self)
        self.print_btn.clicked.connect(lambda: self.onPrint('pdfs'))
        self.print_btn.setFixedSize(100, 50)
        self.print_btn.setStyleSheet('font-size: 18px')
        self.print_btn.setStyleSheet("background-color: #008CBA; color: white;")
        hbox_print.addStretch(1)
        hbox_print.addWidget(self.print_btn)
        layout.addLayout(hbox_print)

        hbox_quick_print = QHBoxLayout()
        hbox_quick_print.addStretch(1)
        hbox_quick_print.addWidget(self.quick_print_btn)  # 添加新的快速打印按钮到布局中
        layout.addLayout(hbox_quick_print)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def onQuickPrint(self):
        self.onSearch('quickpdfs')
        self.onPrint('quickpdfs')

    def onPreview(self):
        pdf_folder = 'pdfs'
        pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith('.pdf') and f != 'merged.pdf']
        file_num = len(pdf_files)
        if 'merged.pdf' in pdf_files:
            file_num -= 1
        if file_num == 0:
            QMessageBox.warning(self, "Error", "请添加文件！")
            return
        output_pdf = os.path.join(pdf_folder, 'merged.pdf')
        merge_pdfs(pdf_files, output_pdf)
        preview_pdf(output_pdf)

    def onDelete(self):
        pdf_folder = 'pdfs'
        for pdf_file in os.listdir(pdf_folder):
            if pdf_file.endswith('.pdf'):
                os.remove(os.path.join(pdf_folder, pdf_file))
        with open("ready_store.txt", 'w') as file:
            pass
        QMessageBox.information(self, "Success", "清除成功!")

    def onPrint(self, path):
        print("printing..................")
        printer_name = self.printer_cb.currentText()
        pdf_folder = path
        pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith('.pdf') and f != 'merged.pdf']
        file_num = len(pdf_files)
        if 'merged.pdf' in pdf_files:
            file_num -= 1
        if file_num == 0:
            QMessageBox.warning(self, "Error", "请添加文件！")
            return
        if path == 'pdfs':
            output_pdf = os.path.join(pdf_folder, 'merged.pdf')
            merge_pdfs(pdf_files, output_pdf)
            win32api.ShellExecute(
                0,
                "print",
                os.path.join(pdf_folder, "merged.pdf"),
                '/d:"%s"' % printer_name,
                ".",
                0
            )
            with open('ready_store.txt', 'r') as file:
                lines = file.readlines()
            df = pd.read_excel('铭牌打印记录.xlsx')
            for line in lines:
                data = line.strip().split(",")
                new_row = {'批次号': data[0], '物料描述': data[1], '日期': data[2], '数量': data[3]}
                df = df._append(new_row, ignore_index=True)
            df.to_excel('铭牌打印记录.xlsx', index=False)
        else:
            print_count_file = 'record_num.txt'
            with open(print_count_file, 'r') as file:
                print_count = int(file.read().strip())
            output_pdf = os.path.join(pdf_folder, 'merged_{:03d}.pdf'.format(print_count))

            # Merge the pdfs
            merge_pdfs(pdf_files, output_pdf)

            # Add code to delete original pdf files
            for pdf_file in pdf_files:
                try:
                    os.remove(pdf_file)
                except OSError as e:
                    print("Error: %s : %s" % (pdf_file, e.strerror))

            # Print the merged pdf
            win32api.ShellExecute(
                0,
                "print",
                output_pdf,
                '/d:"%s"' % win32print.GetDefaultPrinter(),
                ".",
                0
            )

            with open('ready_store.txt', 'r') as file:
                lines = file.readlines()
            df = pd.read_excel('铭牌打印记录.xlsx')
            for line in lines:
                data = line.strip().split(",")
                new_row = {'批次号': data[0], '物料描述': data[1], '日期': data[2], '数量': data[3]}
                df = df.append(new_row, ignore_index=True)
            df.to_excel('铭牌打印记录.xlsx', index=False)

            # Save the new print count to the file
            with open(print_count_file, 'w') as file:
                file.write(str(print_count+1))

    def onSearch(self,directory):
        product_name = int(self.dictionary.get(self.product_name_tc.text(), 0))
        if product_name == 0:
            QMessageBox.warning(self, "Error", "无效编码！")
            return
        quantity = self.quantity_tc.text()
        product = self.df[self.df['物料编码'] == product_name]
        products_per_batch_tc = self.products_per_batch_tc.text()
        labels_per_box = int(self.labels_per_box_tc.text())
        if not product.empty:
            QMessageBox.information(self, "批次", "添加成功！")
            code_wuliao = str(product['物料编码'].values[0])
            description = str(product['物料描述'].values[0])
            code_gongying = str(product['供方代码'].values[0])
            for i in range(int(quantity)):
                new_batch_number = get_new_batch_number(DATE, description) + 1
                new_batch_number += i
                with open('初始.pdf', 'rb') as f:
                    ENCODE = code_wuliao + "-" + code_gongying + "-" + nonSplitDate + "-" + nonSplitDate + "-" + str(
                        new_batch_number).zfill(6)
                    delimeter = ","
                    line = ENCODE + delimeter + description + delimeter + DATE + delimeter + quantity + "\n"
                    with open('ready_store.txt', 'a') as file:
                        file.write(line)
                    source = PdfReader(f)
                    page = source.pages[0]
                    pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
                    packet = io.BytesIO()
                    qr_code_file = generate_qr(ENCODE, 'qr_code.png')
                    qr_code_file_quantity = generate_qr(products_per_batch_tc, 'qr_code_quantity.png')
                    c = canvas.Canvas(packet, pagesize=page.mediabox.upper_right)
                    print(description)
                    c.setFont('Helvetica', 9)
                    c.drawString(40, 150, ENCODE)
                    c.drawString(118, 122, str(product_name))
                    c.drawString(227, 122, DATE)
                    c.drawString(118, 66, DATE)
                    c.drawString(118, 38, str(products_per_batch_tc))
                    c.setFont('SimHei', 9)
                    c.drawString(118, 94, description)
                    c.drawString(60, 10, SUPPILER)
                    c.drawImage(qr_code_file, 3, 70, width=50, height=50)
                    c.drawImage(qr_code_file_quantity, 223, 23, width=50, height=50)
                    c.save()
                    packet.seek(0)
                    new_pdf = PdfReader(packet)
                    page.merge_page(new_pdf.pages[0])
                    output = PdfWriter()
                    output.add_page(page)
                    timestamp = str(time.time()).replace('.', '')
                    for j in range(labels_per_box):
                        label_filename = f'{directory}/output_{product_name}_{i}_{j}.pdf'
                        with open(label_filename, 'wb') as f:
                            output.write(f)
        else:
            QMessageBox.warning(self, "Error", "无效编码！")

def get_new_batch_number(date, product_description):
    df = pd.read_excel('铭牌打印记录.xlsx')  # 请替换为你的Excel文件名
    # 只保留同一天和同一产品的数据
    df_same_day_and_product = df[(df['日期'] == date) & (df['物料描述'] == product_description)]
    if df_same_day_and_product.empty:
        # 如果在同一天和同一产品没有记录，则返回1
        return 0
    else:
        # 否则返回最大批次号加一
        df_same_day_and_product['批次'] = df_same_day_and_product['批次号'].apply(lambda x: int(x[-6:]))  # 从批次号中提取最后六位，并转为整数
        max_batch_number = df_same_day_and_product['批次'].max()
        return max_batch_number

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProductSearchApp()
    ex.show()
    sys.exit(app.exec_())

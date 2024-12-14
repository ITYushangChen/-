from PyQt5.QtCore import Qt
import sys
import pandas as pd
from datetime import datetime
import qrcode
import os
import io
from PyPDF2 import PdfWriter, PdfReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QCompleter, QMessageBox

# 获取当前日期
current_date = datetime.now()

# 以year/month/day的格式输出
DATE = current_date.strftime("%Y/%m/%d")
nonSplitDate = DATE.replace("/","")
SUPPILER = "青岛开拓隆海制冷配件有限公司"

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
        self.product_code_list = [str(code) for code in self.df['物料编码'].unique()]  # 获取所有不重复的物料编码，并将它们转换为字符串
        self.product_describe_list = [str(code)[0:code.rfind('/')] for code in self.df['物料描述'].unique()]  # 获取所有不重复的产品图号，并将它们转换为字符串
        self.dictionary = dict(map(lambda x,y:[x,y],self.product_describe_list,self.product_code_list))
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 400)
        self.setWindowTitle('Product Search App')

        widget = QWidget()
        layout = QVBoxLayout()

        self.label = QLabel('产品图号:')
        layout.addWidget(self.label)

        self.product_name_tc = QLineEdit(self)
        completer = QCompleter(self.product_describe_list)
        completer.setFilterMode(Qt.MatchContains)  # 将匹配模式设置为MatchContains
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

        self.search_btn = QPushButton('搜索', self)
        self.search_btn.clicked.connect(self.onSearch)
        layout.addWidget(self.search_btn)

        self.print_btn = QPushButton('打印', self)
        self.print_btn.clicked.connect(self.onPrint)
        layout.addWidget(self.print_btn)

        self.delete_btn = QPushButton('清除', self)
        self.delete_btn.clicked.connect(self.onDelete)
        layout.addWidget(self.delete_btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def onPreview(self):
        pdf_folder = 'pdfs'
        pdf_files = [os.path.join(pdf_folder, f) for f in os.listdir(pdf_folder) if f.endswith('.pdf')]
        output_pdf = os.path.join(pdf_folder, 'merged.pdf')
        merge_pdfs(pdf_files, output_pdf)
        preview_pdf(output_pdf)
    def onDelete(self):
        pdf_folder = 'pdfs'
        for pdf_file in os.listdir(pdf_folder):
            if pdf_file.endswith('.pdf'):
                os.remove(os.path.join(pdf_folder, pdf_file))
        QMessageBox.information(self, "Success", "清除成功!")

    def onPrint(self):
        print("printing..................")
        pdf_folder = 'pdfs'
        for pdf_file in os.listdir(pdf_folder):
            win32api.ShellExecute(
                0,
                "print",
                os.path.join(pdf_folder, pdf_file),
                '/d:"%s"' % win32print.GetDefaultPrinter(),
                ".",
                0
            )

    def onSearch(self):
        product_name = int(self.dictionary[self.product_name_tc.text()])
        quantity = self.quantity_tc.text()
        product = self.df[self.df['物料编码'] == product_name]
        products_per_batch_tc = self.products_per_batch_tc.text()

        if not product.empty:
            QMessageBox.information(self, "批次", "添加成功！")
            code_wuliao = str(product['物料编码'].values[0])
            description = str(product['物料描述'].values[0])
            code_gongying = str(product['供方代码'].values[0])
            for i in range(int(quantity)):
                with open('初始.pdf', 'rb') as f:
                    ENCODE = code_wuliao + "-" + code_gongying + "-"+ nonSplitDate + "-" + nonSplitDate+ "-" + str(i+1).zfill(6)
                    source = PdfReader(f)
                    page = source.pages[0]
                    pdfmetrics.registerFont(TTFont('SimHei', 'SimHei.ttf'))
                    packet = io.BytesIO()
                    qr_code_file = generate_qr(ENCODE, 'qr_code.png')
                    qr_code_file_quantity = generate_qr(products_per_batch_tc, 'qr_code_quantity.png')
                    c = canvas.Canvas(packet, pagesize=page.mediabox.upper_right)
                    print(description)
                    c.setFont('Helvetica', 11)
                    c.drawString(40, 150, ENCODE)
                    c.drawString(118, 122, str(product_name))
                    c.drawString(227, 122, DATE)
                    c.drawString(118, 66, DATE)
                    c.drawString(118, 38, str(products_per_batch_tc))
                    c.setFont('SimHei', 11)
                    c.drawString(118, 94, description)
                    c.drawString(60, 10, SUPPILER)

                    c.drawImage(qr_code_file, 3, 70, width=50, height=50)
                    c.drawImage(qr_code_file_quantity, 230, 23, width=50, height=50)
                    c.save()
                    packet.seek(0)
                    new_pdf = PdfReader(packet)
                    page.merge_page(new_pdf.pages[0])
                    output = PdfWriter()
                    output.add_page(page)
                    timestamp = str(time.time()).replace('.', '')  # 获取当前时间戳并去除小数点
                    with open(f'pdfs/output_{product_name}_{timestamp}_{i}.pdf', 'wb') as f:  # 文件名中包含产品名和时间戳
                        output.write(f)

        else:
            QMessageBox.warning(self, "Error", "无效编码！")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ProductSearchApp()
    ex.show()
    sys.exit(app.exec_())

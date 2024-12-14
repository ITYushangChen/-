from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

# 创建一个100mm x 70mm的PDF
c = canvas.Canvas("output.pdf", pagesize=(100*mm, 70*mm))

# 添加图片，参数依次为图片路径、x坐标、y坐标、图片宽度、图片高度
c.drawImage("捕获.png", 0, 0, 100*mm, 70*mm)

# 保存PDF
c.save()


import qrcode
from PIL import Image


qr = qrcode.QRCode(
    error_correction=qrcode.constants.ERROR_CORRECT_H,
)

qr.add_data('https://google.com')
qr.make(fit=True)

img = qr.make_image(fill_color='blue', back_color='white')




img.save("my_qr_code.png")

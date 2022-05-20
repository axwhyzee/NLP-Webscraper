from PIL import Image
import pytesseract
import requests


#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Wei Kang\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def img_to_text(path):
    img = Image.open(path)
    
    return pytesseract.image_to_string(img, lang='eng')


def save_img(url, save_path):
    r = requests.get(url)
        
    with open(save_path, 'wb') as g:
        g.write(r.content)


def find_ext(path):
    lower = path.lower()
    if path:
        for ext in ['.png', '.jpg', '.jpeg']:
            if ext in lower:
                return ext
    return ''

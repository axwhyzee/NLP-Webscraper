from PIL import Image
import pytesseract
import requests


#pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Wei Kang\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def img_to_text(path):
    img = Image.open(path)
    
    return pytesseract.image_to_string(img, lang='eng')


def download_url(url, save_path):
    try:
        r = requests.get(url, verify=False)
        
        with open(save_path, 'wb') as g:
            g.write(r.content)
        return True
    except Exception as e:
        print(e)
        return False


def find_ext(path):
    lower = path.lower()
    if path:
        for ext in ['.png', '.jpg', '.jpeg']:
            if ext in lower:
                return ext
    return ''

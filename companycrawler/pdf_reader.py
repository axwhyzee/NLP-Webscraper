import io
import os
import re
import shutil
import PyPDF2
import fitz
from .functions import *


class PDFReader():
    def __init__(self):
        self.pdfs = []
        self.path = ''
        self.pdf_dir = ''

    def add(self, url):
        self.pdfs.append(url)

    def cleanText(self, text):
        text = text.lower()
        text = re.sub(r'[^.\w\s]|_', ' ', text) #remove non-alphanumeric & underscore chars
        return '\n'.join(line for line in text.split('\n') if len(line) > 1).strip() # remove consecutive \n & lines with only 1 character

    def extract_text(self, path):
        output = ''
        if path in os.listdir():
            with open(path, 'rb') as pdf:
                pdf_reader = PyPDF2.PdfFileReader(pdf)
                for pg in range(pdf_reader.numPages):
                    pgObj = pdf_reader.getPage(pg)
                    output += pgObj.extractText().strip() + '\n'
                    pg = str(pg)
                    
                    if pg in os.listdir(self.pdf_dir):
                        for img in os.listdir(os.path.join(self.pdf_dir, pg)):
                            output += img_to_text(os.path.join(self.pdf_dir, pg, img)).strip() + '\n'
            os.remove(path)
            shutil.rmtree(self.pdf_dir)
            print()
        else:
            print('[Error] File not found')
        
        return self.cleanText(output)

    def save_imgs(self, path):
        pdf_file = fitz.open(path)
        self.pdf_dir = gen_path()

        # Create a folder to save the images
        try:
            os.makedirs(self.pdf_dir) 
        except FileExistsError as e:
            pass
                
        for page_index in range(len(pdf_file)):
            try:
                os.makedirs(self.pdf_dir + '/' + str(page_index)) 
            except FileExistsError as e:
                pass
        
            # get the page itself
            page = pdf_file[page_index]
            image_list = page.get_images()
            
            # printing number of images found in this page
            if image_list:
                print(f"[+] Found a total of {len(image_list)} images in page {page_index+1}")
            else:
                print("[!] No images found on page", page_index + 1)
                
            for image_index, img in enumerate(page.get_images(), start=1):
                # get the XREF of the image
                xref = img[0]
                  
                # extract the image bytes
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                  
                # get the image extension
                image_ext = base_image["ext"]
                
                # Load to PIL
                image = Image.open(io.BytesIO(image_bytes))
                
                # save it to local disk
                image.save(open(f'{self.pdf_dir}/{page_index}/{image_index}.{image_ext}','wb'))

    def read_all_pdfs(self):
        for url in self.pdfs:
            pdf_obj = {}
            self.path = gen_path('.pdf')
            if download_url(url, self.path):
                print('[Download] {} <-- {}'.format(self.path, url))
            
                self.save_imgs(self.path)
                pdf_obj['url'] = url
                pdf_obj['text'] = self.extract_text(self.path)

            yield pdf_obj

    def reset(self):
        self.pdfs = []

#!pip install googletrans==4.0.0rc1
#!pip install langdetect

from googletrans import Translator
from langdetect import detect


class GoogleTranslate():
    def __init__(self):
        self.translator = Translator()
        self.tgt = 'en'
        self.max_char = 2000
        self.lines = []

    def get_chunk(self):
        chunk = ''
        while self.lines:
            if len(self.lines[0]) > self.max_char:
                words = self.lines[0].split()
                split_line = ''
                while words:
                    if len(words[0]) > self.max_char:
                        words.pop(0)
                    elif (len(split_line) + len(words[0])) < self.max_char:
                        split_line += words.pop(0) + ' '
                if words:
                    self.lines[0] = ' '.join(words)
                    
                return split_line
                
            elif (len(self.lines[0]) + len(chunk)) < self.max_char:
                chunk += self.lines.pop(0) + '\n'
            else:
                return chunk
        
    def load_lines(self, text):
        self.lines = text.split('\n')

    def translate(self, text):
        lang = detect(text)
        self.load_lines(text)
        
        if lang != self.tgt:
            print('({}) detected'.format(lang))
            translation = ''
            chunk = True
            while chunk:
                chunk = self.get_chunk()
                if chunk:
                    try:
                        translation += self.translator.translate(chunk, src=lang, dest=self.tgt).text + '\n'    
                    except Exception as e:
                        print(e)
                        translation += ' '

            print('[Translate] ({}) --> ({})'.format(lang, self.tgt))
            return translation
        else:
            return text

#!pip install googletrans==4.0.0rc1
#!pip install langdetect

from googletrans import Translator
from langdetect import detect


class GoogleTranslate():
    def __init__(self):
        self.translator = Translator()
        self.tgt = 'en'

    def translate(self, text):
        lang = detect(text)
        if lang != self.tgt:
            print('({}) detected'.format(lang))
            idx = 0
            chunk = ''
            translation = ''
            lines = text.split('\n')
        
            while True:
                while idx < len(lines) and len(chunk) + len(lines[idx]) < 2000:
                    chunk += lines[idx] + '\n'
                    idx += 1
                try:
                    translation += self.translator.translate(chunk, src=lang, dest=self.tgt).text + ' '    
                    print('[Translate] ({}) --> ({})'.format(lang, self.tgt))
                    
                except Exception as e:
                    print(e)
                    translation += ' '
                    
                if idx >= len(lines):
                    return translation

                chunk = lines[idx]
        else:
            return text

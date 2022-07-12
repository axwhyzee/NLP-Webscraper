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
            # if first line is longer than chunk size
            if len(self.lines[0]) > self.max_char:
                # split line into words
                words = self.lines[0].split()
                split_line = ''
                while words:
                    # remove singular words that are longer than chunk size
                    # these words are probably made by multiple words strung together errantly
                    if len(words[0]) > self.max_char:
                        words.pop(0)
                    # if after adding the first word to chunk, its size is still within the chunk size,
                    # then pop the word into the chunk
                    elif (len(split_line) + len(words[0])) < self.max_char:
                        split_line += words.pop(0) + ' '
                    else:
                        break
                # if there are leftover words, replace the first sentence with the leftovers
                if words:
                    self.lines[0] = ' '.join(words)
                    
                return split_line
                
            elif (len(self.lines[0]) + len(chunk)) < self.max_char:
                chunk += self.lines.pop(0) + '\n'
            else:
                break
        return chunk
        
    def load_lines(self, text):
        self.lines = text.split('\n')

    def translate(self, text):
        if not text.strip():
            return ''
        
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
                        print('trans',translation)
                    except Exception as e:
                        print(e)
                        translation += ' '

            print('[Translate] ({}) --> ({})'.format(lang, self.tgt))
            return translation
        else:
            return text
from gensim.models.phrases import Phraser
from gensim.models import Phrases
from nltk.corpus import stopwords
import json
import nltk
import re

# to be used for exclude_words()
nltk.download('stopwords')
exclude = stopwords.words('english')
common_words = ['logo', 'logos', 'hd', 'png', 'svg', 'jpg', 'jpeg', 'home', 'homepage', 'website', 'hd', 'free', 'vector', 'dot', 'gifs', 'vertical', 'language', 'download', 'white', 'black', 'color', 'rgb', 'cmyk', 'index', 'rectangle', 'transparent', 'square', 'header', 'footer', 'screenshot']

data_keys = ['url_tail', 'header', 'search_value', 'alt']

def clean(s):
    # lowercase
    s = s.lower()
    
    # remove chars that are:
    #   ^\w: NOT word char (not alphanumeric)
    #   ^\s: NOT space
    #   ^. : NOT period
    #   |_ : OR underscore
    s = re.sub(r'[^.\w\s]|_', ' ', s)
    
    # remove excess spaces
    s = re.sub(' +', ' ', s)
    s = '\n'.join(line.strip().rstrip('.') for line in s.split('\n'))

    return s

def form_sentences(s, min_tokens=3, min_token_len=1):
    sentences = []

    # split by '.' and '\n' to get sentences
    s = s.replace('. ', '\n').replace('.\n', '\n')
    for sent in s.split('\n'):
        # tokens = space separated words in a sentence
        # e.g., 'this is an apple' has 4 tokens
        # Condition 1) a sentnece must have at least min_tokens (3) tokens
        # Condition 2) each token must be of min_token_len (1)
        tokens = [t for t in sent.split() if len(t) >= min_token_len]
        if len(tokens) >= min_tokens:
            sentences.append(' '.join(tokens))

    return sentences

# if path is image file, return it's extension
# else return ""
def find_ext(path):
    lower = path.lower()
    if path:
        for ext in ['.png', '.jpg', '.jpeg']:
            if lower.endswith(ext):
                return ext
            elif ext in lower:
                for idx in [x.end() for x in re.finditer(ext, lower)]:
                    if idx < len(lower) and not lower[idx].isalnum():
                        return ext

    return ''

# return cleaned, tail segment of a URL
# mainly for getting image filenames
def get_url_tail(s):
    ext = find_ext(s)
    s = s.split(ext)[0].split('/')[-1]
    if s:
        s = s.lower()
        s = s.replace('%20', ' ')
        s = re.sub(r'[^.\w\s]|_', ' ', s)
        s = [w for w in s.split() if w.replace('.', '').isalpha()]

        return ' '.join(s)
    
    return ''

# remove words from a list that are found inside exclude_list
def exclude_words(words, exclude_list):
    if isinstance(words, str):
        return ' '.join([word for word in words.split() if word.lower() not in exclude_list])
    elif isinstance(words, list):
        return [word for word in words if word.lower() not in exclude_list]

# Display header
def print_header(header):
    print('+-'+ len(header)*'-' + '-+')
    print(f'| {header} |')
    print('+-'+ len(header)*'-' + '-+')

def clients_from_json(file, company):
    results = {
        'url': [],
        'page': [],
        'alt': [],
        'url_tail': [],
        'common': []
    }
    exclude_list = exclude + [company.lower()]
    print_header(company)

    with open(file) as f:
        data = json.load(f)
        # each item inside the JSON file is an object containing client data
        for logo in list(data.keys()):
            data[logo]['url_tail'] = get_url_tail(data[logo]['url'])

            # form bigrams and trigrams from client data
            sentence_stream = []
            for data_key in data_keys:
                data_value = data[logo][data_key]
                if data_value:
                    data_value = data_value.replace('-', '_').replace(' ', '_')
                    sentence_stream.append(exclude_words(data_value.split('_'), common_words))

            bigrams = Phrases(sentence_stream, min_count=1, threshold=1, delimiter='_')
            bigram_text = [bigrams[sentence] for sentence in sentence_stream]
            trigrams = Phrases(bigram_text, min_count=1, threshold=1, delimiter='_')
            trigram_text = [trigrams[sentence] for sentence in bigram_text]

            # replace phrases in client data with bigrams / trigrams with delimiter "_"
            # E.g., "colruyt group is a belgian" => "colruyt_group is a belgian"
            for data_key in data_keys:
                data_value = data[logo][data_key]
                if data_value:
                    data[logo][data_key] = ' '.join(trigram_text.pop(0))

            # 1) find most common words
            # 2) extend abbreviations to full forms
            text = []
            freq = {}
            for key in data_keys:
                text += data[logo][key].split()

            text = [word for word in text if len(word)>=2]
            text = exclude_words(text, exclude_list)

            # create freq list of words & phrases
            for word in sorted(list(set(text)), key=len, reverse=True):        
                freq[word] = 0
                for cmp in text:
                    if word == cmp:
                        freq[word] += 1
                    # if current word/phrase is deemed to be a subset of a longer word/phrase, 
                    # transfer the frequency of the smaller word/phrase to the longer one.
                    # We transfer frequency because they have the same root form.
                    # This procedure will extend abbreviations & short forms to full forms
                    elif len(cmp) > len(word) and word == cmp[:len(word)]:
                        if cmp in freq:
                            freq[cmp] += freq[word] + 1
                        else:
                            freq[cmp] = freq[word] + 1
                        freq.pop(word)
                        word = cmp

            # extract the most frequent word/phrase as client name
            # if multiple words/phrases with same frequency, concatenate them together
            client = ''
            if freq:
                max_freq = max(list(freq.values()))
                for token in freq:
                    if freq[token] == max_freq and token.lower() not in client.lower().split():
                        client += token + ' '

            results['url'].append(data[logo]['url'])
            results['url_tail'].append(exclude_words(data[logo]['url_tail'], exclude_list))
            results['alt'].append(exclude_words(data[logo]['alt'], exclude_list))
            results['page'].append(data[logo]['page'])
            results['common'].append(client.strip())

    # remove irrelevant decorators like the "index_" in "index_google" & "index_samsung" from client names
    for tier in ['alt', 'url_tail', 'common']:
        client_freq = {} 
        clients = results[tier]
        
        for client in clients:
            for word in client.split():
                if word not in client_freq:
                    client_freq[word] = 0
                client_freq[word] += 1
        
        for freq_word in list(client_freq.keys()):
            # keep words in client_freq that appear in >50% of the dict. Otherwise pop
            if client_freq[freq_word] < max(2, len(list(data.keys()))//2):
                client_freq.pop(freq_word)
        
        # leftover words in client_freq are the duplicate decorators
        if client_freq:
            for freq_word in client_freq:
                print('Duplicate:', freq_word)
                for i in range(len(clients)):
                    # remove decorators
                    if freq_word in clients[i]:
                        clients[i] = clients[i].replace(freq_word, '')
                        clients[i] = ' '.join(clients[i].split())

        results[tier] = clients
        
    for i in range(len(results['url'])-1, -1, -1):
        if results['alt'][i] == results['url_tail'][i] == results['common'][i] == results['common'][i] == '':
            results['url'] = results['url'][:i] + results['url'][i+1:]
            results['page'] = results['page'][:i] + results['page'][i+1:]
            results['alt'] = results['alt'][:i] + results['alt'][i+1:]
            results['url_tail'] = results['url_tail'][:i] + results['url_tail'][i+1:]
            results['common'] = results['common'][:i] + results['common'][i+1:]

    return results

def print_clients(results):
    for i in range(len(results[list(results.keys())[0]])):
        print('[1]', results['alt'][i])
        print('[2]', results['url_tail'][i])
        print('[3]', results['common'][i])

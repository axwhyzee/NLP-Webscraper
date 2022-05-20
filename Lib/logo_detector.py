from img_processing import *
from tensorflow import keras
from PIL import Image
from genpath import *
import numpy as np
import requests
import cv2
import os

class LogoDetector():
    def __init__(self):
        self.models = [keras.models.load_model(os.path.join(os.getcwd(), 'Lib', 'model_A')), # model A
                       keras.models.load_model(os.path.join(os.getcwd(), 'Lib', 'model_B'))] # model B

        self.dims = [(100, 100, 3), # i/p dimensions A
                     (200, 200, 3)] # i/p dimensions B
        
        self.num_models = len(self.models)
        
    def prepare_img(self, src):
        paths = []
        img_data = []
        ext = find_ext(src)
        try:
            r = requests.get(src, stream=True).content
            path = gen_path(ext)
            paths.append(path)
            with open(path, 'wb') as handler:
                handler.write(r)
        except Exception as e:
            print('[Download Fail]', e)
            return [], []

        img = Image.open(paths[0])
        for i in range(self.num_models):
            dup = None
            path = gen_path(ext)
            
            if self.dims[i][2] == 3:
                dup = img.convert('RGB')
                
            dup = img.resize((self.dims[i][0], self.dims[i][1]))
            dup.save(path)
            paths.append(path)

            img_data.append(cv2.imread(path))
        
        return img_data, paths

    def predict(self, srcs):
        all_img_data = []
        preds = []
        for src in srcs:
            img_data, paths = self.prepare_img(src)
            if len(paths) == self.num_models + 1:
                for path in paths:
                    os.remove(path)

                preds.append([])
                for i in range(self.num_models):
                    pred = self.models[i].predict(np.array([img_data[i]]))[0][0]
                    if i==1:
                        pred = 1-pred

                    preds[-1].append(pred)
                print('[P]', preds[-1], src)
        print()
            
        return preds

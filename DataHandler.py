import requests
import pandas as pd
import os


class DataHandler:

    def __init__(self):
        pass

    def download(self, x):
        r = requests.get(x)
        file_content = r.text
        directory = os.path.join('downloads', 'Consumption.csv')
        os.makedirs(os.path.dirname(directory), exist_ok=True)
        with open(directory, "w") as f:
            f.write(file_content)

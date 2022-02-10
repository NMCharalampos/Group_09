
import requests
import pandas as pd
import os

from sqlalchemy import null


DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
DIRECTORY = os.path.join('downloads', 'Consumption.csv')

class DataHandler:

    data = null

    def __init__(self):
        pass

    def download(self, x):
        print("download data ... ") #TODO
        r = requests.get(x)
        file_content = r.text
        os.makedirs(os.path.dirname(DIRECTORY), exist_ok=True)
        with open(DIRECTORY, "w") as f:
            f.write(file_content)

    def load_data(self):
        if not os.path.isfile(DIRECTORY):
            self.download(DATA_URL)
        
        print("read data ... ")     #TODO
        data = pd.read_csv(DIRECTORY)

        #filter accoringly to task 
        data = data.loc[data['year'] >= 1970].set_index('year')


dataHandler = DataHandler().load_data()


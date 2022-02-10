
import requests
import pandas as pd
import os

from sqlalchemy import null


DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
DIRECTORY = os.path.join('downloads', 'Consumption.csv')

class DataHandler:

    data = pd.DataFrame

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
        self.data = pd.read_csv(DIRECTORY)

        #filter accoringly to task 
        self.data = self.data.loc[self.data['year'] >= 1970].set_index('year')

    def list_countries(self):
        return [country for country in self.data.country.unique()]


dataHandler = DataHandler()
dataHandler.load_data()

print(dataHandler.list_countries())


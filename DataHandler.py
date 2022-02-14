import os
import requests
import pandas as pd
import matplotlib.ticker as mtick

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

    def plot_consumption(self, country, normalize=False):
        if not self.is_country(country):
            return ValueError("This country does not exist.")

        plot_data = self.data[self.data.country == country].filter(regex="consumption")
        if normalize:
            plot_data = plot_data.diff(plot_data.sum(axis=1), axis=0)
        ax = plot_data.plot.area()
        ax.yaxis.set_major_formatter(mtick.PercentFormatter())
        ax.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        return ax

    def is_country(self, country):
        return country in self.list_countries()


dataHandler = DataHandler()
dataHandler.load_data()

dataHandler.plot_consumption('Kosovos')

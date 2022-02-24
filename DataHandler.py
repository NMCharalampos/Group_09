import os
import requests
import pandas as pd
import matplotlib.ticker as mtick
pd.plotting.register_matplotlib_converters()
import matplotlib.pyplot as plt
#%matplotlib inline
import seaborn as sns
import numpy as np

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

        #filter accordingly to task 
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


    def gap_minder(self, year:int):
        """
        Plots information about the relation of gdp, total energy consumption, and population
        Parameters
        --------------
        self: class
            The DataHandler Class itself
        year: integer
            The desired year for the the plot
        Returns:
        --------------
        Nothing. Plots the output to the screen
        """
        if type(year) not in [int]:
            raise TypeError("Variable year is not an integer.")
        plot_data = self.data[self.data.index == year].copy()
        plot_data = plot_data.fillna(0)
        plot_data["total_energy_consumption"] = plot_data.loc[:,plot_data.columns.str.contains('consumption')].sum(axis=1)
        
        plt.figure(dpi=120)
        np_pop = np.array(plot_data.population)
        
        
        sns.scatterplot(x=plot_data.gdp, y=plot_data.total_energy_consumption, hue = plot_data.country, size = np_pop, sizes=(20,900), legend=False)
        
        plt.grid(True)
        plt.xscale('log')
        plt.xlabel('GDP')
        plt.ylabel('Total energy consumption')
        x_ticks = []
        x_tick_1=100_000_000
        for _ in range(8):
            x_ticks.append(x_tick_1)
            x_tick_1 = x_tick_1* 10
            
        
        plt.xticks(x_ticks)
        plt.yticks([50000,10000, 100000,200000, 300000, 400000])
        plt.show()

dataHandler = DataHandler()
dataHandler.load_data()
dataHandler.plot_consumption('Kosovos')
dataHandler.gap_minder(2003)



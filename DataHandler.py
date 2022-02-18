import os
import requests
import pandas as pd
import matplotlib.ticker as mtick
pd.plotting.register_matplotlib_converters()
import matplotlib.pyplot as plt
%matplotlib inline
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


    def gap_minder(self, year):
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
            
            plot_data_6 = self.data[self.data.index == year].copy()
            plot_data_6 = plot_data_6.fillna(0)
            plot_data_6["total_energy_consumption"] = plot_data_6["biofuel_consumption"] + plot_data_6["coal_consumption"] + plot_data_6["fossil_fuel_consumption"] + plot_data_6["gas_consumption"] + plot_data_6["hydro_consumption"] + plot_data_6["low_carbon_consumption"] + plot_data_6["nuclear_consumption"] + plot_data_6["oil_consumption"] +  plot_data_6["other_renewable_consumption"] + plot_data_6["primary_energy_consumption"] + plot_data_6["renewables_consumption"] + plot_data_6["solar_consumption"] + plot_data_6["wind_consumption"]
            
            plt.figure(dpi=120)
            np_pop = np.array(plot_data_6.population)
            np_pop2 = np_pop*2
            
            sns.scatterplot(plot_data_6.gdp, plot_data_6.total_energy_consumption, hue = plot_data_6.country, size = np_pop2, sizes=(20,900), legend=False )
            
            plt.grid(True)
            plt.xscale('log')
            plt.xlabel('GDP')
            plt.ylabel('Total energy consumption')
            plt.xticks([100000000, 1000000000,10000000000, 100000000000, 1000000000000,10000000000000,100000000000000,1000000000000000])
            plt.yticks([50000,10000, 100000,200000, 300000, 400000])
            plt.show()
        



dataHandler = DataHandler()
dataHandler.load_data()

dataHandler.plot_consumption('Kosovos')

dataHandler.gap_minder(2003)



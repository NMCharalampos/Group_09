import os
from typing import List
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick
import requests
import pandas as pd
import seaborn as sns
import numpy as np

DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
DIRECTORY = os.path.join('downloads', 'Consumption.csv')

class DataHandler:

    """
    ...TBD...
    Methods
    --------
    compare_consumption()
        Plots the total sum of each energy consumption column
        for countries selected in '*countries' as a bar chart.

    gdp()
        Plots the GDP column over the years for
        countries selected in '*countries' as a line chart.

    """

    data = pd.DataFrame

    def __init__(self):
        pass

    def download(self, url: str) -> None:
        """downloads the given web resource and saves it to a file
            the file and subfolder will be created if not already existent
        Args:
            url (str): url of the web resource
        """
        print("download data ... ")
        request = requests.get(url)
        file_content = request.text
        os.makedirs(os.path.dirname(DIRECTORY), exist_ok=True)
        with open(DIRECTORY, "w") as file:
            file.write(file_content)

    def load_data(self) -> None:
        """loads the contents of a file into the attribute of this object
            also filters data to the year after 1970
        """
        if not os.path.isfile(DIRECTORY):
            self.download(DATA_URL)
        print("read data ... ")
        self.data = pd.read_csv(DIRECTORY)

        #filter accordingly to task
        self.data = self.data.drop('renewables_consumption', 1)
        self.data = self.data.loc[self.data['year'] >= 1970].set_index('year')

    def list_countries(self) -> List[str]:
        """returns a list of all countries in the data set
        Returns:
            List[str]: list of unique countries
        """
        return [country for country in self.data.country.unique()]

    def plot_consumption(self, country: str, normalize: bool=False) -> matplotlib.axes.Axes:
        """plots the energy consumption of the specified country
        Args:
            country (str): country
            normalize (bool, optional): values are normalized. Defaults to False.
        """
        if not self.is_country(country):
            return ValueError("This country does not exist.")

        plot_data = self.data[self.data.country == country].filter(regex="consumption")
        if normalize:
            plot_data = plot_data.diff(plot_data.sum(axis=1), axis=0)
        plot = plot_data.plot.area()
        plot.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))
        return plot

    def is_country(self, country: str) -> bool:
        """checks wether a country is contained in the data set

        Returns:
            bool: True if country is in the data set
        """
        return country in self.list_countries()

    def compare_consumption(self,*countries:str):
        """

        Plots the total sum of each energy consumption column
        for countries selected in '*countries' as a bar chart.

        Parameters
        ---------------
        *countries: string
            Countries that shall be plotted

        Returns
        ---------------
        Nothing. Plots sum of different energy consumption per country in a bar chart.

        """
        consumption = pd.DataFrame()
        countries_list = []
        for country in countries:
            if not self.is_country(country):
                return ValueError("Country " + country + " does not exist.")
            countries_list.append(country)
            dfc = self.data.loc[self.data["country"] == country].filter(regex='consumption').sum()
            consumption = consumption.append(dfc, ignore_index = True)
            consumption.index = countries_list
        ax2 = consumption.plot.bar(rot=0)
        ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    def gdp(self, *countries:str):
        """

        Plots the GDP column over the years for
        countries selected in '*countries' as a line chart.

        Parameters
        ---------------
        *countries: string
            Countries that shall be plotted

        Returns
        ---------------
        Nothing. Plots GDP over the years per country in a line chart.

        """
        self.data = self.data.reset_index()
        for country in countries:
            if not self.is_country(country):
                return ValueError("Country " + country + " does not exist.")
            df_gdp = self.data.loc[self.data["country"] == country][['country','gdp','year']]
            plt.plot(df_gdp['year'],df_gdp['gdp'], label = country)
        plt.title('GDP Development')
        plt.xlabel('Year')
        plt.ylabel('GDP (in billion USD)')
        plt.legend()
        plt.show()

    def gap_minder(self, year:int) -> None:
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
        plot_data["total_energy_consumption"] = plot_data.filter(regex='consumption').sum(axis=1)

        plt.figure(dpi=120)
        np_pop = np.array(plot_data.population)

        sns.scatterplot(
            x=plot_data.gdp,
            y=plot_data.total_energy_consumption,
            hue = plot_data.country,
            size = np_pop,
            sizes=(20,900),
            legend=False)

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
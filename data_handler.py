import os
from typing import List
import matplotlib
from matplotlib import pyplot as plt
import requests
import pandas as pd
import seaborn as sns
import numpy as np

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
        self.load_data()

    def download(self) -> None:
        """downloads the given web resource and saves it to a file
            the file and subfolder will be created if not already existent

        """
        print("download data ... ")

        data_url = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
        request = requests.get(data_url)
        file_content = request.text
        os.makedirs(os.path.dirname(DIRECTORY), exist_ok=True)
        with open(DIRECTORY, "w") as file:
            file.write(file_content)

    def load_data(self) -> None:
        """loads the contents of a file into the attribute of this object
            also filters data to the year after 1970
        """
        if not os.path.isfile(DIRECTORY):
            self.download()
        print("read data ... ")
        self.data = pd.read_csv(DIRECTORY)

        #filter accordingly to task
        self.data = self.data.drop(['renewables_consumption', 'fossil_fuel_consumption', 'primary_energy_consumption', 'low_carbon_consumption'], 1)
        self.data = self.data.loc[self.data['year'] >= 1970].set_index('year')

    def list_countries(self) -> List[str]:
        """returns a list of all countries in the data set
        Returns:
            List[str]: list of unique countries
        """
        return [country for country in self.data.country.unique()]

    def plot_consumption(self, country: str, normalize: bool=False) -> None:
        """plots the energy consumption of the specified country
        Args:
            country (str): country
            normalize (bool, optional): values are normalized. Defaults to False.
        """
        if not self.is_country(country):
            return ValueError("This country does not exist.")

        plot_data = self.data[self.data.country == country].filter(regex="consumption")

        title = "Energy consumption in "+ country
        ylabel = "Energy consumptio in TWh"

        if normalize:
            plot_data = plot_data.div(plot_data.sum(axis=1), axis=0)
            title += " - normalized"
            ylabel = "Energy consumption - relative"
        

        plot = plot_data.plot.area(title= title )

        plot.set_ylabel(ylabel)
        
        plot.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    def is_country(self, country: str) -> bool:
        """checks wether a country is contained in the data set

        Returns:
            bool: True if country is in the data set
        """
        return country in self.list_countries()

    def compare_consumption(self,*countries:str) -> None:
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
        ax2 = consumption.plot.bar(rot=0, title="Comparison of energy consumption")
        ax2.set_ylabel("Energy consumption in TWh")
        ax2.legend(loc='center left', bbox_to_anchor=(1.0, 0.5))

    def gdp(self, *countries:str) -> None:
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

        plot_data = plot_data[~ plot_data["country"].str.contains("World")]
        plot_data = plot_data[~ plot_data["country"].str.contains("Africa")]
        plot_data = plot_data[~ plot_data["country"].str.contains("Europe")]
        plot_data = plot_data[~ plot_data["country"].str.contains("North America")]

        plt.figure(dpi=120)
        np_pop = np.array(plot_data.population)

        sns.scatterplot(
            x=plot_data.gdp,
            y=plot_data.total_energy_consumption,
            alpha=.5,
            palette="muted",
            size = np_pop,
            sizes=(20,900),
            legend=False)

        plt.grid(True)
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel('GDP in $')
        plt.ylabel('Total energy consumption in TWh ')
        x_ticks = []
        x_tick_1=100_000_000
        for _ in range(8):
            x_ticks.append(x_tick_1)
            x_tick_1 = x_tick_1* 10

        plt.xticks(x_ticks)
        plt.yticks([1,10,100,1000,10000,100000])
        plt.title("Gapminder - " + str(year))
        plt.show()

    def enrich_data(self) -> None:
        """enriches dataframe with emission column for each consumption column relevanz ,
        creates column with total emissions
        """   
        #create emission columns
        self.data["biofuel_emission"] = self.data['biofuel_consumption'] * ((1e9 * 1450)/1e6) 
        self.data["coal_emission"] = self.data['coal_consumption'] * ((1e9 * 1000)/1e6)
        self.data["gas_emission"] = self.data['gas_consumption'] * ((1e9 * 455)/1e6) 
        self.data["hydro_emission"] = self.data['hydro_consumption'] * ((1e9 * 90)/1e6)
        self.data["nuclear_emission"] = self.data['nuclear_consumption'] * ((1e9 * 5.5)/1e6) 
        self.data["oil_emission"] = self.data['oil_consumption'] * ((1e9 * 1200)/1e6)
        self.data["solar_emission"] = self.data['solar_consumption'] * ((1e9 * 53)/1e6)
        self.data["wind_emission"] = self.data['wind_consumption'] * ((1e9 * 14)/1e6)
        
        self.data["Emissions_Total"] = self.data['biofuel_consumption'] * ((1e9 * 1450)/1e6) + \
        self.data['coal_consumption'] * ((1e9 * 1000)/1e6) + self.data['gas_consumption'] * ((1e9 * 455)/1e6) + \
        self.data['hydro_consumption'] * ((1e9 * 90)/1e6) + self.data['nuclear_consumption'] * ((1e9 * 5.5)/1e6) + \
        self.data['oil_consumption'] * ((1e9 * 1200)/1e6) + self.data['solar_consumption'] * ((1e9 * 53)/1e6) + \
        self.data['wind_consumption'] * ((1e9 * 14)/1e6)
        
        print(self.data)

from ctypes import alignment
import os
import warnings
from typing import List
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1 import host_subplot
import requests
import pandas as pd
import seaborn as sns
import numpy as np

from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings("ignore")

DIRECTORY = os.path.join('downloads', 'Consumption.csv')

class DataHandler:

    """
    Methods
    --------

    download()
        downloads the given web resource and saves it to a file,
        the file and subfolder will be created if not already existent

    load_data()
        loads the contents of a file into the attribute of this object,
        calls clean_data and enrich_date function

    clean_data()
        filters to years before 2020 and after 1970,
        converts year to datetime format and sets it as index,
        drops aggregated "_consumption" columns,
        drops "_consumption" columns irrelevant for energy mix analysis,
        creates column with total consumption,
        fills NaN values with 0

    enrich_data()
        enriches cleaned dataframe with emission column for each consumption column,
        creates column with total emissions

    list_countries()
        returns a list of all countries in the data set

    is_country()
        checks wether a country is contained in the data set

    plot_consumption()
        plots the energy consumption of the specified country

    compare_consumption()
        Plots the total sum of each energy consumption column for countries selected in '*countries' as a bar chart

    gdp()
        Plots the GDP column over the years for
        countries selected in '*countries' as a line chart

    gap_minder()
        Plots information about the relation of gdp (x-axis), total energy consumption (y-axis), and population (size)

    scatter_plot()
        Plots relation between energy consumption (x-axis), emission (y-axis) and population (size) in a scatter plot

    arima_predict()
        Plots the predicted emissions and consumption over a specified period of years of
        a country selected in 'country' as two line charts

    """

    data = pd.DataFrame

    def __init__(self):
        self.load_data()

    def download(self) -> None:
        """downloads the given web resource and saves it to a file,
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
        """loads the contents of a file into the attribute of this object,
            calls clean_data and enrich_date function
        """
        if not os.path.isfile(DIRECTORY):
            self.download()
        print("read data ... ")
        self.data = pd.read_csv(DIRECTORY)

        self.clean_data()
        self.enrich_data()

    def clean_data(self) -> None:
        """filters to years before 2020 and after 1970,
         drops continents and areas that are no specific country,
        converts year to datetime format and sets it as index,
        drops aggregated "_consumption" columns,
        drops "_consumption" columns irrelevant for energy mix analysis,
        creates column with total consumption,
        fills NaN values with 0
       
        """

        self.data = self.data.loc[self.data['year'] >= 1970]
        self.data = self.data.loc[self.data['year']<2020]


        self.data = self.data[~ self.data["country"].str.contains("Europe|Africa|Central America|Asia Pacific|Middle East|OPEC|World|CIS"]
        self.data = self.data[~ self.data["country"].str.contains("Other Asia & Pacific|North America|Other CIS|Other Caribbean|Western Africa")]
        self.data = self.data[~ self.data["country"].str.contains("Other Middle East|Other Northern Africa|Middle Africa|")]
        self.data = self.data[~ self.data["country"].str.contains("Other South America|South & Central America|Other Southern Africa")]
    
        self.data["year"] = pd.to_datetime(self.data['year'], format='%Y').dt.strftime('%Y')
        # self.data = self.data.drop("year", axis=1)
        self.data.set_index('year', inplace=True)

        self.data = self.data.drop(["renewables_consumption", "fossil_fuel_consumption", "low_carbon_consumption", \
                                    "primary_energy_consumption" ,"other_renewable_consumption"], axis=1)

        self.data["Consumption_Total"]=self.data.filter(regex='consumption').sum(axis = 1)

        self.data = self.data.fillna(0)

    def enrich_data(self) -> None:
        """enriches dataframe with emission column for each consumption column relevant ,
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

    def list_countries(self) -> List[str]:
        """returns a list of all countries in the data set

        Returns
        ---------------
        list[str]
            List of unique countries
        """
        return [country for country in self.data.country.unique()]

    def is_country(self, country: str) -> bool:
        """checks wether a country is contained in the data set

        Parameters
        ---------------
        country: string
            Coutry which shall be checked

        Returns
        ---------------
        bool
            True if country is in the data set
        """
        return country in self.list_countries()

    def plot_consumption(self, country: str, normalize: bool=False) -> None:
        """plots the energy consumption of the specified country

        Parameters
        ---------------
        country: string
            Coutry whose consumption shall be plotted
        normalize: bool (optional)
            If True values are normalized. Defaults to False.
        """
        if not self.is_country(country):
            raise ValueError("This country does not exist.")

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

    def compare_consumption(self,*countries:str) -> None:
        """
        Plots the total sum of each energy consumption column for countries selected in '*countries' as a bar chart

        Parameters
        ---------------
        *countries: string
            Countries whose consumption shall be plotted
        """
        consumption = pd.DataFrame()
        emission = pd.DataFrame()

        countries_list = []
        for country in countries:
            if not self.is_country(country):
                raise ValueError("Country " + country + " does not exist.")
            countries_list.append(country)
            dfc = self.data.loc[self.data["country"] == country].filter(regex='consumption').sum()
            dfe = self.data.loc[self.data["country"] == country].filter(regex='emission').sum()

            emission = emission.append(dfe, ignore_index=True)
            consumption = consumption.append(dfc, ignore_index = True)
            consumption.index = countries_list
            emission.index = countries_list

        fig = plt.figure() # Create matplotlib figure

        ax = fig.add_subplot() # Create matplotlib axes
        ax2 = ax.twinx() # Create another axes that shares the same x-axis as ax.

        consumption.plot(kind="bar", ax = ax2 , position = 0, figsize=(10,7), width=0.3, align="center")
        emission.plot(kind="bar", ax = ax , position = 1, figsize=(10,7), hatch="/", width=0.3)

        ax.axes.set_xlim(-0.5, len(countries_list)-0.5)


        ax2.set_ylabel("Energy consumption in TWh")
        ax.legend(loc='center left', bbox_to_anchor=(1.2, 0.85))
        ax2.legend(loc='center left', bbox_to_anchor=(1.2, 0.4))


        ax.set_ylabel('Emission')
  
        plt.show()

    def gdp(self, *countries:str) -> None:
        """
        Plots the GDP column over the years for
        countries selected in '*countries' as a line chart

        Parameters
        ---------------
        *countries: string
            Countries that shall be plotted
        """
        gdp_data = self.data.copy()
        gdp_data.reset_index(inplace=True)
        gdp_data = gdp_data[gdp_data["year"].astype("int") <=2016].copy()

        for country in countries:
            if not self.is_country(country):
                raise ValueError("Country " + country + " does not exist.")
            df_gdp = gdp_data.loc[gdp_data["country"] == country][['country','gdp','year']]
            plt.plot(df_gdp['year'],df_gdp['gdp'], label = country)
        plt.title('GDP Development')
        plt.xlabel('Year 1970 - 2016')
        plt.xticks(color='w')
        plt.ylabel('GDP (in billion USD)')
        plt.legend()
        plt.show()

    def gap_minder(self, year:int) -> None:
        """
        Plots information about the relation of gdp (x-axis), total energy consumption (y-axis), and population (size)

        Parameters
        --------------
        year: integer
            The desired year for the the plot
        """
        if type(year) not in [int]:
            raise TypeError("Variable year is not an integer.")
        plot_data = self.data.copy()
        plot_data = plot_data.reset_index()
        plot_data.year = plot_data.year.astype(int)
        plot_data = plot_data.loc[plot_data.year == year]
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

    def scatter_plot(self) -> None:
        """
        Plots relation between energy consumption (x-axis), emission (y-axis) and population (size) in a scatter plot
        """
        scatter_data = self.data.copy()

        scatter_data = scatter_data.groupby(["country"]).mean()
        scatter_data = scatter_data.drop(index=["World", "Africa","Europe","North America"], axis=0).reset_index()
        plt.figure(figsize=(12, 6))
        for country in self.list_countries():
            df1 = scatter_data.loc[scatter_data["country"] == country]
            plt.scatter(x = df1['Consumption_Total'], y = df1['Emissions_Total'], s = df1['population']/300000, alpha = 0.5)
        plt.xlabel("Consumption Total in TWh")
        plt.ylabel("Emissions in t ")
        plt.show()

    def arima_predict(self, country: str, period: int):
        """
        Plots the predicted emissions and consumption over a specified period of years of
        a country selected in 'country' as two line charts

        Parameters
        ---------------
        country: string
            Country whose prediction shall be plotted
        period: int
            Number of predicted years
        """

        i=0
        if type(period) not in [int] or period <1:
            raise TypeError("Variable period is not an integer above zero.")
    
        if not self.is_country(country):
           raise ValueError("This country does not exist.")
        
        arima_df = self.data[['country','Consumption_Total','Emissions_Total']].copy()
        arima_df = arima_df.loc[arima_df["country"] ==country]
        
        df_emissions = arima_df.drop(["country", "Consumption_Total"], axis=1)
        df_emissions = df_emissions.rename(columns= {"Emissions_Total": "value"}) 
        df_emissions = df_emissions.reset_index()
        
        df_consumption = arima_df.drop(["country", "Emissions_Total"], axis=1)
        df_consumption = df_consumption.rename(columns= {"Consumption_Total": "value"})
        df_consumption = df_consumption.reset_index()
    
        legends = ["Predicted Consumption", "Predicted Emission"]
        prediction_total = pd.DataFrame()

        fig , axes = plt.subplots(nrows=1,ncols=2, figsize=(20, 10))
        for df in [df_consumption, df_emissions]:
            df.year = pd.to_datetime(df.year, format='%Y')
            time_series = df.set_index(df.columns[0])
            npts = 5
            train = time_series[:-npts]

            model = ARIMA(train.values, order=(4, 1, 5), dates=train.index)
            model_fit = model.fit()

            prediction = pd.DataFrame(model_fit.predict(start=48, end=48+period, dynamic=True))
            prediction['Time'] = pd.date_range(start='2020-01-01', periods= period+1, freq='YS')
            prediction.set_index('Time', inplace=True)
            
            prediction= prediction.rename({0: 'value'}, axis=1)
            prediction_total = time_series.append(prediction)
            prediction_total.iloc[40:50].plot(ax=axes[i],kind='line', c ='red')
            prediction_total.iloc[49:].plot(ax=axes[i],kind='line', c ='blue')
            
            plt.legend(['Historical','Prediction'])
    
            axes[i].set_title('Emission of ' + country)
            axes[0].set_title('Consumption of ' + country)

            axes[i].set_ylabel('Emissions in t')
            axes[0].set_ylabel('Consumption in TWh')

            i = i+1
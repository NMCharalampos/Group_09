from statsmodels.tsa.arima.model import ARIMA
import os
from typing import List
import matplotlib as plt
import matplotlib.ticker as mtick
import requests
import pandas as pd

DATA_URL = "https://raw.githubusercontent.com/owid/energy-data/master/owid-energy-data.csv"
DIRECTORY = os.path.join('downloads', 'Consumption.csv')

class DataHandler:

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
            self.download()
        print("read data ... ")
        self.data = pd.read_csv(DIRECTORY)

        #filter accordingly to task
        #self.data = self.data.drop(['renewables_consumption', 'fossil_fuel_consumption', 'primary_energy_consumption', 'low_carbon_consumption'], 1)
        self.data = self.data.loc[self.data['year'] >= 1970]
        self.data = self.data.loc[self.data['year']<2020]
        
        # convert year to datetime and set as index
        self.data["Year"] = pd.to_datetime(self.data['year'], format='%Y').dt.strftime('%Y')
        self.data = self.data.drop("year", axis=1)
        self.data.set_index('Year', inplace=True)

    def clean_data(self) -> None:
        """drops aggregated "_consumption" columns,
        drops "_consumption" columns irrelevant for energy mix analysis,
        creates column with total consumption,
        fills NaN values with 0
        """
        
        #drop aggregated and irrelevant consumption columns
        self.data = self.data.drop(["renewables_consumption", "fossil_fuel_consumption", "low_carbon_consumption", \
                                    "primary_energy_consumption"], axis=1)
        
        #select consumption columns, create total column and fill NaN values with 0
        self.data = self.data[["country","biofuel_consumption","coal_consumption","gas_consumption",\
                               "hydro_consumption","nuclear_consumption","oil_consumption","other_renewable_consumption",\
                               "solar_consumption","wind_consumption", "population"]]
        self.data["Consumption_Total"]=self.data.filter(regex='consumption').sum(axis = 1)
        self.data = self.data.fillna(0)
        
        
        return self.data

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
        plot.yaxis.set_major_formatter(mtick.PercentFormatter())
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

    def enrich_data(self) -> None:
        """enriches dataframe with emission column for each consumption column relevanz ,
        creates column with total emissions
        """   
        dataHandler = DataHandler()
        self.data = dataHandler.clean_data() 
        
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
        
        return self.data

    def arima_predict(self, country, period):
        """
    
        Plots the predicted emissions and consumption over a specified period of years of
        a country selected in 'country' as two line charts.

        Parameters
        ---------------
        country: string
            Country that shall be plotted
        
        period: int
            Number of predicted years

        Returns
        ---------------
        Nothing. Plots emissions and consumption over a specified period of years.

        """
        dataHandler = DataHandler()
        self.data = dataHandler.enrich_data()
        i=0
        if type(period) not in [int] or period <1:
            raise TypeError("Variable period is not an integer above zero.")
    
        if not self.is_country(country):
            return ValueError("This country does not exist.")
        
        arimaDF = self.data[['country','Consumption_Total','Emissions_Total']]
        arimaDF = arimaDF.loc[arimaDF["country"] ==country]
        
        ####### Create two dataframes #######
        dfEmissions = arimaDF.drop(["country", "Consumption_Total"], axis=1)
        dfEmissions = dfEmissions.rename(columns= {"Emissions_Total": "value"}) 
        dfEmissions = dfEmissions.reset_index()

        dfConsumption = arimaDF.drop(["country", "Emissions_Total"], axis=1)
        dfConsumption = dfConsumption.rename(columns= {"Consumption_Total": "value"})
        dfConsumption = dfConsumption.reset_index()

        legends = ["Predicted Consumption", "Predicted Emission"]
        colors= ["red","blue"]
        ####### Prepare for arima #############
        fig, axes = plt.subplots(nrows=1,ncols=2, figsize=(20, 10)) 
        for df in [dfConsumption, dfEmissions]:
            time_series = df.set_index(df.columns[0])
            npts = 5 
            train = time_series[:-npts]
            test = time_series[-npts:]

            model = ARIMA(train.values, order=(5, 1, 5), dates=train.index)
            model_fit = model.fit()
            forecast_data =  model_fit.predict(len(train), len(train)+npts-1)
            forecast_index = test.index
            forecast = pd.Series(data=forecast_data, index=forecast_index)
            prediction = pd.DataFrame(model_fit.predict(start=48, end=48+period, dynamic=True))
            prediction['Time'] = pd.date_range(start='2020-01-01', periods= period+1, freq='YS')
            prediction.set_index('Time', inplace=True)


            prediction.plot(ax=axes[i],kind='line', c = colors[i])
            axes[i].set_title('Emission')
            axes[0].set_title('Consumption')
            axes[i].legend(title=legends[i])
            i = i+1


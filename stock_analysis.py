"""
    
    __author__ = Ali Nawaz Maan
    student number = 44688813
    __email__ = a.maan@uq.net.au
"""

import stocks


class LoadCSV(stocks.Loader):
    """
    Loading class for CSV files. It is inherited from Loader class and overwrites init and _process methods.
    """

    def __init__(self, filename, stocks) :
        """Data is loaded on object creation.

        Parameters:
            filename (str): Name of the file from which to load data.
            stocks (StockCollection): Collection of existing stock market data
                                      to which the new data will be added.
        """
        super().__init__(filename, stocks)
        try:
            with open(filename, "r") as file :
                # Use format specific subclass to parse the data in the file.
                self._process(file)
        except RuntimeError:
            raise RuntimeError


    def _process(self, file):
        """
        Process the loaded CSV file, get the trading data and add it into appropriate stocks object and an instance
        of StockCollection Class.

            Parameter (file):
                Read the file line-by-line and extract the data.
                
            Assumptions: Dates are valid if they contain exactly 8 numerical characters.
                        Prices need only be valid non-negative floats, and volume must be
                        a positive integer.
        """
        for line in file:
            line = line.strip()
            try:
                stock_code, date, opening_price, high_price, low_price, closing_price, volume = line.split(",")
                stock = self._stocks.get_stock(stock_code)

                # Trading data Object
                day_data = stocks.TradingData(date, float(opening_price), float(high_price), float(low_price),
                                              float(closing_price), int(volume))
            except Exception:
                raise RuntimeError

            stock.add_day_data(day_data)    # Add trading data into appropriate stock object


class LoadTriplet(stocks.Loader):
    """
    Loading class for Triplet files. It is inherited from Loader class and overwrites init and _process methods.

    """
    def __init__(self, filename, stocks) :
        """Data is loaded on object creation.

        Parameters:
            filename (str): Name of the file from which to load data.
            stocks (StockCollection): Collection of existing stock market data
                                      to which the new data will be added.
        """
        super().__init__(filename, stocks)
        try:
            with open(filename, "r") as file :
                # Use format specific subclass to parse the data in the file.
                self._process(file)
        except RuntimeError:
            raise RuntimeError


    def _process(self, file):
        """
        Process the loaded Triplet file, get the trading data and add it into appropriate stocks object and an instance
        of StockCollection Class.

            Parameter (file):
                Read the file line-by-line and extract the data.

            Assumption: There must be exactly 6 parameters to a company's particular day's stock data.
        """
        keyword_dict = {'DA': 'date', 'OP': 'opening_price', 'HI': 'high_price', 'LO': 'low_price',
                        'CL': 'closing_price', 'VO': 'volume'}

        counter = 0
        for line in file:
            line = line.strip()
            try:
                code, parameter, value = line.split(":")
                if parameter in keyword_dict.keys():
                    keyword_dict[parameter] = value  # Map the parameter values in keyword dict.
                if counter == 5:
                    stock = self._stocks.get_stock(code)

                    # Trading data Object
                    day_data = stocks.TradingData(keyword_dict.get('DA'), float(keyword_dict.get('OP')),
                                                  float(keyword_dict.get('HI')), float(keyword_dict.get('LO')),
                                                  float(keyword_dict.get('CL')), int(keyword_dict.get('VO')))
                    stock.add_day_data(day_data)
                    counter = 0
                else:
                    counter += 1
            except Exception:
                raise RuntimeError


class HighLow(stocks.Analyser):
    """Determine the highest and lowest price for a single stock."""

    def __init__(self):
        self._high_price_list = []
        self._low_price_list = []

    def process(self, day):
        """
        Determines the high and lowe prices of a stock on a day and append those into the high and low lists.

        Parameters:
            day (TradingData): Trading data for one stock on one day.
        """

        try:
            self._high_price_list.append(day.get_high())
            self._low_price_list.append(day.get_low())
        except Exception:
            raise ValueError

    def reset(self):
        self._high_price_list = []
        self._low_price_list = []

    def result(self):
        """
        Returns a tuple containing highest and lowest stock prices from the high and low lists.
        """

        return (max(self._high_price_list), min(self._low_price_list))


class MovingAverage(stocks.Analyser):
    """Determine the Moving average of a stock for a given number of days."""

    def __init__(self, days):

        self._avg_period = int(days)
        self._closing_price_dict = {}
        self._sum = 0

    def process(self, day):
        """
        Get the date and closing price of a stock and map those into closing prices dict.

        Parameters:
            day (TradingData): Trading data for one stock on one day.
        """
        try:
            self._closing_price_dict[day.get_date()] = day.get_close()
        except Exception:
            raise ValueError

    def reset(self):

        self._closing_price_dict = {}
        self._sum = 0

    def result(self):
        """
        Calculates the moving average of a stock for given number of days.

        Returns:
            Moving average

        """

        all_dates_list = []
        closing_price_list = []
        try:
            for i in sorted(self._closing_price_dict.keys()):
                all_dates_list.append(i)

            days_dates = all_dates_list[-(self._avg_period):]
        except Exception:
            raise ValueError

        for i in days_dates:
            closing_price_list.append(self._closing_price_dict[i])

        return sum(closing_price_list) / self._avg_period

class GapUp(stocks.Analyser):
    """
    Finds most recent day in the trading data where the stock’s opening price was
    significantly higher than its previous day’s closing price
    """

    def __init__(self, delta):

        self._delta = delta
        self._prices_dict = {}

    def process(self, day):
        """
        Maps trading data objects to their respective dates in prices dict.

        Parameters:
            day (TradingData): Trading data for one stock on one day.
        """

        try:
            self._prices_dict[day.get_date()] = day
        except Exception:
            raise ValueError
    def reset(self):

        self._prices_dict = {}

    def result(self):
        """
        Returns the GapUp date for a particular stock.

        Returns:
            Trading data object for a GapUp Stock
        """
        try:
            dates = sorted(self._prices_dict.keys())
        except Exception:
            raise ValueError
        price_to_compare = 0.0
        gapup_date = ""
        for i in reversed(dates):

            opening = self._prices_dict[i].get_open()
            closing = self._prices_dict[i].get_close()
            if price_to_compare == 0.0:
                pass
            elif price_to_compare - closing >= self._delta:
                return self._prices_dict.get(gapup_date)

            gapup_date = i
            price_to_compare = opening
        return None



def example_usage () :
    all_stocks = stocks.StockCollection()
    LoadCSV("data_files/march1.csv", all_stocks)
    LoadCSV("data_files/march2.csv", all_stocks)
    LoadCSV("data_files/march3.csv", all_stocks)
    LoadCSV("data_files/march4.csv", all_stocks)
    LoadCSV("data_files/march5.csv", all_stocks)
    LoadTriplet("data_files/feb1.trp", all_stocks)
    LoadTriplet("data_files/feb2.trp", all_stocks)
    LoadTriplet("data_files/feb3.trp", all_stocks)
    LoadTriplet("data_files/feb4.trp", all_stocks)
    volume = stocks.AverageVolume()
    stock = all_stocks.get_stock("ADV")
    stock.analyse(volume)
    print("Average Volume of ADV is", volume.result())
    high_low = HighLow()
    stock.analyse(high_low)
    print("Highest & Lowest trading price of ADV is", high_low.result())
    moving_average = MovingAverage(10)
    stock.analyse(moving_average)
    print("Moving average of ADV over last 10 days is {0:.2f}"
          .format(moving_average.result()))
    gap_up = GapUp(0.011)
    stock = all_stocks.get_stock("YOW")
    stock.analyse(gap_up)
    print("Last gap up date of YOW is", gap_up.result().get_date())



if __name__ == "__main__" :
    example_usage()
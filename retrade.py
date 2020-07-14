# Retrade: Monitors the stock market and places trades automatically.

from datetime import datetime
from yahoo_fin import stock_info # Import stock_info module from yahoo_fin


# Get data from user
ticker = input("Ticker to monitor: ").lower() # The stock to monitor
interval = int(input("Time between price checks (seconds): ")) # Number of seconds between each request
duration = int(60 * float(input("Time until the computer stops monitoring (minutes): "))) # Duration of computer service (multiplied to convert to seconds)
trade_type = input("Trade type (leave blank for 'trailing sell'): ") # Type of trade to execute


# Calculate the finishing time for the service
finish_time = datetime.now() + timedelta(seconds=duration)


# Branch out into different trade methods

if trade_type == "trailing sell" or trade_type == "":

    # Loop until duration reached (or forever if no duration specified)
    while datetime.now() < finish_time or duration == 0:


        # Get live price of stock
        live_price = stock_info.get_live_price(ticker)

        print(live_price)
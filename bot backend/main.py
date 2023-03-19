from neural_intents import GenericAssistant
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import pickle
import sys
import datetime as dt
import plotly.graph_objects as go

with open('portfolio.pkl', 'rb') as f:
    portfolio = pickle.load(f)

print(portfolio)


def save_portfolio():
    with open('portfolio.pkl', 'wb') as f:
        pickle.dump(portfolio, f)


def add_portfolio():
    stock = input("Which stock do you want to add: ")
    amount = input("How many shares do you want to add: ")

    if stock in portfolio.keys():
        portfolio[stock] += int(amount)
    else:
        portfolio[stock] = int(amount)

    save_portfolio()


def remove_portfolio():
    stock = input("Which stock do you want to sell: ")
    amount = input("How many shares do you want to sell: ")

    if stock in portfolio.keys():
        if amount <= portfolio[stock]:
            portfolio[stock] -= amount
            save_portfolio()
        else:
            print(f"You don't have enough shares of {stock}")
    else:
        print(f"You don't have any shares of {stock}")


def show_portfolio():
    print("Your portfolio: ")
    for stock in portfolio.keys():
        print(f"You own {portfolio[stock]} shares of {stock}")


def portfolio_worth():
    sum = 0
    for stock in portfolio.keys():
        data = yf.download(stock, start=dt.datetime.now() - dt.timedelta(days=1),
                           end=dt.datetime.now())
        price = data['Close'].iloc[-1]
        sum += price
    print(f"Your portfolio is worth ${sum}")


def portfolio_gains():
    starting_date = input("Enter a date for comparison (YYYY-MM-DD): ")
    sum_now = 0
    sum_then = 0

    try:
        for stock in portfolio.keys():
            data = yf.download(stock, start=starting_date,
                               end=dt.datetime.now())
            price_now = data['Close'].iloc[-1]
            price_then = data.loc[data.index ==
                                  starting_date]['Close'].values[0]
            sum_now += price_now
            sum_then += price_then
        print(f"Relative Gains: {((sum_now - sum_then)/sum_then)*100}")
        print(f"Absolute Gains: ${sum_now - sum_then}")

    except IndexError:
        print("There was no trading on this day")


def plot_chart():
    stock = input("Choose a stock symbol: ")
    starting_string = input("Choose a starting date (DD/MM/YYYY): ")
    interval_ = input("Enter intervals(Eg: 1h, 15m): ")

    plt.style.use('dark_background')

    start_ = dt.datetime.strptime(starting_string, "%d/%m/%Y")
    end_ = dt.datetime.now()

    df = yf.download(stock, start=start_, end=end_, interval=interval_)
    print(df)
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
    fig.show()


def bye():
    print("Goodbye")
    sys.exit(0)


mappings = {
    'plot_chart': plot_chart,
    'add_portfolio': add_portfolio,
    'remove_portfolio': remove_portfolio,
    'show_portfolio': show_portfolio,
    'portfolio_worth': portfolio_worth,
    'portfolio_gains': portfolio_gains,
    'bye': bye
}

assistant = GenericAssistant(
    'intents.json', mappings, "financial_assitant_model")

assistant.train_model()
assistant.save_model()

while True:
    message = input("")
    assistant.request(message)

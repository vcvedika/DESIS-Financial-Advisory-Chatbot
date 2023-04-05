import os
from neural_intents import GenericAssistant
import matplotlib.pyplot as plt
import yfinance as yf
import pickle
import sys
import datetime as dt
import plotly.graph_objects as go
import telebot
from io import StringIO
import pandas as pd
import numpy as np

# Your own bot token
BOT_TOKEN = "6139937589:AAEPEhmEBgPcpv--RGLCIPNPoMQsCufhH9U"

bot = telebot.TeleBot(BOT_TOKEN)
portfolio = {}
name = ''
goal = 0
file_name = ''

users = {
    'Aastha': 'aastha_portfolio.pkl',
    'Dakshita': 'dakshita_portfolio.pkl',
    'Pranjal': 'pranjal_portfolio.pkl',
    'Soumi': 'soumi_portfolio.pkl',
    'Vedika': 'vedika_portfolio.pkl'
}


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    global name
    name = bot.send_message(
        message.chat.id, "Hi there, please enter your name")
    bot.register_next_step_handler(name, name_handler)


def name_handler(message):
    global portfolio
    global name
    global file_name
    name = message.text
    print(name)
    if name in users:
        file_name = str(name).lower() + '_portfolio.pkl'
        with open(file_name, 'rb') as f:
            portfolio = pickle.load(f)
            bot.reply_to(message, f"Welcome back, {name}")
    else:
        file_name = str(name).lower() + '_portfolio.pkl'
        open(file_name, 'wb')
        portfolio = {}
        users[name] = file_name
        bot.reply_to(message, f"Welcome, {name}")
    print(file_name)


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    print(f"Received message: {message.text}")
    add_reply, prob, reply_msg = assistant.request(message.text, message)
    print(F"Probability: {prob}")
    if add_reply:
        bot.reply_to(message, str(reply_msg))


# ADDING TO PORTFOLIO
def add_portfolio(message):
    stock_name = bot.reply_to(
        message, "Which stock do you want to buy?")
    bot.register_next_step_handler(stock_name, add_stock_name_handler)


def add_stock_name_handler(message):
    stock_name = message.text
    stock_number = bot.reply_to(
        message, f"How many stocks of {stock_name} do you want to buy?")
    bot.register_next_step_handler(
        stock_number, add_stock_number_handler, stock_name)


def add_stock_number_handler(message, stock_name):
    stock_number = message.text
    if stock_name in portfolio.keys():
        portfolio[stock_name] += int(stock_number)
    else:
        portfolio[stock_name] = int(stock_number)
    with open(file_name, 'wb') as adding:
        pickle.dump(portfolio, adding)
    bot.send_message(
        message.chat.id, f"You have bought {stock_number} shares of {stock_name}.")


# REMOVE FROM PORTFOLIO
def remove_portfolio(message):
    stock_name = bot.reply_to(
        message, "Which stock do you want to sell?")
    bot.register_next_step_handler(stock_name, remove_stock_name_handler)


def remove_stock_name_handler(message):
    stock_name = message.text
    stock_number = bot.reply_to(
        message, f"How many stocks of {stock_name} do you want to sell?")
    bot.register_next_step_handler(
        stock_number, remove_stock_number_handler, stock_name)


def remove_stock_number_handler(message, stock_name):
    global name
    stock_number = message.text
    if stock_name in portfolio.keys():
        if int(stock_number) <= portfolio[stock_name]:
            portfolio[stock_name] -= int(stock_number)
        else:
            bot.send_message(
                message.chat.id, f"You don't have enough shares of {stock_name}")
    else:
        bot.send_message(
            message.chat.id, f"You don't have enough shares of {stock_name}")
    for stock, count in list(portfolio.items()):
        if count == 0:
            del portfolio[stock]
    with open(file_name, 'wb') as removing:
        pickle.dump(portfolio, removing)

    bot.send_message(
        message.chat.id, f"You have sold {stock_number} shares of {stock_name}.")


# DISPLAYING PORTFOLIO CONTENTS
def show_portfolio(message):
    if len(portfolio) == 0:
        bot.reply_to(message, "Your portfolio is empty")
    else:
        bot.reply_to(message, "This is your portfolio:")
        for stock in portfolio.keys():
            bot.send_message(
                message.chat.id, f"You own {portfolio[stock]} shares of {stock}")


# DISPLAYING PORTFOLIO VALUE
def portfolio_worth(message):
    if len(portfolio) == 0:
        bot.reply_to(message, "You have no stocks in your portfolio!")
        return
    portfolio_value = 0
    prices = yf.download(list(portfolio.keys()), period="1d")[
        "Adj Close"].iloc[-1]

    portfolio_value = sum(prices * pd.Series(portfolio))
    bot.reply_to(message, f"Your portfolio is worth ${portfolio_value}")


# DISPLAYING PORTFOLIO GAINS OVER TIME
def portfolio_gains(message):
    if len(portfolio) == 0:
        print('You have no stocks in your portfolio!')
        return
    date = bot.reply_to(
        message, "Enter a date for comparison (YYYY-MM-DD): ")
    bot.register_next_step_handler(date, portfolio_gains_handler)


def portfolio_gains_handler(message):
    starting_date = message.text
    sum_now = 0
    sum_then = 0
    try:
        for stock in portfolio.keys():
            data = yf.download(stock, start=starting_date,
                               end=dt.datetime.now())
            price_now = data['Close'].iloc[-1]
            price_then = data.loc[data.index ==
                                  starting_date]['Close'].values[0]
            sum_now += (price_now * portfolio[stock])
            sum_then += (price_then * portfolio[stock])
        bot.reply_to(
            message, f"Relative Gains: {((sum_now - sum_then)/sum_then)*100}")
        bot.reply_to(
            message, f"Absolute Gains: ${sum_now - sum_then}")

    except IndexError:
        bot.reply_to(
            message, "There was no trading on this day")


# DISPLAYING THE CANDLESTICK CHART FOR A STOCK
def plot_chart(message):
    stock_name = bot.reply_to(
        message, "Which stock do you want to plot?")
    bot.register_next_step_handler(stock_name, plotting_handler1)


def plotting_handler1(message):
    stock_name = message.text
    starting_date = bot.reply_to(
        message, "Choose a starting date (DD/MM/YYYY): ")
    bot.register_next_step_handler(
        starting_date, plotting_handler2, stock_name)


def plotting_handler2(message, stock_name):
    starting_date = message.text
    time_interval = bot.reply_to(
        message, "Enter intervals(Eg: 1mo, 1d, 1h, 15m): ")
    bot.register_next_step_handler(
        time_interval, plotting_handler3, stock_name, starting_date)


def plotting_handler3(message, stock_name, starting_date):
    time_interval = message.text
    plt.style.use('dark_background')
    start_ = dt.datetime.strptime(starting_date, "%d/%m/%Y")
    end_ = dt.datetime.now()
    df = yf.download(stock_name, start=start_,
                     end=end_, interval=time_interval)
    print(df)
    fig = go.Figure(data=[go.Candlestick(
        x=df.index, open=df.Open, high=df.High, low=df.Low, close=df.Close)])
    fig.show()


# SAVING MONEY PLAN
def save_money(message):
    # global goal
    reply = bot.reply_to(
        message, "How much money do you want to save? Please enter the value in rupees.")
    bot.register_next_step_handler(reply, command_handle_any_document1)


def command_handle_any_document1(message):
    goal = message.text
    goal = float(goal)
    bot.send_message(
        message.chat.id, "I will also need information regarding your expenses, so please upload your bank statement in csv format.")
    bot.register_next_step_handler(message, command_handle_any_document2, goal)


@bot.message_handler(func=lambda msg: True, content_types=['document'])
def command_handle_any_document2(message, goal):
    # This is a file upload.
    file_url = bot.get_file_url(message.document.file_id)
    print(f"Downloading {file_url}")
    try:
        df = pd.read_csv(file_url)
        str_io = StringIO()
        df.to_html(buf=str_io, classes='table table-striped')
        str_io.seek(0)
        user_adjust_percentage = [0.0, 0.05, 0.10, 0.20]
        user_new_budget = []
        saving = []
        saved_amt = 0
        dict = {"Important": 0, "Non-important": 1,
                "Essential": 2, "Non-Essential": 3}
        user_category_ranking = [0, 0, 0, 0]
        for i in range(len(df['row'])):
            user_category_ranking[dict[df['Class'][i]]] += df['Debit'][i]
        saved = 0
        cred = 0
        deb = 0
        categories = df['Description'].unique()
        existing_expense = {}
        new_expense = {}
        c2 = ["Important", "Non-important",
              "Essential", "Non-Essential", "cumulative"]
        prev_categorywise_expense = {}
        new_categorywise_expense = {}
        for i in c2:
            existing_expense[i] = 0
            new_expense[i] = 0
        for i in categories:
            prev_categorywise_expense[i] = 0
            new_categorywise_expense[i] = 0
        for i in range(len(df['row'])):
            j = dict[df['Class'][i]]
            decrease_amount = user_adjust_percentage[j]
            if (df['Debit'][i] != 0.00):
                current_spending = df['Debit'][i]
                new_budget = float(current_spending) - \
                    (float(current_spending) * decrease_amount)
                saved_amt = round(float(current_spending) * decrease_amount, 2)
                new_budget = round(new_budget, 2)
                user_new_budget.append(new_budget)
                saving.append(saved_amt)
                saved += saved_amt
                deb += current_spending
                existing_expense[df['Class'][i]] += df['Debit'][i]
                new_expense[df['Class'][i]] += new_budget
                prev_categorywise_expense[df['Description']
                                          [i]] += df['Debit'][i]
                new_categorywise_expense[df['Description'][i]] += new_budget
            else:
                cred += df['Credit'][i]
                user_new_budget.append(0.00)
                saving.append(0.00)
        existing_expense["cumulative"] = deb
        new_expense["cumulative"] = deb-saved
        existing_expense_values = list(existing_expense.values())
        new_expense_values = list(new_expense.values())
        x = goal/((cred-deb)+saved)
        x = round(x, 2)
        n = str(x)
        plt.switch_backend('Agg')
        X_axis = np.arange(len(c2))
        plt.bar(X_axis - 0.2, existing_expense_values,
                0.4, label='Current Expenses')
        plt.bar(X_axis + 0.2, new_expense_values,
                0.4, label='Modified Expenses')
        plt.xticks(X_axis, c2)
        plt.xlabel("Expense Categories")
        plt.ylabel("Monthly expense")
        plt.legend()
        plt.savefig('foo.png', bbox_inches='tight')
        plt.close()
        bot.send_photo(chat_id=message.chat.id, photo=open(
            "foo.png", "rb"), caption="Comparison of budgets")
        ans = "Follow the estimated plan for " + n + " months"
        df['Estimated Expense'] = user_new_budget
        df['Saving'] = saving
        df.to_html(buf=str_io, classes='table table-striped')
        str_io.seek(0)
        bot.send_document(message.chat.id, str_io,
                          visible_file_name="analysis_report.html")
        bot.send_message(message.chat.id, "Analysis complete!")
        bot.send_message(message.chat.id, ans)
        return

    except Exception as e:
        print(f"Error in reading file {e}")
        bot.reply_to(
            message, "Cannot read the uploaded file. Please try again.")


# SAY GOODBYE
def bye(message):
    bot.send_message(message.chat.id, "Goodbye!")
    sys.exit(0)


# DEFAULT HANDLER
def default_handler(message):
    bot.reply_to(message, "I did not understand.")


def _initialize_model():

    mappings = {
        'plot_chart': plot_chart,
        'add_portfolio': add_portfolio,
        'remove_portfolio': remove_portfolio,
        'show_portfolio': show_portfolio,
        'portfolio_worth': portfolio_worth,
        'portfolio_gains': portfolio_gains,
        'save_money': save_money,
        'bye': bye,
        None: default_handler
    }

    assistant = GenericAssistant(
        'intents.json', mappings, "financial_assitant_model")

    # assistant.train_model()
    # assistant.save_model()
    assistant.load_model()
    return assistant


assistant = _initialize_model()
print("Started polling")
bot.infinity_polling()

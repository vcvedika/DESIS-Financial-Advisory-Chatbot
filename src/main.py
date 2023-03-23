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

# Your own bot token
BOT_TOKEN = "6198049534:AAHihuaR2zrenr0XaVg6aNHeNEPlf8J5PVg"

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda msg: True)
def echo_all(message):
    print(f"Received message: {message.text}")
    add_reply, prob, reply_msg = assistant.request(message.text, message)
    print(F"Probability: {prob}")
    if add_reply:
        bot.reply_to(message, str(reply_msg))

# Handle document uploads.
@bot.message_handler(func=lambda msg: True, content_types=['document'])
def command_handle_any_document(message):
    # This is a file upload.
    file_url = bot.get_file_url(message.document.file_id)
    print(f"Downloading {file_url}")
    try:
        df = pd.read_csv(file_url)
        str_io = StringIO()
        df.to_html(buf=str_io, classes='table table-striped')
        str_io.seek(0)
        bot.send_document(message.chat.id, str_io, visible_file_name="analysis_report.html")
        bot.send_message(message.chat.id, "Analysis complete!")
        return
    except Exception as e:
        print(f"Error in reading file {e}")
        bot.reply_to(message, "Cannot read the uploaded file. Please try again.")

def add_portfolio(message):
    bot.reply_to(message, "This is add portfolio intent")

def remove_portfolio(message):
    bot.reply_to(message, "This is remove portfolio intent")

def show_portfolio(message):
    bot.reply_to(message, "This is show portfolio intent")

def portfolio_worth(message):
    bot.reply_to(message, "This is portfolio worth intent")

def portfolio_gains(message):
    bot.reply_to(message, "This is portfolio gains intent")

def plot_chart(message):
    bot.reply_to(message, "This is plot chart intent")

def bye(message):
    bot.reply_to(message, "This is good bye intent")

def default_handler(message):
    bot.reply_to(message, "I did not understand.")

mappings = {
    'plot_chart': plot_chart,
    'add_portfolio': add_portfolio,
    'remove_portfolio': remove_portfolio,
    'show_portfolio': show_portfolio,
    'portfolio_worth': portfolio_worth,
    'portfolio_gains': portfolio_gains,
    'bye': bye,
    None: default_handler
}

assistant = GenericAssistant(
    'src/intents.json', mappings, "financial_assitant_model")

assistant.train_model()
assistant.save_model()    

bot.infinity_polling()

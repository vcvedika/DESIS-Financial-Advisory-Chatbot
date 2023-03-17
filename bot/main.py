import os
import telebot
from dotenv import load_dotenv

load_dotenv()
API_TOKEN = os.getenv('API_KEY')
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['help'])
def help(message):
    str = "Here's a list of commands to help you out\n\n1. /greet - Sends you a greet message\n"
    bot.send_message(message.chat.id, str)

@bot.message_handler(commands=['greet'])
def greet(message):
    bot.reply_to(message,"Hey!")  

bot.polling()

import os
import requests
import telebot
from telebot import types
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit("Please, create .env file, otherwise the token will not be found")
else:
    load_dotenv()


bot = telebot.TeleBot(os.getenv('BOT'))

# Dictionary to store user data during the conversation
user_data = {}


# Function to display a greeting

@bot.message_handler(func=lambda message: message.text.lower() in ['hello!', 'hi!'])
def greetings(message):
    bot.send_message(message.chat.id, f"Hello, {message.from_user.first_name}!"
                                      f" Please, enter /start to begin the interaction.")


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)

    help_button = types.KeyboardButton("/help")
    markup.add(help_button)

    bot.send_message(chat_id, "Welcome to the apartment search bot!"
                              " I will help you to find suitable accommodation"
                              "according to your budget and preferences!\n"
                              "To get to know me, please, press the 'help' button!", reply_markup=markup)


@bot.message_handler(commands=['help'])
def help_user(message):
    chat_id = message.chat.id

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    low_button = types.KeyboardButton("/low")
    markup.add(low_button)

    bot.send_message(chat_id, "Let me introduce you to my main commands.\n"
                              "Command /low will get you affordable accommodation.")


# Function to handle the /low command
@bot.message_handler(commands=['low'])
def low(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"location": "", "checkin": "", "checkout": ""}

    msg = bot.send_message(chat_id, "Please enter the location:")
    bot.register_next_step_handler(msg, get_location)


def get_location(message):
    chat_id = message.chat.id
    location = message.text.strip()
    user_data[chat_id]["location"] = location

    msg = bot.send_message(chat_id, "Please enter the check-in date (YYYY-MM-DD):")
    bot.register_next_step_handler(msg, get_checkin)


def get_checkin(message):
    chat_id = message.chat.id
    checkin = message.text.strip()
    user_data[chat_id]["checkin"] = checkin

    msg = bot.send_message(chat_id, "Please enter the check-out date (YYYY-MM-DD):")
    bot.register_next_step_handler(msg, get_checkout)


def get_checkout(message):
    chat_id = message.chat.id
    checkout = message.text.strip()
    user_data[chat_id]["checkout"] = checkout

    location = user_data[chat_id]["location"]
    checkin = user_data[chat_id]["checkin"]
    checkout = user_data[chat_id]["checkout"]

    url = "https://airbnb13.p.rapidapi.com/search-location"

    querystring = {
        "location": location,
        "checkin": checkin,
        "checkout": checkout,
        "adults": "1",
        "children": "0",
        "infants": "0",
        "pets": "0",
        "currency": "USD"
    }

    headers = {
        "X-RapidAPI-Key": "cda2150777msh71d754e1400caf7p1dc2d7jsn9165cb26363b",
        "X-RapidAPI-Host": "airbnb13.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring, timeout=10)
    response = response.json()

    results = []

    for hotel_number, hotel_data in enumerate(response['results'], start=1):

        try:
            if hotel_data["price"]["total"] < 150:
                hotel_number += 1
                text = (f'Possible accommodation:\n'
                        f'\n{hotel_data["id"] = }\t\n'
                        f'{hotel_data["url"] = }\t\n'
                        f'{hotel_data["rating"] = }\t\n'
                        f'{hotel_data["price"]["total"] = }$\t')
                results.append(text)

        except:

            raise KeyError("Check out this place!")

        if hotel_number >= 10:
            break

    if results:
        bot.send_message(chat_id, "\n\n".join(results))
    else:
        bot.send_message(chat_id, "No available apartments found.\n"
                                  "Please press the 'help' button to continue.")


# Starting the bot
bot.polling()

import telebot
import os
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework.permissions import AllowAny
from telebot import types
from api.customer.models import Customer
from django.conf import settings

# Get your token from environment variables or hardcode it here
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', settings.TELEGRAM_BOT_TOKEN)
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

def menu_buttons():
    markup = types.ReplyKeyboardMarkup(row_width=1,
                                       resize_keyboard=True)
    loyalty_btn = types.KeyboardButton('💳 My loyalty points')
    website_btn = types.KeyboardButton('🌐 Our website')

    shops_btn = types.KeyboardButton('📍 Our shops')
    feedback_btn = types.KeyboardButton('✍️ Leave feedback')

    markup.add(loyalty_btn, website_btn)
    markup.row(shops_btn, feedback_btn)
    return markup

def contact_button():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True, one_time_keyboard=True)
    contact_btn = types.KeyboardButton('📞 Share my contact', request_contact=True)
    markup.add(contact_btn)

    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = ("Hello, Welcome to Telegram Bot!\n")

    bot.send_message(message.chat.id, welcome_text)
    bot.send_message(message.chat.id, "Choose an option:", reply_markup=menu_buttons())

###### message handlers ######
@bot.message_handler(func=lambda message: message.text == '💳 My loyalty points')
def loyalty_points(message):
    # Send a message with a contact-sharing button
    bot.send_message(message.chat.id, "Please share your contact to view your loyalty points:",
                     reply_markup=contact_button())

@bot.message_handler(func=lambda message: message.text == '🌐 Our website')
def our_website(message):
    markup = types.InlineKeyboardMarkup()
    website_button = types.InlineKeyboardButton(text="Visit our website", url="https://www.google.com")
    markup.add(website_button)
    bot.send_message(message.chat.id, "Click the button below to visit our website:", reply_markup=markup)

###### end message handlers ######


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.contact is not None:
        phone_number = message.contact.phone_number
        customer = Customer.objects.get(phone_number=phone_number)
        bot.send_message(message.chat.id, f"Your loyalty points are: {customer.loyalty_points}")
        bot.send_message(message.chat.id, "Choose an option:", reply_markup=menu_buttons())

def start_bot():
    bot.polling()

@api_view(['POST'])
@permission_classes([AllowAny])
def telegram_webhook(request):
    json_data = request.data

    # Handle incoming update from Telegram
    update = telebot.types.Update.de_json(json_data)
    bot.process_new_updates([update])

    return JsonResponse({"status": "received"}, status=200)

@api_view(['GET'])
@permission_classes([AllowAny])
def start_bot_view(request):
    # Optionally, you can run the bot in a separate thread or process
    from threading import Thread
    Thread(target=bot.polling).start()

    return Response({"message": "Bot has started polling!"})

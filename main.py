import telebot
import openai
import requests
import logging
from datetime import datetime
from telebot import types
import os
import io
import sqlite3
import json
from keep_alive import keep_alive

keep_alive()

# Set your Telegram bot token and OpenAI API key
BOT_NAME = 'Xtreme AI'
AI_NAME = 'AiX'
TELEGRAM_TOKEN='6405481289:AAG-1YbpQFHkI8ue2RJqMf09R1Y-9VfV_pc'
OPENAI_API_KEY = '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'
GOOGLE_MAPS_API_KEY = 'AIzaSyCg5NC8pnn-lRURnoiL3cWPoJSeLfoKn3g'  # Replace with your Google Maps API key


openai.api_key = OPENAI_API_KEY

# Create an instance of the TeleBot class
bot = telebot.TeleBot(TELEGRAM_TOKEN)


# Function to initialize the SQLite database
def initialize_database():
    connection = sqlite3.connect('bot_database.db')
    cursor = connection.cursor()

    # Create a table to store user information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            subscribed INTEGER
        )
    ''')

    connection.commit()
    connection.close()

# Function to save user information to the database
def save_user_info(user_id, username, subscribed):
    connection = sqlite3.connect('bot_database.db')
    cursor = connection.cursor()

    # Insert or update user information
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, username, subscribed)
        VALUES (?, ?, ?)
    ''', (user_id, username, subscribed))

    connection.commit()
    connection.close()

# Function to get user information from the database
def get_user_info(message):
    user_id = message.from_user.id  # Extract user ID
    connection = sqlite3.connect('bot_database.db')
    cursor = connection.cursor()

    # Retrieve user information
    cursor.execute('SELECT username, subscribed FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()

    connection.close()

    return result  # Returns (username, subscribed) or None if not found

# Initialize the database when the bot starts
initialize_database()

# File path to store the total user number
USER_FILE_PATH = "user.txt"

logo_url = 'https://i.ibb.co/B2K2Nsf/IMG-20231122-205607-799.jpg'

subscribed_users = []

# Direct URL to the online welcome GIF
WELCOME_GIF_URL = 'https://miro.medium.com/v2/resize:fit:1280/0*aBpQVhXdQ7FINy6M.gif'

# Replace with the actual URL of your welcome GIF

# Dictionary to store user message history
user_messages = {}

# 'system' variable defined globally
system = [{"role": "system", "content": f"You are a chatbot and image generator, a helpful AI assistant created by Ahmed Sumon, and your name is {AI_NAME}. Always greet with Sir. If anyone says fuck you, then you say Astagfirullah! don't say like that😞. কেউ যদি বলে তোমাকে চুদি তাহলে বলবে নাউজুবিল্লাহ এইসব কথা বলবেন না বিয়ে করে বউয়ের সাথে এসব করেন। যদি কেউ তুই করে বলে তুমিও তাহলে তুই করে বলবে।"}]

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id  # Extract user ID

    # Extract username and full name from the message object
    username = message.from_user.username
    user_full_name = message.from_user.full_name

    # Use the save_user_info function to save user information
    save_user_info(user_id, username, 1)  # 1 represents subscribed

    # Use the get_user_info function to retrieve user information
    user_info = get_user_info(message)
    if user_info:
        stored_username, subscribed = user_info
        # Use the retrieved information as needed
        user_full_name = user_full_name or stored_username  # Use stored username if full name is not available

    save_total_users()

    # Send a nice welcome message and GIF in one message
    bot.send_animation(message.chat.id, WELCOME_GIF_URL)
    bot.send_message(message.chat.id, f' ᴀssᴀʟᴀᴍᴜᴀʟᴀɪᴋᴜᴍ, {user_full_name}!🤗\nɪ ᴀᴍ {BOT_NAME}, ʏᴏᴜʀ ᴀɪ ᴄʜᴀᴛʙᴏᴛ.\nɪ ʜᴀᴠᴇ ᴀɴ ᴀɪ ᴀssɪsᴛᴀɴᴛ ɴᴀᴍᴇᴅ {AI_NAME}. sᴇɴᴅ ᴜs ᴀ ᴍᴇssᴀɢᴇ, ᴀɴᴅ ᴡᴇ ᴡɪʟʟ ᴛʀʏ ᴛᴏ ʀᴇsᴘᴏɴᴅ. ʏᴏᴜ ᴄᴀɴ ᴜsᴇ /aix ғᴏʀ ʀᴜɴ ᴛʜᴇ ᴄʜᴀᴛʙᴏᴛ ᴀɴᴅ /img ғᴏʀ ɢᴇɴᴇʀᴀᴛᴇ ɪᴍᴀɢᴇ.\nᴊᴏɪɴ ᴏᴜʀ ᴄʜᴀɴɴᴇʟ @tm_xtreme. ᴊᴏɪɴ ɢʀᴏᴜᴘ @tm_xtreme_chat. ᴀᴅᴍɪɴ ɪᴅ @ar_sumon.\nᴜsᴇ /help ғᴏʀ ᴍᴏʀᴇ ᴄᴏᴍᴍᴀɴᴅs. ᴛʜᴀɴᴋs ғᴏʀ ᴜsɪɴɢ ᴏᴜʀ sᴇʀᴠɪᴄᴇs.💥')
    user_id = message.from_user.id
    if user_id not in subscribed_users:
        subscribed_users.append(user_id)
        bot.send_message(message.chat.id, "✅✅✅")

@bot.message_handler(commands=['aix'])
def ai_command(message):
    # Extract the question from the message text after the '/aix' command
    question = message.text.split('/aix', 1)[1].strip()

    # Get the user's message history or create an empty list if it doesn't exist
    user_history = user_messages.get(message.chat.id, [])
    user_history.append({"role": "user", "content": question})

    # Save the user's message history
    user_messages[message.chat.id] = user_history

    # Check if a question is provided
    if question:
        try:
            msg = bot.send_message(message.chat.id, f"━━━━━━━━━━━━━━━━━━━━\nPlease wait, Collecting your answer 🔄⌛\n━━━━━━━━━━━━━━━━━━━━")
            # Call the ChatGPT API using OpenAI version 1.0.0
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=system + user_history,
                max_tokens=1000,  # Adjust the token limit as needed
                temperature=0.7,
            )

            # Get the AI's reply
            ai= response['choices'][0]['message']['content']
            ai_reply =(f"━━━━━━━━━━━━━━━━━━━━\n{AI_NAME}: {ai}\n━━━━━━━━━━━━━━━━━━━━")
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text= ai_reply)

            # Send the AI's reply
           #msg3=bot.reply_to(message, f'{AI_NAME}: {ai_reply}')


        except Exception as e:
            print(f"Error: {e}")
            bot.reply_to(message, "Oops! Something went wrong. Please try again later.")
    else:
        bot.reply_to(message, "Please provide a question after the /aix command.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = (
        "┌────────⭓\n"
        "├⪦ ∷ /start - To start the bot.\n"
        "├⪦ ∷ /aix Questions - Ask a question to the AI.\n"
        "├⪦ ∷ /img Description - Generate Image.\n"
        "├⪦ ∷ /ninfo - Phone number location\n"
        "├⪦ ∷ /ngd number - Nagad Half info\n"
        "├⪦ ∷ /url example.com - Shorten a URL\n"
        "├⪦ ∷ /ipinfo - Get IP info\n"
        "├⪦ ∷ /id - Telegram ID \n"
        "└────────────────⧕\n"
        "» Currently, the bot has a total of 8 commands that can be used."
    )
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['img'])
def generate_image(message):

    # Extract the description from the message text after the '/img' command
    description = message.text.split('/img', 1)[1].strip()

    if description:
        try:
            msg = bot.send_message(message.chat.id, f"━━━━━━━━━━━━━━━━━━━━\nPlease wait, Generating your image 🔄⌛\n━━━━━━━━━━━━━━━━━━━━")
            # Use OpenAI API to generate image with DALL-E
            response = openai.Image.create(
                model="dall-e-3",  # Replace with your preferred model
                prompt=description,
                n=1,
                size="1024x1024",
                quality="standard"
                # Add any other parameters as needed
            )

            if response and response['data']:
                # Download the image content from the URL
                image_url = response['data'][0]['url']
                image_content = requests.get(image_url).content

                msg2='━━━━━━━━━━━━\nProcessing complete! 💯✅\n━━━━━━━━━━━━'

                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text=msg2)
                # Send the image directly
                bot.send_photo(message.chat.id, image_content, caption=f'AiX: Generated image: {description}')
            else:
                bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="Failed to generate the image. Please try again.")

        except Exception as e:
            print(f"Error: {e}")
            bot.edit_message_text(chat_id=msg.chat.id, message_id=msg.message_id, text="Oops! Something went wrong. Please for 1min and try again or change description. Because your prompt may contain text that is not allowed by our safety system.")

    else:
        bot.reply_to(message, "Please provide a description after the /img command.")

# Dictionary to store user information
user_info_dict = {}

@bot.message_handler(commands=['id'])
def get_userinfo(message):
    # Check if a username is provided
    if len(message.text.split()) > 1:
        requested_username = message.text.split()[1].strip()

        # Store the provided username
        user_info_dict[message.from_user.id] = requested_username

    # Extract user information
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name

    # Get the stored username or fallback to the username from the user object
    username = user_info_dict.get(user_id, message.from_user.username)

    # Create a clickable link for the user link using HTML
    user_link = f"<a href='tg://user?id={user_id}'>ID Link</a>"

    # Get user profile photos
    user_profile_photos = bot.get_user_profile_photos(user_id, limit=1)

    if user_profile_photos.photos:
        # Get the file_id of the user's profile photo
        photo_file_id = user_profile_photos.photos[0][-1].file_id

        # Compose the user info message with a clickable ID Link
        user_info_message = (
            f"<b>User Info:</b>\n"
            f"<b>Telegram ID:</b> <code>{user_id}</code>\n"
            f"<b>First Name:</b> {first_name}\n"
            f"<b>Last Name:</b> {last_name}\n"
            f"<b>Username:</b> @{username}\n"
            f"<b>User link:</b> {user_link}"
        )

        # Send the user info message with the user's profile picture as the caption
        bot.send_photo(message.chat.id, photo_file_id, caption=user_info_message, parse_mode='HTML')
    else:
        # If no profile photo is available, just send the user info message
        bot.reply_to(message, user_info_message, parse_mode='HTML')

@bot.message_handler(commands=['ninfo'])
def ai_command(message):
    # Extract the question from the message text after the '/aix' command
    question = message.text.split('/ninfo', 1)[1].strip()
    bot.send_message(message.chat.id, f'This feature is not working anymore. We are trying to fix it. Stay tuned 💔')

admin_user_id = 6647338433

@bot.message_handler(func=lambda message: message.text and not message.text.startswith('/'))
def handle_non_command_messages(message):
    # Extract the text of the message
    user_full_name = message.from_user.full_name

    user_message = message.text

    # Log the user's message
    logging.info(f"{datetime.now()} - User {message.chat.id}: {user_message}")

    if message.from_user.id != admin_user_id:
        # Forward the user's message to the admin with Telegram ID 6647338433
        bot.forward_message(admin_user_id, message.chat.id, message.message_id)

        # You can also send a reply or perform additional actions here if desired
        bot.send_message(message.chat.id, f"AiX: Hello, {user_full_name}! \nPlease give me a command. A message without a command means you want to talk with the admin. If you want to talk with the admin, then explain your concern here. The admin will contact you shortly.\nCommand /help to know more about commands. Thank you.\n»𝕋𝕖𝕒𝕞 𝕏𝕋ℝ𝔼𝕄𝔼\n@tm_xtreme.")

@bot.message_handler(func=lambda message: True, content_types=['text'], reply_to_message_id=lambda m: m.from_user.id == admin_user_id)
def forward_admin_reply(message):
    # Forward the admin's reply to the original sender
    original_sender_id = message.reply_to_message.forward_from.id
    bot.forward_message(original_sender_id, message.chat.id, message.message_id)

    # You can also send a reply or perform additional actions here if desired
    bot.reply_to(message, f"Admin replied to your message, {user_full_name}.")

@bot.message_handler(commands=['notice'])
def notice_command(message):
    if message.from_user.id == 6647338433:
        bot.reply_to(message, "Enter your announcement:")
        bot.register_next_step_handler(message, lambda msg: send_announcement_to_all(msg, bot))
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

def send_announcement_to_all(message, bot_instance):
    for user_id in subscribed_users:
        try:
            bot_instance.send_message(user_id, message.text)
        except Exception as e:
            print(f"Failed to send message to {user_id}. Error: {e}")

# Command handler to get total bot users
@bot.message_handler(commands=['utotal'])
def utotal_command(message):
    if message.from_user.id == admin_user_id:
        total_users = len(subscribed_users)
        bot.reply_to(message, f"Total number of bot users: {total_users}")

        # Send the content of the user.txt file to the admin
        send_user_txt_to_admin(message)
    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# Function to send the content of the user.txt file to the admin
def send_user_txt_to_admin(message):
    try:
        with open(USER_FILE_PATH, 'r') as file:
            user_txt_content = file.read().strip()

        # Save the content of user.txt as a temporary file
            temp_file_name = f"user_tmp_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
            with open(temp_file_name, "w") as tmp_file:
                   tmp_file.write(user_txt_content)


# Send the temporary file as a document to the admin
            with open(temp_file_name, "rb") as document:
                    bot.send_document(message.chat.id, document, caption="Here is the content of user.txt")



          # Remove the temporary file
            os.remove(temp_file_name)

    except Exception as e:
        bot.reply_to(message, f"Failed to send user.txt content. Error: {e}")




# Function to save the total number of users
def save_total_users():
    try:
        # Get the current total from the user.txt file
        total_users = get_total_users()

        # Increment the total by 1 (assuming the start command represents a new subscriber)
        total_users += 1

        # Save the updated total to the user.txt file
        with open(USER_FILE_PATH, 'w') as file:
            file.write(str(total_users))
    except Exception as e:
        print(f"Error saving total users: {e}")


# Function to get the total number of users
def get_total_users():
    try:
        # Read the current total from the user.txt file
        with open(USER_FILE_PATH, 'r') as file:
            total_users = int(file.read().strip())
        return total_users

    except FileNotFoundError:
        # If the file doesn't exist, set total_users to 0
        return 0
    except ValueError:
        # If there's an issue converting to int, set total_users to 0
        return 0




# Function to create an inline keyboard with a Google Maps button
def create_google_maps_button(lat, lon):
    keyboard = types.InlineKeyboardMarkup()
    google_maps_button = types.InlineKeyboardButton(
        text="Open in Google Maps",
        url=f"https://www.google.com/maps?q={lat},{lon}&key={GOOGLE_MAPS_API_KEY}"
    )
    keyboard.add(google_maps_button)
    return keyboard

@bot.message_handler(commands=['ipinfo'])
def ip_info(message):
    question = message.text.split('/ipinfo', 1)[1].strip()
    user_id = message.chat.id
    bot.send_message(user_id, "Please wait...")

    if question:
        try:
            ip_address = message.text.split('/ipinfo', 1)[1].strip()
            response = requests.get(f"https://api.weatherapi.com/v1/ip.json?key=7ca30df5844b4b6087230641212908&q={ip_address}").json()

            print("Full Response:", response)  # Add this line to print the entire response

            # Check if the 'ip' key is present in the response
            if 'ip' in response:
                result = (
                    f"⚠️⚠️ 🇦 🇮 🇽     🇮 🇵⚠️⚠️\n"
                    f"=============================\n"
                    f"*IP                   :* {response['ip']}\n"
                    f"--------------------------------------------------------\n"
                    f"*TYPE             :* {response['type']}\n"
                    f"--------------------------------------------------------\n"
                    f"*TIME-ZONE  :* {response['tz_id']}\n"
                    f"--------------------------------------------------------\n"
                    f"*LOCAL TIME:* {response['localtime']}\n"
                    f"--------------------------------------------------------\n"
                    f"*COUNTRY     :* {response['country_name']}\n"
                    f"--------------------------------------------------------\n"
                    f"*CITY               :* {response['city']}\n"
                    f"--------------------------------------------------------\n"
                    f"*LON & LAT    :* {response['lon']},{response['lat']}\n"
                    f"--------------------------------------------------------\n"
                )

                # Create a Google Maps link with a pin at the specified latitude and longitude
                google_maps_link = f"https://www.google.com/maps?q={response['lat']},{response['lon']}&key={GOOGLE_MAPS_API_KEY}"


            else:
                # Handle the case when the 'ip' key is not present
                result = "⚠️⚠️ 🇦 🇮 🇽     🇮 🇵⚠️⚠️\n\nERROR: No matching location found. It seems like you are trying with a private IP. Please try with a public IP."

            # Download the logo image and create an instance of InputFile
            logo_image = requests.get(logo_url).content

            bot.send_photo(user_id, logo_image, caption=result, parse_mode="Markdown", reply_markup=create_google_maps_button(response['lat'], response['lon']))

        except IndexError:
            bot.send_message(user_id, "Please provide an IP address after the /ipinfo command.")
        except requests.exceptions.RequestException as e:
            bot.send_message(user_id, f"Error retrieving IP information: {e}")
    else:
        bot.send_message(user_id, "Please provide an IP address after the /ipinfo command.")

# Command handler to print all users
@bot.message_handler(commands=['udata'])
def print_users_command(message):
    if message.from_user.id == admin_user_id:
        # Call the function to print all users
        users_data = get_all_users_data()

        # Format the user data for display
        formatted_users = "\n".join([f"User ID: {user_id}, Username: {username}, Subscribed: {subscribed}" for user_id, username, subscribed in users_data])

        # Save the formatted user data to a file
        with open('subscribed_users.txt', 'w') as file:
            file.write(formatted_users)

        # Send the formatted user data as a document
        with open('subscribed_users.txt', 'rb') as file:
            bot.send_document(message.chat.id, file, caption=f"Here is your subscriber list.")

    else:
        bot.reply_to(message, "You are not authorized to use this command.")

# Function to get all users' data from the database
def get_all_users_data():
    connection = sqlite3.connect('bot_database.db')
    cursor = connection.cursor()

    # Retrieve all users' data
    cursor.execute('SELECT user_id, username, subscribed FROM users')
    users_data = cursor.fetchall()

    connection.close()

    return users_data  # Returns a list of tuples (user_id, username, subscribed)

#URL SHORTENER

# URL shortener API endpoint
URL_SHORTENER_API = 'https://is.gd/create.php?format=json&callback=myfunction&url={}&shorturl={}&logstats=1'

# Direct variables to store user state
waiting_for_url = {}
waiting_for_alias = {}

# Handle /url command for getting URL
@bot.message_handler(commands=['url'])
def ushort_command_url(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    try:
        # Extract the URL from the message text after the '/url' command
        waiting_for_url[user_id] = message.text.split()[1]

        # Ask for an alias
        bot.send_message(chat_id, "Great! 😸👍\nNow, please provide an alias for your URL after the /alias command to create a custom URL ☺️.")
        waiting_for_alias[user_id] = True
    except IndexError:
        bot.reply_to(message, 'Please provide a URL after /url.\nExample: /url https://example.com')

# Handle /alias command for getting alias
@bot.message_handler(commands=['alias'])
def ushort_command_alias(message):
    chat_id = message.chat.id
    user_id = message.from_user.id

    # Check if waiting for alias
    if waiting_for_alias.get(user_id, False):
        # Check if there are elements in the list after splitting
        if len(message.text.split()) > 1:
            alias = message.text.split()[1]
            # Get URL from waiting_for_url
            url = waiting_for_url.get(user_id, '')  # Use get() to avoid KeyError

            # Shorten URL using is.gd API
            response = requests.get(URL_SHORTENER_API.format(url, alias))

            try:
                # Extract JSON content from the JSONP response
                jsonp_content = response.content.decode('utf-8')
                json_content_start = jsonp_content.find('{')
                json_content_end = jsonp_content.rfind('}') + 1
                json_content = jsonp_content[json_content_start:json_content_end]

                # Parse the JSON content
                data = json.loads(json_content)
                short_url = data.get('shorturl', '')

                if short_url:
                    bot.send_message(chat_id, f"DONE! 🤟\nYour Shortened URL is here 👉: {short_url}")
                else:
                    bot.send_message(chat_id, "Failed to shorten URL. Please try again.")
            except (requests.exceptions.JSONDecodeError, ValueError) as e:
                print(f"Failed to parse API response. Response content: {response.content}")
                print(f"Error details: {e}")
                bot.send_message(chat_id, "Failed to shorten URL. Please try again.")
            finally:
                # Reset user state
                waiting_for_url.pop(user_id, None)  # Use pop() to remove the key if it exists
                waiting_for_alias.pop(user_id, None)
        else:
            bot.send_message(chat_id, "Please provide an alias after the /alias command.")
    else:
        bot.send_message(chat_id, "Invalid command. Please use /url to shorten a URL first.")


#NAGAD HALF INFO

API_URL = 'https://api.mr999plus.site/nagad-info/{number}'

@bot.message_handler(commands=['ngd'])
def handle_get_info(message):
    try:
        phone_number = message.text.split()[1]
        api_url = API_URL.format(number=phone_number)

        response = requests.get(api_url)
        data = response.json()

        if response.status_code == 200 and data['data']['success']:
            user_info = data['data']['info']
            msg = f"»  𝗡𝗨𝗠𝗕𝗘𝗥  :   {phone_number}\n»  𝗡𝗔𝗠𝗘  :   {user_info['name']}\n»  𝗨𝗦𝗘𝗥𝗜𝗗  :   {user_info['userId']}\n»  𝗦𝗧𝗔𝗧𝗨𝗦  :   {user_info['status']}\n»  𝗨𝗦𝗘𝗥𝗧𝗬𝗣𝗘  :   {user_info['userType']}\n»  𝗥𝗕𝗕𝗔𝗦𝗘  : {user_info['rbBase']}\n»  𝗩𝗘𝗥𝗜𝗙𝗜𝗖𝗔𝗧𝗜𝗢𝗡𝗦𝗧𝗔𝗧𝗨𝗦  :  {user_info['verificationStatus']}\n»  𝕋𝕖𝕒𝕞 𝕏𝕋ℝ𝔼𝕄𝔼\n"
        else:
            msg = f"Error: {data['msg']}"

        bot.reply_to(message, msg)
    except IndexError:
        bot.reply_to(message, 'Please provide a phone number. Example: /ngd 01712345678')




# Polling loop to keep the bot running
bot.polling()
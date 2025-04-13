
'''
#build by delone  (nouredine_kn)  https://github.com/nouredinekn
#telegram : nouredine_kn
#instagram: nouredine_kn
#my website:  developpeurcasablanca.com
'''
import undetected_chromedriver as uc
import json
import requests
import telebot
import time
import threading
import logging


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except FileNotFoundError:
    logger.error("config.json not found!")
    exit(1)
except json.JSONDecodeError:
    logger.error("Invalid config.json format!")
    exit(1)

EMAIL = str(config['EMAIL']).lower()
ACCESS_TOKEN = config['ACCESS_TOKEN']
TELEGRAM_ID = config['TELEGRAM_ID']
TELEGRAM_BOT_TOKEN = config['TELEGRAM_BOT_TOKEN']
callmebot=config['callmebot']
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


STATUS = {'status': ''}


TELEGRAM_ID_GROUP=config['TELEGRAM_ID_GROUP']
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)


def send_gp(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_ID_GROUP,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Telegram notification sent successfully.")
        else:
            print(f"Failed to send Telegram notification: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")

def send_telegram_notification(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_ID,
        'text': message,
        'parse_mode': 'Markdown'
    }
    try:    
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            print("Telegram notification sent successfully.")
            send_gp(message)
        else:
            print(f"Failed to send Telegram notification: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram notification: {e}")
    


def run_bot():
    logger.info("Starting Telegram bot polling...")
    @bot.message_handler(commands=['status'])
    def send_welcome(message):
        logger.info("Received /status command from chat_id: %s", message.chat.id)
        bot.reply_to(message, STATUS["status"] if STATUS["status"] else "No status available yet.")
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        logger.error("Bot polling error: %s", e)
        time.sleep(10)
        run_bot() 


options = uc.ChromeOptions()

driver = uc.Chrome(options=options)


logger.info("Loading initial page...")
driver.get("https://admission.1337.ma/candidature/check-in")
time.sleep(20) 

cookies = [
    {
        "name": "accessToken",
        "value": ACCESS_TOKEN,
        "domain": "admission.1337.ma",
        "path": "/",
        "secure": False,
        "httpOnly": True,
        "sameSite": "Lax"
    }
]

for cookie in cookies:
    driver.add_cookie(cookie)
driver.refresh()

def main_loop():
    send_telegram_notification("RUNED!")
    i = 0
    while True:
        try:
            logger.info("Refreshing page...")
            driver.refresh()
            if i == 0:
                time.sleep(10)  
            html = driver.page_source
            
            
            if EMAIL not in html:
                message = "PLEASE CHANGE ACCESS_TOKEN! AND RUN ME AGAIN"
                STATUS["status"] = message
                logger.warning(message)
                while True:
                    html = driver.page_source
                    logger.debug("HTML content: %s", html[:500])  
                    if EMAIL not in html:
                        send_telegram_notification(message)
                        STATUS["status"] = message
                    else:
                        logger.info("Email found, access token valid again.")
                        break
                    
            
            
            if 'Any available Check-ins will appear here' in html:
                logger.debug("HTML content: %s", html[:500]) 
                STATUS['status'] = 'Any available Check-ins will appear here'
                logger.info("No check-ins available.")
            else:
                
                if EMAIL not in html:
                    message = "PLEASE CHANGE ACCESS_TOKEN! AND RUN ME AGAIN"
                    STATUS["status"] = message
                    logger.warning(message)
                    while True:
                        html = driver.page_source
                        logger.debug("HTML content: %s", html[:500])
                        if EMAIL not in html:
                            send_telegram_notification(message)
                            STATUS["status"] = message
                        else:
                            logger.info("Email found, access token valid again.")
                            break
                        
                else:
                    message = "GO GO TAKE ['CHECK IN']!"
                    STATUS['status'] = message
                    requests.get(callmebot)
                    logger.info(message)
                    while True:
                        driver.refresh()
                        send_telegram_notification(message)
                        html = driver.page_source
                        if 'Any available Check-ins will appear here' in html:
                            logger.debug("HTML content: %s", html[:500])
                            STATUS['status'] = 'Any available Check-ins will appear here'
                            logger.info("Back to no check-ins available.")
                            break
                        
                    i = 1
            
            
        except Exception as e:
            logger.error("Error during page check: %s", e)
            send_telegram_notification(f"Error during page check: {e}")
            


logger.info("Starting bot thread...")
bot_thread = threading.Thread(target=run_bot)
bot_thread.daemon = True 
bot_thread.start()
logger.info("Starting main loop...")
main_loop()
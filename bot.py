#!/usr/bin/python3
import re
import telebot
import schedule
import time
import logging
import oauth2 as oauth
import logging
import firefly
import users
import traceback
import json

#########################################################################################
# Basic config
# 

# Load configs
content_file = open("config.json", 'r')
content = content_file.read()
content_file.close()
CONFIGS = json.loads(content) #TODO: make error message if configs file doesn't exist or is corrupted

MESSAGES = {
    "welcome": "Welcome!",
    "asking_to_verify_money_in_pocket": "Let's check money in your pocket. How much do you have?",
    "you_are_my_user_already": "You are my user already",
    "you_are_my_master": "You are my first user. I choose you as my master.",
    #
    "choose_your_pocket_prefix": "choose pocket ", 
    "choose_your_pocket_account": "choose your pocket account",
    "choose_your_pocket_account_retry": "choose your pocket account. I didn't get what you've said.",
    #
    "excuses_for_bothering": "Okey, I do not bother you",
    "where_did_you_get_money": "Whoa, that's more than you got before. Where did you get the money?",
    "no_amount_sent": "You didn't send amount of money you took. I can't handle such messages for the moment.",
    "thankyou": "Thank you",
    "choose_budget": "Choose budget:",
    #
    "no_connection": "No connection to your firefly server, sorry. Check your server and api key and try again.",
    "request_for_server": "Please, tell me your firefly server url (for example `http://152.12.51.224` or `http://myfirefly.com`)",
    "request_for_server_failed_validation": "Doesn't look like server url",
    "request_for_oauth_key": "Please, tell me firefly access token (for example `eyJ0eXAiOiJKV1QiLCJZboci9iJSUzI1NiIsImp0aSI6ImY1YWY0Yzc2ZTBkNDliNjA2ZTAwZjcyYTc0YjQ4YzM4MTc1Y2JjNWI4MjU1MWU3NDMwNTM5MWJkNGRiYmU0NDk2ODE1MGRmYThhYjg0NzM2In0`)",
    #
    "rules_introduction": "You can send me spent money at any time (for example `123 tea`). Once a day I will ask you, how much money do you have in your pocket."
}
firefly = firefly.Firefly()

#########################################################################################
# Basic classes
# 

class ScheduledTeleBot(telebot.TeleBot):
    def __non_threaded_polling(self, schedule, none_stop=False, interval=0, timeout=3):
        logger.info('Started polling.')
        self._TeleBot__stop_polling.clear()
        error_interval = .25

        while not self._TeleBot__stop_polling.wait(interval):
            try:
                schedule.run_pending()
                self._TeleBot__retrieve_updates(timeout)
                error_interval = .25
            except apihelper.ApiException as e:
                logger.error(e)
                if not none_stop:
                    self._TeleBot__stop_polling.set()
                    logger.info("Exception occurred. Stopping.")
                else:
                    logger.info("Waiting for {0} seconds until retry".format(error_interval))
                    time.sleep(error_interval)
                    error_interval *= 2
            except KeyboardInterrupt:
                logger.info("KeyboardInterrupt received.")
                self._TeleBot__stop_polling.set()
                break

        logger.info('Stopped polling.')

    def polling(self, schedule, none_stop=False, interval=0, timeout=20):
     	self.__non_threaded_polling(schedule, none_stop, interval, timeout)

#########################################################################################
# Main variables
# 

bot = ScheduledTeleBot(CONFIGS["telegram_token"])
logger = logging.getLogger('TeleBot')
users=users.User()

#########################################################################################
# Chatting callbacks
# 

# cronjob, that sends message to users
def cronjob():
    logger.info('cronjob function')
    for chat_id in users.getUsersIds():
        markup = telebot.types.ForceReply(selective=False)
        bot.send_message(chat_id, MESSAGES["asking_to_verify_money_in_pocket"], reply_markup=markup)

########################################
# Init communication

# replies for `/start`
@bot.message_handler(commands=['start'])
def send_welcome(message):
    # TODO: security
    try:
        bot.reply_to(message, MESSAGES["welcome"])
        if users.exists(message.from_user.username):
            bot.send_message(message.chat.id, MESSAGES["you_are_my_user_already"])
        else:
            users.add(message.from_user.username, message.chat.id)
            # send message for function _check_if_reply_to_server_request(msg)
            markup = telebot.types.ForceReply(selective=False)
            bot.send_message(message.chat.id, MESSAGES["request_for_server"], reply_markup=markup)
    except Exception as err:
        print(err)
        traceback.print_exc()

# checking, if message is reply for firefly server request
def _check_if_reply_to_server_request(msg):
    if not hasattr(msg,'reply_to_message'):
        return False
    if not hasattr(msg.reply_to_message,'text'):
        return False
    return msg.reply_to_message.text == MESSAGES["request_for_server"]

@bot.message_handler(func=_check_if_reply_to_server_request)
def got_reply_on_server_request(message):
    if (True): # TODO: validate message
        users.setServer(message.from_user.username, message.text)
        # Please, tell me firefly access token (for example `eyJ0eXAiOiJKV1QiLCJZboci9iJSUzI1NiIsImp0aSI6ImY1YWY0Yzc2ZTBkNDliNjA2ZTAwZjcyYTc0YjQ4YzM4MTc1Y2JjNWI4MjU1MWU3NDMwNTM5MWJkNGRiYmU0NDk2ODE1MGRmYThhYjg0NzM2In0`)
        markup = telebot.types.ForceReply(selective=False)
        bot.send_message(message.chat.id, MESSAGES["request_for_oauth_key"], reply_markup=markup)
    else:
        bot.send_message(message.chat.id, MESSAGES["request_for_server_failed_validation"])
        markup = telebot.types.ForceReply(selective=False)
        bot.send_message(message.chat.id, MESSAGES["request_for_server"], reply_markup=markup)

# checking, if message is reply to firefly oauth token request
def _check_if_reply_to_access_token_request(msg):
    if not hasattr(msg,'reply_to_message'):
        return False
    if not hasattr(msg.reply_to_message,'text'):
        return False
    return msg.reply_to_message.text == MESSAGES["request_for_oauth_key"]

@bot.message_handler(func=_check_if_reply_to_access_token_request)
def got_reply_on_access_token(message):
    try:
        users.setAccessToken(message.from_user.username, message.text)
        if firefly.testConnection(message.from_user.username, users):
            if not users.hasMaster():
                bot.send_message(message.chat.id, MESSAGES["you_are_my_master"])
            # ask user, which account should be locked to this user. Using telegram's buttons: "choose pocket <pocketname>"
            balances = firefly.getBalances(message.from_user.username, users)
            markup = telebot.types.ReplyKeyboardMarkup()
            for balace in balances:
                markup.row(telebot.types.KeyboardButton(MESSAGES["choose_your_pocket_prefix"]+str(balace)))
            bot.reply_to(message, MESSAGES["choose_your_pocket_account"], reply_markup=markup)
        else:
            bot.send_message(message.chat.id, MESSAGES["no_connection"])
            markup = telebot.types.ForceReply(selective=False)
            bot.send_message(message.chat.id, MESSAGES["request_for_server"], reply_markup=markup)
    except Exception as err:
        print(err)
        traceback.print_exc()

@bot.message_handler(regexp=MESSAGES["choose_your_pocket_prefix"])
def choose_pocket(message):
    try:
        message_text = message.text
        # get balances and incomes from firefly
        pockets_data = firefly.getBalancesExtended(message.from_user.username, users)

        # get pockets
        message_pocket = ''
        account_id = 0
        account_currency = ""
        for pocket in pockets_data:
            if pocket["attributes"]["name"] in message_text:
                message_pocket = pocket["attributes"]["name"]
                account_id = pocket["id"]
                account_currency = pocket["attributes"]["currency_code"]
                message_text = message_text.replace(pocket["attributes"]["name"],'')
                break
        # message is left in message_text

        if message_pocket:
            users.setPocket(message.from_user.username, value=message_pocket, account_id=account_id, account_currency=account_currency)
            users.setAuthorized(message.from_user.username)
            # Send welcome message            
            markup = telebot.types.ReplyKeyboardHide(selective=False)
            bot.send_message(message.chat.id, MESSAGES["rules_introduction"], reply_markup=markup)
        else:
            for pocket in pockets:
                markup.row(telebot.types.KeyboardButton('choose pocket '+str(pocket)))
            markup = telebot.types.ReplyKeyboardMarkup()
            bot.reply_to(message, MESSAGES["choose_your_pocket_account_retry"], reply_markup=markup)
    except Exception as err:
        print(err)
        traceback.print_exc()


########################################
# Crons communication

# check for next function
def _check_if_message_made_by_cron(msg):
    if not hasattr(msg,'reply_to_message'):
        return False
    if not hasattr(msg.reply_to_message,'text'):
        return False
    return msg.reply_to_message.text == MESSAGES["asking_to_verify_money_in_pocket"]


# if this is reply to message, made by cron - we expect money in pocket (see _check_if_message_made_by_cron())
@bot.message_handler(func=_check_if_message_made_by_cron)
def got_reply_on_cron(message):
    message_text = message.text
    # get money in pocket from firefly
    current_balance = firefly.getCurrentBalance(message.from_user.username, users)

    # get number
    message_number = re.findall('\d+', message_text)[0]
    message_text = message_text.replace(message_number,'')

    if not message_number:
        bot.reply_to(message, MESSAGES["excuses_for_bothering"])
        bot.send_message(users.getMasterId(), "User @"+message.from_user.username+" ignores me!")
        pass
    else:
        try:
            message_integer = int(message_number)
            balance_diff = message_integer-current_balance
            if message_integer > current_balance:
                # get balances and incomes from firefly
                balances = firefly.getBalances(message.from_user.username, users)
                balances.extend(firefly.getIncomes(message.from_user.username, users))

                markup = telebot.types.ReplyKeyboardMarkup()
                for balance in balances:
                    markup.row(telebot.types.KeyboardButton('took '+str(balance_diff)+' from '+str(balance)))
                bot.reply_to(message, MESSAGES["where_did_you_get_money"], reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "You have spent "+str(balance_diff)+".")
                _talk_about_spent_money(message, message_number=str(balance_diff))
        except Exception as err:
            print(err)


# Adding money to user's balance from another balance
# Works with messages:
# - took 1231 from balance1
# - took 1231
@bot.message_handler(regexp="took")
def took_money(message):
    message_text = message.text
    # get balances and incomes from firefly
    balances = firefly.getBalances(message.from_user.username, users)

    # get number
    message_number = re.findall('\d+', message_text)[0]
    message_text = message_text.replace(message_number,'')

    # get balance
    message_balance = ''
    for balance in balances:
        if balance in message_text:
            message_balance = balance
            message_text = message_text.replace(balance,'')
            break
    # message is left in message_text

    if not message_balance:
    #    TODO: ask user for balance. With buttons.
        pass
    elif not message_number:
        markup = telebot.types.ReplyKeyboardHide()
        bot.reply_to(message, MESSAGES["no_amount_sent"], reply_markup=markup)
    else:
        firefly.take(message.from_user.username, users, int(message_number), message_balance, message_text)
        markup = telebot.types.ReplyKeyboardHide()
        bot.reply_to(message, MESSAGES["thankyou"], reply_markup=markup)
        pass

########################################
# Make transaction communication

# talking about spent money. Aknowledge needed info.
def _talk_about_spent_money(message_to_reply, message_number="",message_budget="",message_text=""):
    # get budgets from firefly
    budgets=firefly.getBudgets(message_to_reply.from_user.username, users)

    if not message_budget:
        markup = telebot.types.ReplyKeyboardMarkup()
        for budget in budgets:
            markup.row(telebot.types.KeyboardButton(message_number+' '+budget+' '+message_text))
        bot.reply_to(message_to_reply, MESSAGES["choose_budget"], reply_markup=markup)
    # if everything got - just add it to firefly
    else:
        try:
            markup = telebot.types.ReplyKeyboardHide()
            firefly.spend(message_to_reply.from_user.username, users, int(message_number), message_budget, message_text)
            bot.reply_to(message_to_reply, MESSAGES["thankyou"], reply_markup=markup)
        except Exception as err:
            print(err)

# If message have numbers and not caught by previous handlers - we suppose it's about spent money
@bot.message_handler(regexp="[0-9]+")
def recieved_number(message):
    message_text = message.text
    # get budgets from firefly
    budgets=firefly.getBudgets(message.from_user.username, users)

    # get number
    message_number = re.findall('\d+', message_text)[0]
    message_text = message_text.replace(message_number,'')
    # get budget
    message_budget = ''
    for budget in budgets:
        if budget in message_text:
            message_budget = budget
            message_text = message_text.replace(budget,'')
            break
    # message is left in message_text

    # if expense not set - ask for it
    _talk_about_spent_money(message, message_number=message_number, message_budget=message_budget, message_text=message_text)

#########################################################################################
# Main executing code
# 
                    # TODO: scheduling should be in config or in personal user's settings
schedule.every().day.at("20:00").do(cronjob)
#schedule.every().minute.do(cronjob)

bot.polling(schedule)
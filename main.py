from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json

#pass in the appropriate bot token
bot_token: Final = ''
bot_username: Final = 'customerGluHealthCheckerBot'

url_health_stats = 'https://gqu4gue08i.execute-api.ap-south-1.amazonaws.com/dev/healthstats'
url_running_processes = "https://gqu4gue08i.execute-api.ap-south-1.amazonaws.com/dev/runningprocesses"
url_vm_health_check = 'https://gqu4gue08i.execute-api.ap-south-1.amazonaws.com/dev/vmhealthcheck'

def get_response(url):
    try:
        response = requests.get(url)

        if response.status_code == 200:
            return response.text
        else:
            print(f'Failed to retrieve data. Status code: {response.status_code}')

    except requests.exceptions.RequestException as e:
        print(f'An error occurred: {e}')

#Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hey! Thanks for coming here. I can help you with the health of CustomerGlu servers.'
                                    ' Please use /help to check for commands')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_message = 'Press 1 to get Server statistics.\nPress 2 to check if VM is responding.\nPress 3 to get all the running processes.'
    await update.message.reply_text(help_message)

def handle_response(text: str) -> str:
    if '1' == text:
        response = get_response(url_health_stats)
        data = json.loads(response)
        cpu_percentage = data['cpu_times_utilization_percentage']
        current_frequency = data['current_frequency']
        total_physical_memory = data['total_physical_memory']
        total_available_physical_memory = data['total_available_physical_memory']
        percentage_usage_physical_memory = data['percent_usage_physical_memory']
        response_string = ("CPU percentages: " + str(cpu_percentage) + "\nCurrent frequency: " + str(current_frequency)
                           + " Mhz" + "\nTotal Physical Memory: " + str(total_physical_memory) + " bytes"
                           "\nTotal Available Physical Memory: " + str(total_available_physical_memory) + " bytes" +
                           "\n" + "Physical Memory Usage: " + str(percentage_usage_physical_memory) + "%")
        return response_string

    elif '2' == text:
        response = get_response(url_vm_health_check)
        data = json.loads(response)

        return data['Message']

    elif '3' == text:
        response = get_response(url_running_processes)
        processes_list = json.loads(response)
        i = 1
        process_string = ''

        for process in processes_list:
            process_string += ("Process " + str(i) + ":\nPID = " +str(process['pid']) + ", Name = " +
                               (str(process['name']))) + ", Status = " + str(process['status']) + "\n\n"
            i += 1

        return process_string

    return 'I\'m sorry but I don\'t understand that command. Please use /help to check for commands'

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type : str = update.message.chat.type
    text: str = update.message.text

    if message_type == "group":
        if bot_username in text:
            new_text: str = text.replace(bot_username,'').strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')


if __name__ == "__main__":
    print('Starting bot...')
    app = Application.builder().token(bot_token).build()

    #Commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))

    #Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    app.add_error_handler(error)

    app.run_polling(poll_interval=3)
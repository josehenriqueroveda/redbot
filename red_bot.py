import telebot
import pandas as pd
from datetime import date
import os
import shutil
from redminelib import Redmine
import local_config

redmine = Redmine(local_config.REDMINE_URL, key=local_config.REDMINE_KEY)
API_KEY = local_config.TELEGRAM_KEY

bot = telebot.TeleBot(API_KEY)


# Delete the old files
def delete_files():
    old_files = os.listdir(
        'DESTINATION_DIRECTORY')
    for item in old_files:
        fp = os.path.join(
            'DESTINATION_DIRECTORY', item)
        # check if it is a directory or file
        if os.path.isdir(fp):
            shutil.rmtree(fp)
        elif os.path.isfile(fp):
            os.remove(fp)
        else:
            print("It is a special file (socket, FIFO, device file)")


@bot.message_handler(commands=['projects'])
def get_projects(msg):
    projects = redmine.project.all()
    txt = """"""
    for project in projects:
        txt = txt + f'\n - {project}'
    bot.send_message(
        msg.chat.id, f'🚀 Listing projects: {txt}')



@bot.message_handler(commands=['issues'])
def get_issues(msg):
    issues = redmine.issue.filter(status_id='open', assigned_to_id="YOUR_USER_ID (INT)"})
    txt = """"""
    for issue in issues:
        txt = txt + f'\n - {issue}'
    bot.send_message(
        msg.chat.id, f'📑 Listing all your open issues: {txt}')


# Tracker ID: 1 - Bug | 2 - Feature | 3 - Support
@bot.message_handler(commands=['bugs'])
def get_bugs(msg):
    bugs = redmine.issue.filter(
        status_id='open', assigned_to_id="YOUR_USER_ID (INT)", tracker_id=1)
    txt = """"""
    if bugs:
        for bug in bugs:
            txt = txt + f'\n - {bug}'
        bot.send_message(
            msg.chat.id, f'🐛 Listing all open bugs: {txt}')
    else:
        bot.send_message(msg.chat.id, '🙏 There are no bugs')


# Tracker ID: 1 - Bug | 2 - Feature | 3 - Support
@bot.message_handler(commands=['features'])
def get_features(msg):
    features = redmine.issue.filter(
        status_id='open', assigned_to_id="YOUR_USER_ID (INT)", tracker_id=2)
    txt = """"""
    if features:
        for feature in features:
            txt = txt + f'\n - {feature}'
        bot.send_message(
            msg.chat.id, f'🆕 Listing all open features: {txt}')
    else:
        bot.send_message(msg.chat.id, '💤 There are no open features')


# Tracker ID: 1 - Bug | 2 - Feature | 3 - Support
@bot.message_handler(commands=['supports'])
def get_supports(msg):
    supports = redmine.issue.filter(
        status_id='open', assigned_to_id="YOUR_USER_ID (INT)", tracker_id=3)
    txt = """"""
    if supports:
        for support in supports:
            txt = txt + f'\n - {support}'
        bot.send_message(
            msg.chat.id, f'🧯 Listing all open supports: {txt}')
    else:
        bot.send_message(msg.chat.id, '✌️ There are no support requests')


@bot.message_handler(commands=['report'])
def get_report(msg):
    issues = redmine.issue.filter(status_id='open')
    issues.export(
        'csv', savepath='DESTINATION_DIRECTORY', columns='all')
    bot.send_message(msg.chat.id, '⌛ Generating your Weeky Report...')
    status_code = build_report()
    if status_code == 200:
        bot.send_message(
            msg.chat.id, '✅ Your Weekly Report was generated on: \n DESTINATION_DIRECTORY')
    else:
        bot.send_message(msg.chat.id, '❌ Error: No files were generated')
    delete_files()


def build_report():
    files = os.listdir(
        'DESTINATION_DIRECTORY')
    if files:
        today = date.today().strftime("%d-%m-%Y")
        df = pd.read_csv('DESTINATION_DIRECTORY/issues.csv',
                         usecols=['Project', 'Subject','Status', 'Assignee', 'Due date'])
        df = df[df['Assignee'] == 'YOUR_NAME']
        df = df[df['Status'] != 'New']
        df['Project'] = df['Project'] + ': ' + df['Subject']
        del df['Subject']
        df.columns = ['Task', 'Status', 'Responsible', 'Due Date']
        df = df.sort_values(by=['Task'])
        df.to_excel(
            f'DESTINATION_DIRECTORY/Weekly_Report_{today}.xlsx', encoding='utf-8', index=False)
        return 200
    else:
        return 404


def check(msg):
    return True


@bot.message_handler(func=check)
def answer(msg):
    txt = """
    🤖 *Choose one option to continue...*\n
    /projects View all projects\n
    /issues View all open issues\n
    /bugs View open bugs\n
    /features View open features\n
    /supports View open supports\n
    /report Generate Weekly Report 
    """
    bot.send_message(msg.chat.id, txt, parse_mode='Markdown')


bot.infinity_polling()

# -*- coding: utf-8 -*-
from tgclient import *
import json
import redis
import re
import urllib.request as ur
from requests import get
import os
import json
import random
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error


"""
	@IT_MKH or @CRUEL
	@CRUEL_TEAM
"""


r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
token = 'TOKEN'
bot = TelegramBot(token, True)
sudo = [284244758, 0]


def download(url, file_name):
    with open(file_name, "wb") as file:
        response = get(url)
        file.write(response.content)


def img(music, image):
    audio = MP3(music, ID3=ID3)

    try:
        audio.add_tags()
    except error:
        pass

    audio.tags.add(
        APIC(
            encoding=3,
            mime='image/png',
            type=3,
            desc=u'Cover',
            data=open(image, 'rb').read()
        )
    )
    audio.save()


def join(user_id):
    mem = bot.getChatMember('@iranmusic_ir', user_id['from']['id'])
    if mem:
        if mem['status'] in ['creator', 'administrator', 'member']:
            return True
        elif user_id['from']['id'] in sudo:
            return True


@bot.command(r'[/#!]fbc')
def fbc(message):
    if message['from']['id'] in sudo:
        if 'reply_to_message' in message:
            gp = r.smembers("music_tag_bot")
            messageid = message['reply_to_message']['message_id']
            fch = message['reply_to_message']['chat']['id']
            t = 0
			k = 0
            for i in gp:
                try:
                    bot.forwardMessage(i, fch, messageid)
                    t = t + 1
                except:
                    k = k + 1
                    pass
            bot.sendMessage(message['chat']['id'], 'تعداد ارسال موفق : {}\nتعداد افرادی که ربات را بلاک کرده اند : {}'.format(t,k))


@bot.command(r'[/#!]stats')
def stats(message):
    if message['from']['id'] in sudo:
        users = r.scard("mahla_tag_bot")
        text = '''👤تعداد کاربران پیوی : {}'''.format(users)
        bot.sendMessage(message['chat']['id'], text)


@bot.command(r'^/start$')
def start(message):
    r.sadd("mahla_tag_bot", message['from']['id'])
    if join(message):
        text = '''سلام دوست عزیز من ☺️🌹

به ربات ویرایش تگ موزیک و همچنین ساخت دمو خوش اومدی 🙃
برای شروع کار کافیه فقط فایل موزیکتو برای من بفرستی 🤓
برو بریم🏃'''
        bot.sendMessage(message['chat']['id'], text)
    else:
        text = '''سلام 😝
چرا تو چنلمون عضو نیستی؟🙁😔
من کار نمیکنم تا اینکه عضو بشی😜
وارد کانال زیر بشو و بعدش دکمه زیر این متنو بزن 🤗
@IRANMUSIC_IR
@IRANMUSIC_IR'''
        bot.sendMessage(message['chat']['id'], text, reply_markup={
            'inline_keyboard': [
                [
                    InlineKeyboard(text='عضو شدم 😊', callback_data='join')
                ]
            ]
        })


@bot.message('audio')
def audio(message):
    print(message)
    try:
        r.hset('audio_tag', message['from']['id'], message['audio']['file_id'])
        text = ''' {} : {}'''.format(message['audio']['title'], message['audio']['performer'])
        bot.sendMessage(message['chat']['id'], text, reply_to_message_id=message['message_id'],
                        reply_markup={
                            'inline_keyboard': [
                                [
                                    InlineKeyboard(text='ویرایش تگ 🎧', callback_data='tag'),
                                    InlineKeyboard(text='🎼 ساخت دمو', callback_data='demo'),
                                ],
                                [
                                    InlineKeyboard(text='🖼 ویرایش کاور ', callback_data='image')
                                ]
                            ]
                        })
    except Exception as e:
        print(e)
        bot.sendMessage(message['chat']['id'], 'نشد که ☹️')


@bot.callback_query()
def call(message):
    try:
        if join(message):
            if message['data'] == 'demo':
                file_id = r.hget('audio_tag', message['from']['id'])
                file_info = bot.getFile(file_id)
                download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                         'audio/{}.mp3'.format(message['from']['id']))
                os.system('cutmp3 -i audio/{}.mp3 -O audio/{}-tag.mp3 -a 0:15.0 -b 0:45.0'.format(message['from']['id'],
                                                                                                  message['from'][
                                                                                                      'id']))
                bot.editMessageText('🔄ساخت و ارسال دمو', message['message']['chat']['id'],
                                    message_id=message['message']['message_id'])
                bot.sendChatAction(message['message']['chat']['id'], 'upload_document')
                bot.sendVoice(message['message']['chat']['id'],
                              voice=open('audio/{}-tag.mp3'.format(message['from']['id']), 'rb'))
                os.remove('audio/{}.mp3'.format(message['from']['id']))
                os.remove('audio/{}-tag.mp3'.format(message['from']['id']))

            if message['data'] == 'tag':
                text = '''برای ویرایش تگ موزیک روی موزیک ریپلی کنید و به صورت زیر عنوان و نام خواننده را وارد کنید👇🏻

عنوان : خواننده'''
                bot.answerCallbackQuery(message['id'], text, True)
            if message['data'] == 'image':
                text = 'برای ویرایش کاور موزیک (عکس موزیک) ابتدا فایل موزیک را ارسال کرده سپس عکسی را که میخواهید با کاور فعلی تعویض شود را روی موزیک ریپلی و ارسال کنید.'
                bot.answerCallbackQuery(message['id'], text, True)
            if message['data'] == 'join':
                text = '''سلام دوست عزیز من ☺️🌹

به ربات ویرایش تگ موزیک و همچنین ساخت دمو خوش اومدی 🙃
برای شروع کار کافیه فقط فایل موزیکتو برای من بفرستی 🤓
برو بریم🏃'''
                bot.sendMessage(message['message']['chat']['id'], text)
        else:
            text = '''سلام 😝
چرا تو چنلمون عضو نیستی؟🙁😔
من کار نمیکنم تا اینکه عضو بشی😜
وارد کانال زیر بشو و بعدش دکمه زیر این متنو بزن 🤗
@IRANMUSIC_IR
@IRANMUSIC_IR'''
            bot.sendMessage(message['message']['chat']['id'], text, reply_markup={
                'inline_keyboard': [
                    [
                        InlineKeyboard(text='عضو شدم 😊', callback_data='join')
                    ]
                ]
            })
    except:
        bot.sendMessage(message['message']['chat']['id'], 'نشد که ☹️')


@bot.command(r'^(.*):(.*)$')
def tag(message, matches):
    try:
        if join(message):
            if 'reply_to_message' in message:
                if 'audio' in message['reply_to_message']:
                    file_id = r.hget('audio_tag', message['from']['id'])
                    file_info = bot.getFile(file_id)
                    download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                             'audio/{}.mp3'.format(message['from']['id']))
                    bot.sendChatAction(message['chat']['id'], 'upload_document')
                    bot.sendAudio(message['chat']['id'], audio=open('audio/{}.mp3'.format(message['from']['id']), 'rb'),
                                  duration=message['reply_to_message']['audio']['duration'],
                                  performer=matches[1], title=matches[0])
                    os.remove('audio/{}.mp3'.format(message['from']['id']))
        else:
            text = '''سلام 😝
چرا تو چنلمون عضو نیستی؟🙁😔
من کار نمیکنم تا اینکه عضو بشی😜
وارد کانال زیر بشو و بعدش دکمه زیر این متنو بزن 🤗
@IRANMUSIC_IR
@IRANMUSIC_IR'''
            bot.sendMessage(message['chat']['id'], text, reply_markup={
                'inline_keyboard': [
                    [
                        InlineKeyboard(text='عضو شدم 😊', callback_data='join')
                    ]
                ]
            })
    except Exception as e:
        bot.sendMessage(message['chat']['id'], 'نشد که ☹️')
        print(e)


@bot.message('photo')
def photo(message):
    try:
        # print(message)
        if join(message):
            if 'reply_to_message' in message:
                if 'audio' in message['reply_to_message']:
                    file_id = r.hget('audio_tag', message['from']['id'])
                    file_info = bot.getFile(file_id)
                    download('https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info['file_path']),
                             'audio/{}.mp3'.format(message['from']['id']))
                    fileid = message['photo'][2]['file_id']
                    fileinfo = bot.getFile(fileid)
                    download('https://api.telegram.org/file/bot{0}/{1}'.format(token, fileinfo['file_path']),
                             'image/{}.png'.format(message['from']['id']))
                    img('audio/{}.mp3'.format(message['from']['id']),
                               'image/{}.png'.format(message['from']['id']))
                    bot.sendAudio(message['chat']['id'], audio=open('audio/{}.mp3'.format(message['from']['id']), 'rb'),
                                  performer=message['reply_to_message']['audio']['performer'],
                                  title=message['reply_to_message']['audio']['title'])
                    os.remove('audio/{}.mp3'.format(message['from']['id']))
                    os.remove('image/{}.png'.format(message['from']['id']))


    except Exception as e:
        print(e)
        bot.sendMessage(message['chat']['id'], 'عملیات تعویض کاور ناموفق بود -ـ-')


bot.run(False)

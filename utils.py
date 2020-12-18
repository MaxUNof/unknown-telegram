# -*- coding: utf-8 -*-
# Coded by @maxunof with power of Senko!

from telethon.extensions import html
from telethon.tl.custom.message import Message


def escape_html(source):
    changes = {"&": "&amp;", "<": "&lt;",
               ">": "&gt;", "\"": "&quot;", "'": "&#39;"}
    for frm, to in changes.items():
        source = source.replace(frm, to)
    return source


async def send(message, content, **kwargs):
    res = []
    if isinstance(content, Message):
        res.append(await message.respond(content, **kwargs))
        try:
            await message.delete()
        except:
            pass
        return res
    if isinstance(content, str) and not kwargs.get("force_file", False):
        text, entities = html.parse(content)
        if message.sender_id != (await message.client.get_me()).id:
            await message.reply(html.unparse(text[:4096], entities))
        else:
            await message.edit(html.unparse(text[:4096], entities))
        text = text[4096:]
        res.append(message)
        while len(text) > 0:
            message.entities = entities
            message.text = html.unparse(text[:4096], message.entities)
            text = text[4096:]
            res.append(await message.respond(message, parse_mode="HTML", **kwargs))
        return res
    else:
        if message.media is None:
            await message.edit("<b>Sending media...</b>")
            res.append(await message.client.send_file(entity=message.chat_id,
                                                      file=content, reply_to=message.reply_to_msg_id, **kwargs))
            await message.delete()
            return res
        else:
            res.append(await message.edit(file=content, **kwargs))
            return res


def format_seconds(sec):
    MINUTE = 60
    HOUR = MINUTE * 60
    DAY = HOUR * 24
    days = int(sec / DAY)
    hours = int((sec % DAY) / HOUR)
    minutes = int((sec % HOUR) / MINUTE)
    seconds = int(sec % MINUTE)
    string = ""
    if days > 0:
        string += str(days) + " " + (days == 1 and "day" or "days") + ", "
    if hours > 0:
        string += str(hours) + " " + (hours == 1 and "hour" or "hours") + ", "
    if minutes > 0:
        string += str(minutes) + " " + (minutes ==
                                        1 and "minute" or "minutes") + ", "
    string += str(seconds) + " " + (seconds == 1 and "second" or "seconds")
    return string

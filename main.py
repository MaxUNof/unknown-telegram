# -*- coding: utf-8 -*-
# Coded by @maxunof with power of Senko!

import cmd
import importlib
import logging
import os
import subprocess
import sys

from git import Repo
from telethon.sync import TelegramClient, events
from tinydb import Query, TinyDB

import moduling
import utils

GIT_MASTER = "https://github.com/m4xx1m/unknown-telegram.git"

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(filename="utg.log", level=logging.INFO, filemode="w")
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

db = TinyDB('db.json')

# TODO: Do this better
restart = False

logging.info("Loading modules...")

modules = moduling.get_modules(
    moduling.get_modules_py("sysmodules"), db, system=True) + moduling.get_modules(moduling.get_modules_py("modules"), db)

logging.info("Modules loaded: {}".format(len(modules)))

class CoreModule(moduling.Module):
    def __init__(self):
        self.name = "Core"
        self.props = {
            "commands": {
                "help": self.help_cmd,
                "update": self.update_cmd,
                "restart": self.restart_cmd
            },
            "incoming_handler": None,
            "system": True
        }

    def format_command(self, mod):
        cmds = []
        for cmdname, _ in mod.props["commands"].items():
            cmds.append(cmdname)
        if len(cmds) == 0:
            return "<b>• {}</b>".format(mod.name)
        return "<b>• {}:</b> <code>{}</code>".format(mod.name, ', '.join(cmds))

    async def help_cmd(self, client, message, cmd):
        sysmods = []
        usermods = []
        for mod in modules:
            cmd = self.format_command(mod)
            if mod.props["system"]:
                sysmods.append(cmd)
                continue
            usermods.append(cmd)
        await utils.send(message, "<b>Help for Unknown Telegram</b>\n\n<b>System Modules:</b>\n{}\n\n<b>User Modules:</b>\n{}".format('\n'.join(sysmods), '\n'.join(usermods)))

    async def update_cmd(self, client, message, cmd):
        await utils.send(message, "<b>Fetching last version from the git...</b>")
        repo = Repo(ROOT_DIR)
        try:
            origin = repo.remotes['origin']
            repo.delete_remote(origin)
        except:
            pass
        try:
            origin = repo.create_remote('origin', GIT_MASTER)
        except:
            await utils.send(message, "<b>Can't recreate origin!</b>")
            return
        hash = ""
        newhash = ""
        try:
            hash = repo.commit("master").__str__()
        except:
            pass
        try:
            fetch = origin.fetch()
            newhash = fetch[0].commit.__str__()
        except:
            await utils.send(message, "<b>Invalid git credentials!</b>")
            return
        if not 'master' in repo.heads:
            repo.create_head("master", origin.refs.master)
        repo.heads.master.set_tracking_branch(origin.refs.master)
        repo.heads.master.checkout(True)
        if hash == newhash:
            await utils.send(message, "<b>Already up to date!</b>")
            return
        origin.pull()
        await utils.send(message, "<b>Updating requirements...</b>")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "--user", "-r",
                            os.path.join(ROOT_DIR, "requirements.txt")])
        except subprocess.CalledProcessError:
            await utils.send(message, "<b>Can't update requirements!</b>")
            return
        await utils.send(message, "<b>Update completed!</b>")
        global restart
        restart = True
        await client.disconnect()
        return

    async def restart_cmd(self, client, message, cmd):
        await utils.send(message, "<b>Restarting...</b>")
        global restart
        restart = True
        await client.disconnect()

modules.insert(0, CoreModule())


async def outgoing_handler(event):
    client = event._client
    message = event.message
    command = cmd.Command(message.raw_text)
    if command.cmd == "":
        return
    for module in modules:
        if command.cmd in module.props["commands"]:
            try:
                await module.props["commands"][command.cmd](client, message, command)
            except Exception as e:
                logging.error(e)
                await utils.send(message, "<b>An error occurred while executing the module.</b>")
            break

async def incoming_handler(event):
    client = event._client
    message = event.message
    for module in modules:
        if module.props["incoming_handler"] is None:
            continue
        try:
            await module.props["incoming_handler"](client, message)
        except Exception as e:
            logging.error(e)


client = TelegramClient(
    'utg',
    api_id=6,
    api_hash="eb06d4abfb49dc3eeb1aeb98ae0f581e",
    app_version="6.0.1 (19117)",
    device_model="OnePlusONEPLUS A5010",
    system_version="SDK 29")
client.parse_mode = "html"
client.start(lambda: input('Please enter your phone: '))
client.add_event_handler(incoming_handler,
                         events.NewMessage(incoming=True))
client.add_event_handler(outgoing_handler,
                         events.NewMessage(outgoing=True, forwards=False))
client.run_until_disconnected()

if restart:
    logging.info("Restarting...")
    python = sys.executable
    if sys.platform == 'win32':
        cmd = [python] + sys.argv
        cmd = subprocess.list2cmdline(cmd)
        sts = os.spawnv(os.P_WAIT, python, [cmd])
        os._exit(sts)
    else:
        os.execl(python, python, *sys.argv)

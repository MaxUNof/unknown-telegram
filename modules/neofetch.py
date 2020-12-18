# -*- coding: utf-8 -*-
# Coded by m4xx1m

import moduling
import utils
import os

class Module(moduling.Module):
    def __init__(self, db):
        self.name = "Neofetch"

    async def neofetch_cmd(self, client, message, cmd):
        await message.edit('<code>' + os.popen('neofetch --stdout').read() + '</code>')

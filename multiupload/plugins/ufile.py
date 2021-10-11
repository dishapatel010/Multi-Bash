'''MultiUpload, An Telegram Bot Project
Copyright (c) 2021 Anjana Madu and Amarnath CDJ <https://github.com/AnjanaMadu>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>'''

import asyncio, os, requests, time
from configs import Config
from requests import post
from multiupload import anjana
from telethon.sync import events, Button
from multiupload.fsub import *
from multiupload.utils import downloader, humanbytes
from config import LOG_CHANNEL

@anjana.on(events.NewMessage(pattern='^/ufile'))
async def ufile(event):
	user_id = event.sender_id
	if event.is_private and not await check_participant(user_id, f'@{Config.CHNLUSRNME}', event):
		return
	if event.reply_to_msg_id:
		pass
	else:
		return await event.edit("Please Reply to File")

	async with anjana.action(event.chat_id, 'typing'):
		await asyncio.sleep(2)
	msg = await event.reply("**Processing...**")
	amjana = await event.get_reply_message()


	## LOGGING TO A CHANNEL
	xx = await event.get_chat()
	reqmsg = f'''Req User: [{xx.first_name}](tg://user?id={xx.id})
FileName: {amjana.file.name}
FileSize: {humanbytes(amjana.file.size)}
#UFILE'''
	await anjana.send_message(LOG_CHANNEL, reqmsg)

	result = await downloader(
		f"downloads/{amjana.file.name}",
		amjana.media.document,
		msg,
		time.time(),
		f"**🏷 Downloading...**\n➲ **File Name:** {amjana.file.name}",
	)

	async with anjana.action(event.chat_id, 'document'):
		await msg.edit("Now Uploading to UFile")
		r = post('https://up.ufile.io/v1/upload/create_session',
			data={'file_size': amjana.file.size})

		r2 = post('https://up.ufile.io/v1/upload/chunk',
			stream=True,
			data={'chunk_index': 1, 'fuid': r.json()["fuid"]},
			files={'file': open(f'{result.name}','rb')}
			)

		url = "https://up.ufile.io/v1/upload/finalise"
		r3 = post(url, data={
			'fuid': r.json()["fuid"],
			'file_name': result.name,
			'file_type': result.name.split(".")[-1],
			'total_chunks': 1
			})
	await anjana.action(event.chat_id, 'cancel')

	hmm = f'''File Uploaded successfully !!
Server: UFile

**~ File name:** __{amjana.file.name}__
**~ File size:** __{humanbytes(amjana.file.size)}__
NOTE: Bandwidth limit is 1MB/s. After a month files will be deleted.'''
	await msg.edit(hmm, buttons=(
		[Button.url('📦 Download', r3.json()['url'])],
		[Button.url('Support Chat 💭', 't.me/harp_chat')]
		))

	os.remove(result.name)
# MIT License
# see LICENSE for details

# Copyright (c) 2019 Arkrissym


import random

from discord.ext.commands import Cog

from core import config


class Moderation(Cog):
	@Cog.listener()
	async def on_member_join(self, member):
		messages = config.strings[config.getLocale(member.guild.id)]['bot']['member_join_msg']
		msg = random.randint(0, len(messages) - 1)
		ch = member.guild.system_channel
		if not ch:
			for ch in member.guild.text_channels:
				break

		await ch.send(messages[msg].format(member.name))

	@Cog.listener()
	async def on_member_remove(self, member):
		messages = config.strings[config.getLocale(member.guild.id)]['bot']['member_remove_msg']
		msg = random.randint(0, len(messages) - 1)
		ch = member.guild.system_channel
		if not ch:
			for ch in member.guild.text_channels:
				break

		await ch.send(messages[msg].format(member.name))

	@Cog.listener()
	async def on_member_ban(self, guild, user):
		ch = guild.system_channel
		if not ch:
			for ch in guild.text_channels:
				break

		await ch.send(config.strings[config.getLocale(guild.id)]['bot']['member_ban_msg'].format(user.name))

	@Cog.listener()
	async def on_member_unban(self, guild, user):
		ch = guild.system_channel
		if not ch:
			for ch in guild.text_channels:
				break

		await ch.send(config.strings[config.getLocale(guild.id)]['bot']['member_unban_msg'].format(user.name))


def setup(bot):
	bot.add_cog(Moderation())

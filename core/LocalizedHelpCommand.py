# MIT License
# see LICENSE for details

# Copyright (c) 2019 Arkrissym

import discord
from discord.ext import commands

from core import config


class LocalizedHelpCommand(commands.DefaultHelpCommand):
	def __init__(self, **options):
		super().__init__(**options)

	def command_not_found(self, string):
		locale = config.getLocale(self.context.guild.id)
		return config.strings[locale]["bot"]["command_not_found"].format(string)

	def subcommand_not_found(self, command, string):
		locale = config.getLocale(self.context.guild.id)
		if isinstance(command, commands.Group) and len(command.all_commands) > 0:
			return config.strings[locale]["bot"]["sub_command_not_found_1"].format(command, string)
		return config.strings[locale]["bot"]["sub_command_not_found_2"].format(command)

	def get_ending_note(self):
		locale = config.getLocale(self.context.guild.id)
		command_name = self.context.invoked_with
		return config.strings[locale]["bot"]["help_command_ending_note"].format(self.clean_prefix, command_name)

	def add_indented_commands(self, cmds, *, heading, max_size=None):
		if not cmds:
			return

		locale = config.getLocale(self.context.guild.id)

		self.paginator.add_line(heading)
		max_size = max_size or self.get_max_size(cmds)

		get_width = discord.utils._string_width
		for command in cmds:
			name = command.name
			width = max_size - (get_width(name) - len(name))

			short_doc = command.short_doc
			try:
				module_name = short_doc.split("+")[0]
				string_name = short_doc.split("+")[1]
				short_doc = config.strings[locale][module_name][string_name]
			except:
				pass

			entry = '{0}{1:<{width}} {2}'.format(self.indent * ' ', name, short_doc, width=width)
			self.paginator.add_line(self.shorten_text(entry))

	def add_command_formatting(self, command):
		locale = config.getLocale(self.context.guild.id)

		if command.description:
			description = command.description

			try:
				module_name = description.split("+")[0]
				string_name = description.split("+")[1]
				description = config.strings[locale][module_name][string_name]
			except:
				pass
			self.paginator.add_line(description, empty=True)

		signature = self.get_command_signature(command)
		self.paginator.add_line(signature, empty=True)

		if command.help:
			help_string = command.help
			try:
				module_name = help_string.split("+")[0]
				string_name = help_string.split("+")[1]
				help_string = config.strings[locale][module_name][string_name]
			except:
				pass
			self.paginator.add_line(help_string, empty=True)

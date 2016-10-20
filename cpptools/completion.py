from subprocess import *
from gi.repository import GObject, Gdk, Gtk, Gio, GtkSource, Gedit
import os, re
from settings import settings

# for stripping
def find_between(s, start, end):
	return (s.split(start))[1].split(end)[0]

# replace html chars
def escape_html(s):
	return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def unescape_html(s):
	return s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")

# Completion provider
class CppToolsAutocompleteProvider(GObject.Object, GtkSource.CompletionProvider):
	__gtype_name__ = 'CppToolsAutocompleteProvider'

	def __init__(self, doc):
		GObject.Object.__init__(self)
		self.priority = 1
		self.document = doc
		self.proposals = []
		self.index = -1

	def do_get_name(self):
		return "CppToolsAutocomplete"

	def do_get_priority(self):
		return self.priority

	def do_match(self, context):
		return True

	def do_populate(self, context):
		# get document
		doc = self.document

		# get text
		start_iter = doc.get_start_iter()
		end_iter = doc.get_end_iter()
		text = doc.get_text(start_iter, end_iter, True)

		# get position
		mark = doc.get_mark('insert')
		iter = doc.get_iter_at_mark(mark)
		row = iter.get_line() + 1
		col = iter.get_line_offset() + 1

		# get current line and last character
		start_iter = doc.get_iter_at_line(row-1)
		end_iter = doc.get_iter_at_line(row-1)
		end_iter.forward_to_line_end()
		line = doc.get_text(start_iter, end_iter, True)
		last_char = line[col-2]

		# check if we are complete after this characters
		if last_char != '.' and last_char != ':' and last_char != ',' and last_char != '(' and last_char != '<' and last_char != '>' and last_char != '\t' and last_char != ' ':
			# filter old completions
			newproposals = list()
			if self.index != -1:
				for prop in self.proposals:
					if prop.get_text().startswith(line[self.index:col-1]):
						newproposals.append(prop)

			context.add_proposals(self, newproposals, True)

			return

		# remember position of autocomplete
		self.index = col - 1

		includes = ''
		include_arr = settings.get_string('includes').split()
		for inc in include_arr:
			includes += "-I" + inc + " "

		# execute autocomplete provider
		cmd = "clang -cc1 -fsyntax-only -x c++ -std=c++11 -code-completion-macros " + includes + " -code-completion-at=-:{}:{} -".format(row, col)

		p = Popen(cmd, cwd=os.path.dirname(doc.get_uri_for_display()), shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
		output, err = p.communicate(input = text.encode())

		# add completions
		self.proposals = []
		completes = output.splitlines()
		for complete in completes:
			if not complete.startswith(b'COMPLETION'):
				return

			complete = complete.decode('utf-8') # byte to string
			sindex = complete.find(':')
			eindex = complete.find(':', sindex+2)

			# check for signature
			if eindex != -1:
				symbol = complete[sindex+1:eindex].strip() # get symbol
			else:
				symbol = complete[sindex+1:].strip()

			# exclude patterns
			if symbol == 'Pattern':
				continue

			temp = complete # temporary string
			temp = temp.replace('#]', '#] ', 1) # additional space
			temp = temp.replace('<#', '').replace('#>', '').replace('[#', '').replace('#]', '').replace('{#', '').replace('#}', '') # strip helpers

			index = temp.find(' : ')
			if index == -1:
				temp = temp[temp.find(': ') + 2:] # get signature
			else:
				temp = temp[index + 2:] # get signature

			signature = temp.strip()
			index = temp.find(symbol)

			if index == -1:
				completion = signature
			else:
				completion = temp[index:].strip() # without returntype

			self.proposals.append(GtkSource.CompletionItem.new(signature, completion, None, None))

		# show proposals
		context.add_proposals(self, self.proposals, True)

	def set_priority(self, priority):
		self.priority = priority

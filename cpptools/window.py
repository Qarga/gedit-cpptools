from subprocess import *
from gi.repository import GObject, Gdk, Gtk, Gio, GtkSource, Gedit
from completion import CppToolsAutocompleteProvider
from settings import settings

# Window Plugin
class CppToolsWindowPlugin(GObject.Object, Gedit.WindowActivatable):
	__gtype_name__ = "CppToolsPlugin"

	window = GObject.property(type = Gedit.Window)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self._insert_menu()
		pass

	def register(self, window, tab):
		# check language
		language = tab.get_document().get_language().get_name()
		if language != "C" and language != "C++":
			return

		# check if provider exists
		for provider in tab.get_view().get_completion().get_providers():
			if provider.get_name() == "CppToolsAutocomplete":
				return

		# add provider
		complete = CppToolsAutocompleteProvider(tab.get_document())
		tab.get_view().get_completion().add_provider(complete)
		pass

	def do_deactivate(self):
		self._remove_menu()
		pass

	def _insert_menu(self):
		action = Gio.SimpleAction(name="formatcode")
		action.connect('activate', lambda a, p: self.on_format_code())
		self.window.add_action(action)

	def _remove_menu(self):
		self.window.remove_action("formatcode")

	def on_format_code(self):
		# get document
		doc = self.window.get_active_tab().get_document()

		# get text
		start_iter = doc.get_start_iter()
		end_iter = doc.get_end_iter()
		text = doc.get_text(start_iter, end_iter, True)

		# execute autocomplete provider
		cmd = "clang-format -style=" + settings.get_string('formatstyle')
		p = Popen(cmd, shell=True, stdout=PIPE, stdin=PIPE, stderr=PIPE)
		output, err = p.communicate(input = text.encode())

		doc.set_text(output.decode('utf-8'))

		pass

	def do_update_state(self):
		self.register(self.window, self.window.get_active_tab())

		language = self.window.get_active_tab().get_document().get_language().get_name()
		enabled = (language == "C" or language == "C++")
		self.window.lookup_action("formatcode").set_enabled(enabled)
		pass

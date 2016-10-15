from gi.repository import GObject, Gio, GLib, PeasGtk, Gtk, Gedit
import os, locale, gettext
from settings import settings

APP="cpptools"
DIR=os.path.dirname(__file__)

locale.setlocale(locale.LC_ALL, '')
gettext.bindtextdomain(APP, DIR + '/locale/')
gettext.textdomain(APP)
_ = gettext.gettext

# App Plugin to format code menu
class CppToolsAppPlugin(GObject.Object, Gedit.AppActivatable, PeasGtk.Configurable):
	app = GObject.Property(type=Gedit.App)

	def __init__(self):
		GObject.Object.__init__(self)

	def do_activate(self):
		self.menu_ext = self.extend_menu("tools-section-1")
		item = Gio.MenuItem()
		item.set_attribute_value("accel", GLib.Variant("s", "<Alt><Shift>F"))
		item.set_attribute_value("label", GLib.Variant("s", _("Format code")))
		item.set_attribute_value("action", GLib.Variant("s", "win.formatcode"))
		self.menu_ext.append_menu_item(item)

	def do_create_configure_widget(self):
		saved_style = settings.get_string('formatstyle')
		saved_includes = settings.get_string('includes')

		styles = ['LLVM', 'Google', 'Chromium', 'Mozilla', 'Webkit']

		content = Gtk.VBox()
		content.set_spacing(5)

		format_style_box = Gtk.HBox()
		format_style_label = Gtk.Label(_('Format style'))
		format_style_widget = Gtk.ComboBoxText()
		format_style_widget.set_entry_text_column(0)

		i = 0
		for style in styles:
			format_style_widget.append_text(style)
			if style == saved_style:
				format_style_widget.set_active(i)

			i = i + 1

		format_style_widget.connect('changed', self.on_formatstyle_changed)
		format_style_box.pack_start(format_style_label, False, False, 10)
		format_style_box.pack_end(format_style_widget, False, False, 10)

		includes_box = Gtk.ScrolledWindow()
		includes_text = Gtk.TextView()
		includes_text.get_buffer().set_text(saved_includes)
		includes_text.get_buffer().connect('changed', self.on_includes_changed)
		includes_box.add(includes_text)
		includes_label = Gtk.Label(_('System includes'))

		content.pack_start(format_style_box, False, False, 0)
		content.pack_start(includes_label, False, False, 0)
		content.pack_start(includes_box, True, True, 0)
		content.show_all()

		return content

	def on_formatstyle_changed(self, combo):
		settings.set_string('formatstyle', combo.get_active_text())

	def on_includes_changed(self, buffer):
		start = buffer.get_start_iter()
		end = buffer.get_end_iter()
		includes = buffer.get_text(start, end, True)
		settings.set_string('includes', includes)

	def deactivate(self):
		self.menu_ext = None

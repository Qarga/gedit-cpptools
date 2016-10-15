from gi.repository import GObject, Gio, GLib, PeasGtk, Gtk, Gedit
import sys, os

path = os.path.dirname(__file__)

if not path in sys.path:
	sys.path.insert(0, path)

from app import CppToolsAppPlugin
from window import CppToolsWindowPlugin

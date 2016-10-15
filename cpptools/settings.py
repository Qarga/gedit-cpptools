from gi.repository import Gio
import os

DIR=os.path.dirname(__file__)
schema_source = Gio.SettingsSchemaSource.new_from_directory(DIR, Gio.SettingsSchemaSource.get_default(), False)
schema = Gio.SettingsSchemaSource.lookup(schema_source, 'ru.qarga.cpptools', False)
settings = Gio.Settings.new_full(schema, None, '/ru/qarga/cpptools/')

# -*- coding: utf-8 -*-
import os
from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt import QtCore

from qgis.utils import active_plugins
from .qgissettingmanager import *

CONFIG_FILE_URL = "https://qgisplugin.dataforsyningen.dk/qgis_plugin_dataforsyningen_datafordeler_udentoken.qlr"


class Settings(SettingManager):
    settings_updated = QtCore.pyqtSignal()

    def __init__(self):
        SettingManager.__init__(self, "Dataforsyningen")
        self.add_setting(String("dataforsyningen_token", Scope.Global, ""))
        self.add_setting(String("datafordeler_apikey", Scope.Global, ""))
        self.add_setting(Bool("use_custom_file", Scope.Global, False))
        self.add_setting(String("custom_qlr_file", Scope.Global, ""))
        self.add_setting(Bool("only_background", Scope.Global, False))
        path = QFileInfo(os.path.realpath(__file__)).path()
        df_path = path + "/df/"
        if not os.path.exists(df_path):
            os.makedirs(df_path)

        self.add_setting(String("cache_path", Scope.Global, df_path))
        self.add_setting(String("df_qlr_url", Scope.Global, CONFIG_FILE_URL))

    def dataforsyningen_set(self):
        dataforsyningen_set = False
        if self.value("dataforsyningen_token"):
            dataforsyningen_set = True
        elif (
            "Kortforsyningen" in active_plugins
        ):  # Take the token from kortforsyning plugin
            s = QtCore.QSettings()
            kortforsyningen_token = s.value("plugins/Kortforsyningen/token")
            if kortforsyningen_token:
                self.set_value("dataforsyningen_token", kortforsyningen_token)
                dataforsyningen_set = True

        return dataforsyningen_set

    def datafordeler_set(self):
        datafordeler_set = False
        if self.value("datafordeler_apikey"):
            datafordeler_set = True
        elif (
            "Kortforsyningen" in active_plugins
        ):  # Take the apikey from kortforsyning plugin
            s = QtCore.QSettings()
            kortforsyningen_apikey = s.value("plugins/Kortforsyningen/apikey")
            if kortforsyningen_apikey:
                self.set_value("datafordeler_apikey", kortforsyningen_apikey)
                datafordeler_set = True

        return datafordeler_set

    def emit_updated(self):
        self.settings_updated.emit()

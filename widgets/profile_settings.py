# coding=utf-8
"""
Created on 10.4.2018
Updated on 1.8.2018

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2018 Severi Jääskeläinen, Samuel Kaiponen, Heta Rekilä and
Sinikka Siironen, 2020 Juhani Sundell

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program (file named 'LICENCE').
"""
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä " \
             "\n Sinikka Siironen \n Juhani Sundell"

import widgets.input_validation as iv
import widgets.binding as bnd
import widgets.gui_utils as gutils

from pathlib import Path

from modules.measurement import Measurement

from widgets.preset_widget import PresetWidget

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QLocale


class ProfileSettingsWidget(QtWidgets.QWidget, bnd.PropertyTrackingWidget,
                            bnd.PropertySavingWidget,
                            metaclass=gutils.QtABCMeta):
    """Class for creating a profile settings tab.
    """
    # TODO track_change may not be necessary here, as none of these values
    #   are used for simulations
    name = bnd.bind("nameLineEdit", track_change=True)
    description = bnd.bind(
        "descriptionPlainTextEdit", track_change=True)
    modification_time = bnd.bind(
        "dateLabel", fget=bnd.unix_time_from_label,
        fset=bnd.unix_time_to_label)

    reference_density = bnd.bind(
        "referenceDensityDoubleSpinBox", track_change=True)
    number_of_depth_steps = bnd.bind(
        "numberOfDepthStepsSpinBox", track_change=True)
    depth_step_for_stopping = bnd.bind(
        "depthStepForStoppingSpinBox", track_change=True)
    depth_step_for_output = bnd.bind(
        "depthStepForOutputSpinBox", track_change=True)
    depth_for_concentration_from = bnd.bind(
        "depthForConcentrationFromDoubleSpinBox", track_change=True)
    depth_for_concentration_to = bnd.bind(
        "depthForConcentrationToDoubleSpinBox", track_change=True)
    channel_width = bnd.bind(
        "channelWidthDoubleSpinBox", track_change=True)
    number_of_splits = bnd.bind("numberOfSplitsSpinBox", track_change=True)
    normalization = bnd.bind(
        "normalizationComboBox", track_change=True)

    def __init__(self, measurement: Measurement, preset_folder=None):
        """
        Initializes the widget.

        Args:
            measurement: Measurement object.
        """
        super().__init__()
        uic.loadUi(gutils.get_ui_dir() / "ui_profile_settings_tab.ui", self)
        self.measurement = measurement
        self._original_properties = {}

        self.fields_are_valid = False
        iv.set_input_field_red(self.nameLineEdit)
        self.nameLineEdit.textChanged.connect(
            lambda: iv.check_text(self.nameLineEdit, qwidget=self))
        self.nameLineEdit.textEdited.connect(
            lambda: iv.sanitize_file_name(self.nameLineEdit))
        self.nameLineEdit.setEnabled(False)

        locale = QLocale.c()
        self.referenceDensityDoubleSpinBox.setLocale(locale)
        self.depthForConcentrationFromDoubleSpinBox.setLocale(locale)
        self.depthForConcentrationToDoubleSpinBox.setLocale(locale)
        self.channelWidthDoubleSpinBox.setLocale(locale)

        gutils.fill_combobox(self.normalizationComboBox, ["First"])
        self.set_properties(**self.measurement.profile.get_settings())

        gutils.set_min_max_handlers(
            self.depthForConcentrationFromDoubleSpinBox,
            self.depthForConcentrationToDoubleSpinBox,
            min_diff=0.01
        )

        if preset_folder is not None:
            self.preset_widget = PresetWidget.add_preset_widget(
                preset_folder / "profile", "pro",
                lambda w: self.layout().insertWidget(0, w),
                save_callback=self.save_properties_to_file,
                load_callback=self.load_properties_from_file
            )
        else:
            self.preset_widget = None

    def get_property_file_path(self) -> Path:
        raise NotImplementedError

    def save_on_close(self) -> bool:
        return False

    def save_properties_to_file(self, file_path: Path):
        def err_func(err: Exception):
            if self.preset_widget is not None:
                self.preset_widget.set_status_msg(
                    f"Failed to save preset: {err}")
        self._save_json_file(
            file_path, self.get_properties(), True, error_func=err_func)
        if self.preset_widget is not None:
            self.preset_widget.load_files(selected=file_path)

    def load_properties_from_file(self, file_path: Path):
        # TODO create a base class for settings widgets to get rid of this
        #   copy-paste code

        def err_func(err: Exception):
            if self.preset_widget is not None:
                self.preset_widget.set_status_msg(
                    f"Failed to load preset: {err}")
        bnd.PropertySavingWidget.load_properties_from_file(
            self, file_path, error_func=err_func)

    def get_original_property_values(self):
        """Returns the original values of this Widget's properties.
        """
        return self._original_properties

    def update_settings(self):
        """Update profile settings.
        """
        self.measurement.profile.set_settings(**self.get_properties())

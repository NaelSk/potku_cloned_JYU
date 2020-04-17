# coding=utf-8
"""
Created on 20.5.2019
Updated on 22.5.2019

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2019 Heta Rekilä

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

__author__ = "Heta Rekilä \n Juhani Sundell"
__version__ = "2.0"

import abc

import widgets.binding as bnd

from pathlib import Path

from widgets.binding import PropertyBindingWidget
from widgets.gui_utils import QtABCMeta

from PyQt5 import QtWidgets
from PyQt5 import uic
from PyQt5.QtCore import QLocale
from PyQt5.QtCore import Qt

_REC_TYPES = {
    "4-point box": ("box", 5),
    "6-point box": ("box", 7),
    "8-point two-peak": ("two-peak", 9),
    "10-point two-peak": ("two-peak", 11),
}
# Update _REC_TYPES to enable two-way binding based on solution sizes.
_REC_TYPES.update({
    (sol_size, key)
    for key, (rtype, sol_size) in _REC_TYPES.items()
})


def recoil_from_combobox(instance, combobox):
    """Converts the text value shown in combobox to a recoil type.
    """
    qbox = getattr(instance, combobox)
    return _REC_TYPES[qbox.currentText()][0]


def sol_size_from_combobox(instance, combobox):
    """Converts the text value shown in combobox to solution size.
    """
    qbox = getattr(instance, combobox)
    return _REC_TYPES[qbox.currentText()][1]


def sol_size_to_combobox(instance, combobox, value):
    """Sets the selected item in the given combobox based on the solution size.
    """
    qbox = getattr(instance, combobox)
    try:
        str_value = _REC_TYPES[value]
        qbox.setCurrentIndex(qbox.findText(str_value, Qt.MatchFixedString))
    except KeyError:
        pass


class OptimizationParameterWidget(QtWidgets.QWidget,
                                  PropertyBindingWidget,
                                  abc.ABC,
                                  metaclass=QtABCMeta):
    """Abstract base class for recoil and fluence optimization parameter
    widgets.
    """
    # TODO reorganize the input elements in the ui file (simulation,
    #  nsga2 and problem parameters should be in their own categories)
    # TODO disable simulation parameters when skip simulation is selected
    # Common properties
    gen = bnd.bind("generationSpinBox")
    pop_size = bnd.bind("populationSpinBox")
    number_of_processes = bnd.bind("processesSpinBox")
    cross_p = bnd.bind("crossoverProbDoubleSpinBox")
    mut_p = bnd.bind("mutationProbDoubleSpinBox")
    stop_percent = bnd.bind("percentDoubleSpinBox")
    check_time = bnd.bind("timeSpinBox")
    check_max = bnd.bind("maxTimeEdit")
    check_min = bnd.bind("minTimeEdit")
    skip_simulation = bnd.bind("skip_sim_chk_box")

    def __init__(self, ui_file, **kwargs):
        """Initializes a optimization parameter widget.

        Args:
            ui_file: relative path to a ui_file
            kwargs: values to show in the widget
        """
        super().__init__()
        uic.loadUi(ui_file, self)

        locale = QLocale.c()
        self.crossoverProbDoubleSpinBox.setLocale(locale)
        self.mutationProbDoubleSpinBox.setLocale(locale)
        self.percentDoubleSpinBox.setLocale(locale)

        self.set_properties(**kwargs)


class OptimizationRecoilParameterWidget(OptimizationParameterWidget):
    """
    Class that handles the recoil optimization parameters' ui.
    """

    # Recoil specific properties
    upper_limits = bnd.multi_bind(
        ("upperXDoubleSpinBox", "upperYDoubleSpinBox")
    )
    lower_limits = bnd.multi_bind(
        ("lowerXDoubleSpinBox", "lowerYDoubleSpinBox")
    )
    # sol_size values are unique (5, 7, 9 or 11) so they can be used in
    # two-way binding
    sol_size = bnd.bind("recoilTypeComboBox", fget=sol_size_from_combobox,
                        fset=sol_size_to_combobox)
    recoil_type = bnd.bind("recoilTypeComboBox", fget=recoil_from_combobox,
                           twoway=False)

    @property
    def optimize_recoil(self):
        return True

    def __init__(self, **kwargs):
        """Initialize the widget.

        Args:
            kwargs: property values to be shown in the widget.
        """
        ui_file = Path("ui_files", "ui_optimization_recoil_params.ui")
        super().__init__(ui_file, **kwargs)

        locale = QLocale.c()
        self.upperXDoubleSpinBox.setLocale(locale)
        self.lowerXDoubleSpinBox.setLocale(locale)
        self.upperYDoubleSpinBox.setLocale(locale)
        self.lowerYDoubleSpinBox.setLocale(locale)


class OptimizationFluenceParameterWidget(OptimizationParameterWidget):
    """
    Class that handles the fluence optimization parameters' ui.
    """

    # Fluence specific properties
    upper_limits = bnd.bind("fluenceDoubleSpinBox")
    dis_c = bnd.bind("disCSpinBox")
    dis_m = bnd.bind("disMSpinBox")

    @property
    def lower_limits(self):
        return 0.0

    @property
    def sol_size(self):
        return 1

    @property
    def optimize_recoil(self):
        return False

    def __init__(self, **kwargs):
        """Initialize the widget.

        Args:
            kwargs: property values to be shown in the widget.
        """
        ui_file = Path("ui_files", "ui_optimization_fluence_params.ui")
        super().__init__(ui_file, **kwargs)

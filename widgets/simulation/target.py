# coding=utf-8
"""
Created on 28.3.2018
Updated on 4.7.2018

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2018 Severi Jääskeläinen, Samuel Kaiponen, Heta Rekilä and
Sinikka Siironen

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
             "\n Sinikka Siironen"
__version__ = "2.0"

import os

from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5 import uic

from widgets.matplotlib.simulation.composition import TargetCompositionWidget
from widgets.matplotlib.simulation.recoil_atom_distribution import \
    RecoilAtomDistributionWidget


class TargetWidget(QtWidgets.QWidget):
    """ Widget that can be used to define target composition and
        recoil atom distribution.
    """

    def __init__(self, tab, simulation, target, icon_manager):
        """Initializes thw widget that can be used to define target composition
        and
        recoil atom distribution.

        Args:
            tab: A TabWidget.
            simulation: A Simulation object.
            target: A Target object.
            icon_manager: An icon manager class object.
        """
        super().__init__()
        self.ui = uic.loadUi(os.path.join("ui_files", "ui_target_widget.ui"),
                             self)

        self.tab = tab
        self.simulation = simulation
        self.target = target

        self.target_widget = TargetCompositionWidget(self, self.target,
                                                     icon_manager)
        self.recoil_distribution_widget = RecoilAtomDistributionWidget(
            self, self.simulation, self.target, tab, icon_manager)

        icon_manager.set_icon(self.ui.editPushButton, "edit.svg")
        self.ui.editPushButton.setIconSize(QtCore.QSize(14, 14))
        self.ui.editPushButton.setToolTip(
            "Edit name, description and reference density "
            "of this recoil element")
        self.ui.recoilListWidget.hide()
        self.ui.editLockPushButton.hide()
        self.ui.elementInfoWidget.hide()

        self.ui.exportElementsButton.clicked.connect(
            self.recoil_distribution_widget.export_elements)

        self.ui.targetRadioButton.clicked.connect(self.switch_to_target)
        self.ui.recoilRadioButton.clicked.connect(self.switch_to_recoil)

        self.ui.targetRadioButton.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(0)

        self.ui.saveButton.clicked.connect(lambda:
                                           self.__save_target_and_recoils())

        self.del_points = None

        self.set_shortcuts()

    def switch_to_target(self):
        """
        Switch to target view.
        """
        self.recoil_distribution_widget.original_x_limits = \
            self.recoil_distribution_widget.axes.get_xlim()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.recoilListWidget.hide()
        self.ui.editLockPushButton.hide()
        self.ui.exportElementsButton.show()
        self.ui.elementInfoWidget.hide()
        self.ui.instructionLabel.setText("")

    def switch_to_recoil(self):
        """
        Switch to recoil atom distribution view.
        """
        self.ui.stackedWidget.setCurrentIndex(1)
        self.recoil_distribution_widget.update_layer_borders()
        self.ui.exportElementsButton.hide()
        self.ui.recoilListWidget.show()
        self.ui.editLockPushButton.show()
        self.recoil_distribution_widget.recoil_element_info_on_switch()
        self.ui.instructionLabel.setText("You can add a new point to the "
                                         "distribution on a line between "
                                         "points using Ctrl+click ("
                                         "macOs users ⌘+click).")

    def __save_target_and_recoils(self):
        """
        Save target and element simulations.
        """
        target_name = "temp"
        if self.target.name is not "":
            target_name = self.target.name
        target_path = os.path.join(self.simulation.directory, target_name +
                                   ".target")
        self.target.to_file(target_path, None)

        self.recoil_distribution_widget.save_mcsimu_rec_profile(
            self.simulation.directory)

    def set_shortcuts(self):
        """
        Set shortcuts for deleting points.
        """
        self.del_points = QtWidgets.QShortcut(self)
        self.del_points.setKey(QtCore.Qt.Key_Delete)
        self.del_points.activated.connect(
            lambda: self.recoil_distribution_widget.remove_points())

# coding=utf-8
"""
Created on 1.3.2018
Updated on 22.5.2018
"""
from PyQt5.QtGui import QIcon

from dialogs.energy_spectrum import EnergySpectrumParamsDialog, \
    EnergySpectrumWidget

__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n " \
             "Sinikka Siironen"
__version__ = "2.0"

from PyQt5 import QtWidgets


class SimulationControlsWidget(QtWidgets.QWidget):
    """Class for creating simulation controls widget for the element simulation.

    Args:
        element_simulation: ElementSimulation object.
    """

    def __init__(self, element_simulation):
        super().__init__()

        self.element_simulation = element_simulation

        main_layout = QtWidgets.QHBoxLayout()

        controls_group_box = QtWidgets.QGroupBox(self.element_simulation.name)
        controls_group_box.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                                         QtWidgets.QSizePolicy.Preferred)

        state_layout = QtWidgets.QHBoxLayout()
        state_layout.addWidget(QtWidgets.QLabel("State: "))
        self.state_label = QtWidgets.QLabel("Not started")
        state_layout.addWidget(self.state_label)
        state_widget = QtWidgets.QWidget()
        state_widget.setLayout(state_layout)

        controls_layout = QtWidgets.QHBoxLayout()
        run_button = QtWidgets.QPushButton("Start")
        run_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                 QtWidgets.QSizePolicy.Fixed)
        run_button.clicked.connect(self.__start_simulation)
        stop_button = QtWidgets.QPushButton("Stop")
        stop_button.setSizePolicy(QtWidgets.QSizePolicy.Fixed,
                                  QtWidgets.QSizePolicy.Fixed)
        stop_button.clicked.connect(self.__stop_simulation)
        controls_layout.addWidget(run_button)
        controls_layout.addWidget(stop_button)
        controls_widget = QtWidgets.QWidget()
        controls_widget.setLayout(controls_layout)

        processes_layout = QtWidgets.QFormLayout()
        processes_label = QtWidgets.QLabel("No. of processes: ")
        processes_spinbox = QtWidgets.QSpinBox()
        processes_spinbox.setToolTip("Number of processes used in simulation")
        processes_layout.addRow(processes_label, processes_spinbox)
        processes_widget = QtWidgets.QWidget()
        processes_widget.setLayout(processes_layout)

        state_and_controls_layout = QtWidgets.QVBoxLayout()
        state_and_controls_layout.addWidget(processes_widget)
        state_and_controls_layout.addWidget(state_widget)
        state_and_controls_layout.addWidget(controls_widget)

        controls_group_box.setLayout(state_and_controls_layout)

        main_layout.addWidget(controls_group_box)

        self.setLayout(main_layout)

    def __start_simulation(self):
        """ Calls ElementSimulation's start method.
        """
        self.element_simulation.start()
        self.state_label.setText("Running")

    def __stop_simulation(self):
        """ Calls ElementSimulation's stop method.
        """
        self.element_simulation.stop()
        self.state_label.setText("Stopped")

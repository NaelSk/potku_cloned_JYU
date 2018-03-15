# coding=utf-8
'''
Created on 5.3.2018
Updated on 15.3.2018
'''
__author__ = "Severi Jääskeläinen \n Samuel Kaiponen \n Heta Rekilä \n Sinikka Siironen"

from PyQt5 import QtWidgets, uic
import sys, logging, os
from Widgets.MatplotlibSimulationEnergySpectrumWidget import MatplotlibSimulationEnergySpectrumWidget


class SimulationEnergySpectrumWidget(QtWidgets.QWidget):
    """ Simulation energy spectrum widget which is added to the simulation tab.
    """

    def __init__(self, parent):
        """ Initialize the energy spectrum widget.
        Args:
            parent: Parent of the energy spectrum widget (SimulationTabWidget)
        """
        try:
            super().__init__()
            self.parent = parent
            self.icon_manager = parent.icon_manager
            self.ui = uic.loadUi(os.path.join("ui_files", "ui_energy_spectrum_simu.ui"), self)
            self.icon_manager = parent.icon_manager
            self.progress_bar = None
            title = str(self.ui.windowTitle())
            self.ui.setWindowTitle(title)
            self.simulation = parent.simulation
            self.ui.saveSimuEnergySpectraButton.clicked.connect(self.save_spectra)
            self.energy_spectrum_data = {}

            # Graph in matplotlib widget and add to window
            self.matplotlib = MatplotlibSimulationEnergySpectrumWidget(
                self,
                self.energy_spectrum_data)
        except:
            import traceback
            msg = "Could not create Energy Spectrum graph. "
            err_file = sys.exc_info()[2].tb_frame.f_code.co_filename
            str_err = ", ".join([sys.exc_info()[0].__name__ + ": " + \
                                 traceback._some_str(sys.exc_info()[1]),
                                 err_file,
                                 str(sys.exc_info()[2].tb_lineno)])
            msg += str_err
            logging.getLogger(self.simulation.simulation_name).error(msg)
            if hasattr(self, "matplotlib"):
                self.matplotlib.delete()
        finally:
            if self.progress_bar:
                self.measurement.statusbar.removeWidget(self.progress_bar)
                self.progress_bar.hide()

    def save_spectra(self):
        """ Save the create denergy spectra.
        """
        QtWidgets.QMessageBox.critical(self, "Error", "Not implemented",
                                       QtWidgets.QMessageBox.Ok, QtWidgets.QMessageBox.Ok)


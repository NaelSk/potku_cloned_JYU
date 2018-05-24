# coding=utf-8
"""
Created on 15.3.2013
Updated on 24.5.2018

Potku is a graphical user interface for analyzation and 
visualization of measurement data collected from a ToF-ERD 
telescope. For physics calculations Potku uses external 
analyzation components.  
Copyright (C) Jarkko Aalto, Timo Konu, Samuli Kärkkäinen, Samuli Rahkonen and 
Miika Raunio

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
__author__ = "Jarkko Aalto \n Timo Konu \n Samuli Kärkkäinen \n Samuli Rahkonen \n Miika Raunio"
__versio__ = "1.0"

from os.path import join
from PyQt5 import QtCore, QtGui, uic, QtWidgets

from dialogs.element_selection import ElementSelectionDialog
from modules.element import Element
import modules.masses as masses


class SelectionSettingsDialog(QtWidgets.QDialog):
    """Selection Settings dialog handles showing settings for selection made in 
    measurement (in matplotlib graph).
    """
    def __init__(self, selection):
        """Inits selection settings dialog.
        
        Args:
            selection: Selection class object.
        """
        super().__init__()
        self.selection = selection
        self.measurement = selection.measurement
        self.element_colormap = self.selection.element_colormap
        self.ui = uic.loadUi(join("ui_files", "ui_selection_settings.ui"), self)
        self.__set_isotope_weight_factor()
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        # Setup connections
        self.ui.sampleType.currentIndexChanged.connect(self.__change_type)
        self.ui.sample_element_button.clicked.connect(self.__change_sample_element)
        self.ui.sample_isotope_radio.toggled.connect(self.__toggle_isotope_sample)
        self.ui.sample_isotope_combobox.currentIndexChanged.connect(
            lambda: self.__set_isotope_weight_factor(self.ui.sample_isotope_combobox))
        self.ui.rbs_element_button.clicked.connect(self.__change_rbs_element)
        self.ui.rbs_isotope_radio.toggled.connect(self.__toggle_isotope_rbs)
        self.ui.rbs_isotope_combobox.currentIndexChanged.connect(
            lambda: self.__set_isotope_weight_factor(self.ui.rbs_isotope_combobox))
        self.ui.colorButton.clicked.connect(self.__click_color_button)
        self.ui.OKButton.clicked.connect(self.__accept_settings) 
        self.ui.cancelButton.clicked.connect(self.close)
        
        # Set current values to UI and show
        self.__set_values_to_dialog()
        # Whether we accept or cancel selection, then remove selection if cancel.
        self.isOk = False
        self.exec_()
    

    def __set_values_to_dialog(self):
        """Set parent's values into the dialog.
        """
        element = self.selection.element
        isotope = self.selection.element.isotope
        if self.selection.type == "ERD":

            self.ui.groupBox_sample.setEnabled(True)
            self.ui.sample_element_button.setText(element.symbol)

            if element.isotope:
                self.ui.sample_isotope_radio.setChecked(True)
                self.ui.sample_isotope_combobox.setEnabled(True)

            self.__enable_element_fields(element.symbol,
                                         self.ui.sample_isotope_combobox,
                                         self.ui.sample_isotope_radio,
                                         self.ui.sample_standard_mass_radio,
                                         self.ui.sample_standard_mass_label,
                                         current_isotope=element.isotope)
        elif self.selection.type == "RBS":

            self.ui.groupBox_rbs.setEnabled(True)
            self.ui.rbs_element_button.setText(element.symbol)

            if element.isotope:
                self.ui.rbs_isotope_radio.setChecked(True)
                self.ui.rbs_isotope_combobox.setEnabled(True)

            self.__enable_element_fields(element.symbol,
                                         self.ui.rbs_isotope_combobox,
                                         self.ui.rbs_isotope_radio,
                                         self.ui.rbs_standard_mass_radio,
                                         self.ui.rbs_standard_mass_label,
                                         sample=False,
                                         current_isotope=element.isotope)
        else:
            raise ValueError("Invalid values")

        # Set proper type (ERD / RBS) of the element
        for i in range(self.ui.sampleType.count()):
            if self.ui.sampleType.itemText(i) == self.selection.type:
                self.ui.sampleType.setCurrentIndex(i)

        self.ui.sampleWeightFactor.setValue(self.selection.weight_factor)

        # Selection Element
        if element:
            self.ui.sample_element_button.setText(element.symbol)
            self.ui.colorButton.setText("Automatic [{0}]".format(element.symbol))

        selection_isotope = None
        if isotope:
            self.ui.sample_isotope_radio.setChecked(True)
            self.ui.sample_isotope_combobox.setEnabled(True)
            selection_isotope = isotope
        self.__enable_element_fields(element.symbol,
                                     self.ui.sample_isotope_combobox,
                                     self.ui.sample_isotope_radio,
                                     self.ui.sample_standard_mass_radio,
                                     self.ui.sample_standard_mass_label,
                                     current_isotope=selection_isotope)

        # self.color = QtGui.QColor(self.selection.default_color)
        # Check if selection color is same as default color for "automatic" text.
        # self.__change_color_button_color(element.symbol)

        # RBS Element
        if self.selection.type == "RBS":
            rbs_isotope = None
            self.ui.groupBox_rbs.setEnabled(True)
            self.ui.rbs_element_button.setText(Element.__str__(
                self.selection.element_scatter))
            if self.selection.element_scatter.isotope:
                self.ui.rbs_isotope_radio.setChecked(True)
                self.ui.rbs_isotope_combobox.setEnabled(True)
                rbs_isotope = self.selection.element_scatter.isotope
            self.__enable_element_fields(Element.__str__(
                self.selection.element_scatter),
                                         self.ui.rbs_isotope_combobox,
                                         self.ui.rbs_isotope_radio,
                                         self.ui.rbs_standard_mass_radio,
                                         self.ui.rbs_standard_mass_label,
                                         sample=False,
                                         current_isotope=rbs_isotope)

        self.__check_if_settings_ok()
        
    
    def __change_sample_element(self):
        """Shows dialog to change selection element.
        """
        self.__change_element(self.ui.sample_element_button,
                              self.ui.sample_isotope_combobox,
                              self.ui.sample_standard_mass_label,
                              self.ui.sample_standard_mass_radio,
                              self.ui.sample_isotope_radio)
        self.__check_if_settings_ok()
        
                  
    def __change_rbs_element(self):
        """Shows dialog to change selection element.
        """
        self.__change_element(self.ui.rbs_element_button,
                              self.ui.rbs_isotope_combobox,
                              self.ui.rbs_standard_mass_label,
                              self.ui.rbs_standard_mass_radio,
                              self.ui.rbs_isotope_radio,
                              sample=False)
        self.__check_if_settings_ok()

            
    def __change_element(self, button, isotope_combobox, standard_mass_label,
                         standard_mass_radio, isotope_radio,
                         sample=True):
        """Shows dialog to change selection element.
        
        Args:
            button: QtWidgets.QPushButton (button to select element)
            isotope_combobox: QtWidgets.QComboBox
            isotope_radio: QtGui.QRadioButton
            standard_mass_radio: QtGui.QRadioButton
            standard_mass_label: QtWidgets.QLabel
        """
        dialog = ElementSelectionDialog()
        # Only disable these once, not if you cancel after selecting once.
        if button.text() == "Select": 
            isotope_radio.setEnabled(False)
            standard_mass_radio.setEnabled(False)
            standard_mass_label.setEnabled(False)
        # If element was selected, proceed to enable appropriate fields.
        if dialog.element:
            button.setText(dialog.element)
            self.__enable_element_fields(dialog.element, isotope_combobox,
                                         isotope_radio, standard_mass_radio,
                                         standard_mass_label, sample)
    
    
    def __enable_element_fields(self, element, isotope_combobox,
                                isotope_radio, standard_mass_radio,
                                standard_mass_label, sample=True,
                                current_isotope=None):
        """Enable element information fields.
        
        Args:
            element: String representing element.
            isotope_combobox: QtWidgets.QComboBox
            isotope_radio: QtGui.QRadioButton
            standard_mass_radio: QtGui.QRadioButton
            standard_mass_label: QtWidgets.QLabel
            sample: Boolean representing if element is sample (and not RBS element).
        """
        if element:
            isotope_radio.setEnabled(True)
            standard_mass_radio.setEnabled(True)
            standard_mass_label.setEnabled(True)
            self.__load_isotopes(isotope_combobox,
                                 standard_mass_label,
                                 element,
                                 current_isotope)
            self.__set_color_button_color(element)
        
    
    def __set_color_button_color(self, element):
        """Set default color of element to color button.
        
        Args:
            element: String representing element.
        """
        self.ui.groupBox_coloring.setEnabled(True)
        if element and element != "Select":
            self.color = QtGui.QColor(self.element_colormap[element])
            if self.selection.is_closed:
                self.color = QtGui.QColor(self.selection.default_color)
            self.__change_color_button_color(element)
        
    
    def __set_isotope_weight_factor(self, isotope_combobox=None):
        """Set a specific isotope's weight factor to label.
        
        Args:
            isotope_combobox: A QtWidgets.QComboBox element of isotopes.
        """
        if not isotope_combobox or not isotope_combobox.isEnabled():
            self.ui.isotope_specific_weight_factor_label.setText("")
        else:
            isotope_index = isotope_combobox.currentIndex()
            unused_isotope, propability = isotope_combobox.itemData(isotope_index)
            isotope_weightfactor = 100.0 / float(propability)
            text = "%.3f for specific isotope" % isotope_weightfactor
            self.ui.isotope_specific_weight_factor_label.setText(text)
        
        
    def __click_color_button(self):
        """Shows dialog to change selection color.
        """
        dialog = QtWidgets.QColorDialog(self)
        self.color = dialog.getColor(QtGui.QColor(self.color))
        if self.color.isValid():
            self.__change_color_button_color(self.ui.sample_element_button.text())
    
    
    def __change_color_button_color(self, element):
        """Change color button's color.
        
        Args:
            element: String representing element name.
        """
        if not self.ui.colorButton.text():
            return  # TODO: If color is manually chosen, do not reset?
        text_color = "black"
        luminance = 0.2126 * self.color.red() + 0.7152 * self.color.green()
        luminance += 0.0722 * self.color.blue()
        if luminance < 50:
            text_color = "white"
        style = "background-color: {0}; color: {1};".format(self.color.name(),
                                                            text_color)
        self.ui.colorButton.setStyleSheet(style)

        if self.color.name() == self.element_colormap[element]:
            self.ui.colorButton.setText("Automatic [{0}]".format(element))
        else:
            self.ui.colorButton.setText("")
        
    
    def __load_isotopes(self, combobox, standard_mass_label,
                        element, current_isotope=None):
        """Change isotope information regarding element
        
        Args:
            combobox: QtWidgets.QComboBox where element's isotopes are loaded to.
            standard_mass_label: QtWidgets.QLabel where element's standard mass is shown.
            element: String representing element.
            current_isotope: String representing current isotope.
        """
        standard_mass = masses.get_standard_isotope(element)
        standard_mass_label.setText(str(round(standard_mass, 3)))
        masses.load_isotopes(element, combobox, current_isotope)

        
    def __change_type(self):
        """Toggle ERD/RBS type change.
        """
        if self.ui.sampleType.currentText() == "RBS":
            self.__change_type_to_rbs()
        elif self.ui.sampleType.currentText() == "ERD":
            self.__change_type_to_erd()
    
    
    def __change_type_to_rbs(self):
        """Change sample settings to RBS mode.
        """
        self.ui.groupBox_rbs.setEnabled(True)
        self.ui.groupBox_sample.setEnabled(False)
        # Put current sample settings to RBS
        self.ui.rbs_isotope_combobox.clear()
        self.ui.rbs_element_button.setText(self.ui.sample_element_button.text())
        self.ui.rbs_isotope_radio.setChecked(
                                   self.ui.sample_isotope_radio.isChecked())
        self.ui.rbs_isotope_combobox.setEnabled(
                                   self.ui.sample_isotope_radio.isChecked())
        self.ui.rbs_standard_mass_radio.setChecked(
                                   self.ui.sample_standard_mass_radio.isChecked())
        current_isotope = None
        if self.ui.sample_element_button.text() != "Select":
            if self.ui.sample_isotope_radio.isChecked():
                mass_index = self.ui.sample_isotope_combobox.currentIndex()
                isotope_data = self.ui.sample_isotope_combobox.itemData(mass_index)
                current_isotope = isotope_data[0]
            self.__enable_element_fields(self.ui.sample_element_button.text(),
                                         self.ui.rbs_isotope_combobox,
                                         self.ui.rbs_isotope_radio,
                                         self.ui.rbs_standard_mass_radio,
                                         self.ui.rbs_standard_mass_label,
                                         sample=False,
                                         current_isotope=current_isotope)
        
        # Put measurement settings element information to sample settings.
        #measurement_settings = self.settings.get_measurement_settings()
        #elem_symbol = measurement_settings.measuring_unit_settings.element.symbol
        #elem_isotope = str(measurement_settings.measuring_unit_settings.element.isotope)
        # standard_mass = str(masses.get_standard_isotope(
        #                                                           elem_symbol))
        # self.ui.sample_element_button.setText(elem_symbol)
        self.ui.sample_standard_mass_radio.setEnabled(False)
        self.ui.sample_standard_mass_label.setEnabled(False)
        # self.ui.sample_standard_mass_label.setText(standard_mass)
        self.ui.sample_isotope_radio.setChecked(True)
        self.ui.sample_isotope_radio.setEnabled(False)
        self.ui.sample_isotope_combobox.setEnabled(False)
        # masses.load_isotopes(elem_symbol,
        #                                     self.ui.sample_isotope_combobox,
        #                                     elem_isotope)
        # self.__set_color_button_color(sample_element)
        self.__set_color_button_color(self.ui.rbs_element_button.text())
        if current_isotope:
            self.__set_isotope_weight_factor(self.ui.rbs_isotope_combobox)
    
    
    def __change_type_to_erd(self):
        """Change sample settings to ERD mode.
        """
        self.ui.groupBox_rbs.setEnabled(False)
        self.ui.groupBox_sample.setEnabled(True)
        
        # Put RBS information to sample settings.
        self.ui.sample_isotope_combobox.clear()
        self.ui.sample_element_button.setText(self.ui.rbs_element_button.text())
        self.ui.sample_isotope_radio.setChecked(
                                      self.ui.rbs_isotope_radio.isChecked())
        self.ui.sample_isotope_combobox.setEnabled(
                                      self.ui.rbs_isotope_radio.isChecked())
        self.ui.sample_standard_mass_radio.setChecked(
                                      self.ui.rbs_standard_mass_radio.isChecked())
        self.ui.sample_standard_mass_label.setText(
                                      self.ui.rbs_standard_mass_label.text())
        current_isotope = None
        if self.ui.rbs_element_button.text() != "Select":
            if self.ui.sample_isotope_radio.isChecked():
                mass_index = self.ui.rbs_isotope_combobox.currentIndex()
                isotope_data = self.ui.rbs_isotope_combobox.itemData(mass_index)
                current_isotope = isotope_data[0]
            self.__enable_element_fields(self.ui.rbs_element_button.text(),
                                         self.ui.sample_isotope_combobox,
                                         self.ui.sample_isotope_radio,
                                         self.ui.sample_standard_mass_radio,
                                         self.ui.sample_standard_mass_label,
                                         current_isotope=current_isotope)
        if self.ui.sample_element_button.text() == "Select":
            self.ui.sample_standard_mass_label.setEnabled(False)
            self.ui.sample_standard_mass_radio.setEnabled(False)
            self.ui.sample_isotope_radio.setEnabled(False)
            self.ui.colorButton.setStyleSheet("")  # Clear style
            self.ui.colorButton.setText("Automatic")
        # else:
            # self.__set_color_button_color(self.ui.sample_element_button.text())
        
        # Clear RBS area.
        self.ui.rbs_element_button.setText("Select")
        self.ui.rbs_standard_mass_label.setText("0")
        self.ui.rbs_isotope_combobox.clear()
        # Switch to this by default.
        self.ui.rbs_standard_mass_radio.setChecked(True)
        if current_isotope:
            self.__set_isotope_weight_factor(self.ui.sample_isotope_combobox)
    
    
    def __toggle_isotope_sample(self):
        """Toggle Sample isotope radio button.
        """
        self.__change_to_specific_isotope(self.ui.sample_isotope_radio,
                                          self.ui.sample_isotope_combobox)
    
    
    def __toggle_isotope_rbs(self):
        """Toggle RBS isotope radio button.
        """
        self.__change_to_specific_isotope(self.ui.rbs_isotope_radio,
                                          self.ui.rbs_isotope_combobox)
    
    
    def __change_to_specific_isotope(self, radio, combobox):
        """Toggle combobox visibility depending on if radio button is checked.
        
        Args:
            radio: A QtGui.QRadioButton element.
            combobox: A QtWidgets.QComboBox element.
        """
        combobox.setEnabled(radio.isChecked())
        # self.__set_isotope_weight_factor()
        if radio.isChecked():
            self.__set_isotope_weight_factor(combobox)
        else:
            self.__set_isotope_weight_factor()
        
 
    def __check_if_settings_ok(self):
        """Check if sample settings are ok, and enable ok button.
        """
        type = self.ui.sampleType.currentText()
        rbs_element = self.ui.rbs_element_button.text()
        sample_element = self.ui.sample_element_button.text()
        if type == "RBS" and rbs_element != "Select" and rbs_element \
            and rbs_element:
            self.ui.OKButton.setEnabled(True)
        elif type == "ERD" and sample_element != "Select" and sample_element:
            self.ui.OKButton.setEnabled(True)
        else:
            self.ui.OKButton.setEnabled(False)
 
 
    def __accept_settings(self):
        """Accept settings given in the selection dialog and save these to parent. 
        """
        self.selection.type = self.ui.sampleType.currentText()

        # For standard isotopes:
        isotope = None
        rbs_isotope = None

        symbol = self.ui.sample_element_button.text()

        if self.selection.type == "ERD":
            if self.ui.sample_isotope_radio.isChecked():
                isotope_index = self.ui.sample_isotope_combobox.currentIndex()
                isotope_data = self.ui.sample_isotope_combobox.itemData(isotope_index)
                isotope = int(isotope_data[0])
                self.selection.element_scatter = Element("")

        else:
            rbs_element = self.ui.rbs_element_button.text()
            if self.ui.rbs_isotope_radio.isChecked():
                isotope_index = self.ui.rbs_isotope_combobox.currentIndex()
                isotope_data = self.ui.rbs_isotope_combobox.itemData(isotope_index)
                rbs_isotope = int(isotope_data[0])
                self.selection.element_scatter = Element(rbs_element,
                                                         rbs_isotope)

        self.selection.element = Element(symbol, isotope)
        self.selection.type = self.ui.sampleType.currentText()
        self.selection.weight_factor = self.ui.sampleWeightFactor.value()

        self.selection.default_color = self.color.name()
        self.selection.reset_color()
        self.isOk = True
        self.close()

# coding=utf-8
"""
Created on 2.2.2020
Updated on 5.2.2020

Potku is a graphical user interface for analyzation and
visualization of measurement data collected from a ToF-ERD
telescope. For physics calculations Potku uses external
analyzation components.
Copyright (C) 2020 TODO

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

__author__ = "Juhani Sundell"
__version__ = ""  # TODO

import unittest
import tempfile
import os

from tests.utils import change_wd_to_root
from modules.recoil_element import RecoilElement
from modules.element import Element


class TestErdFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # default recoil element
        cls.elem_4he = RecoilElement(Element.from_string("4He"),
                                     [], "red")

        # Valid file names for the recoil element
        cls.valid_erd_files = [
            "4He-Default.101.erd",
            "4He-Default.102.erd"
        ]

        # Invalid file names for the recoil element
        cls.invalid_erd_files = [
            "4He-Default.101",
            ".4He-Default.102.erd",
            ".4He-Default..erd",
            "4He-Default.101.erf",
            "4He-Default./.103.erd",
            "4He-Default.\\.104.erd",
            "3He-Default.102.erd"
        ]

        cls.expected_values = [
            (f, s + 101)
            for s, f in enumerate(cls.valid_erd_files)
        ]

    @change_wd_to_root
    def test_get_seed(self):
        import modules.element_simulation as es
        # get_seed looks for an integer in the second part of the string
        # split by dots
        self.assertEqual(102, es.get_seed("O.102.erd"))
        self.assertEqual(0, es.get_seed("..3.2.1.0."))
        self.assertEqual(-1, es.get_seed("..-1.2"))

        # File paths are also valid arguments
        self.assertEqual(101, es.get_seed("/tmp/.101.erd"))
        self.assertEqual(101, es.get_seed("\\tmp\\.101.erd"))

        # get_seed makes no attempt to check if the entire string
        # is a valid file name or path to an erd file
        self.assertEqual(101, es.get_seed(".101./erd"))
        self.assertEqual(101, es.get_seed(".101.\\erd"))

        # Having less split parts before or after returns None
        self.assertIsNone(es.get_seed("111."))
        self.assertIsNone(es.get_seed("0-111."))
        self.assertIsNone(es.get_seed(".111.."))

        # So does having no splits at all
        self.assertIsNone(es.get_seed("100"))

    @change_wd_to_root
    def test_get_valid_erd_files(self):
        import modules.element_simulation as es

        self.assertEqual([], list(es.validate_erd_file_names(
            self.invalid_erd_files, self.elem_4he)))

        res = list(es.validate_erd_file_names(self.valid_erd_files,
                                              self.elem_4he))

        self.assertEqual(self.expected_values, res)

        # Combining invalid files with valid files does not change the
        # result
        new_files = self.invalid_erd_files + self.valid_erd_files

        res = list(es.validate_erd_file_names(new_files,
                                              self.elem_4he))

        self.assertEqual(self.expected_values, res)

    @change_wd_to_root
    def test_erdfilehandler_init(self):
        from modules.element_simulation import ERDFileHandler
        handler = ERDFileHandler(self.valid_erd_files, self.elem_4he)

        exp = [(f, s, False) for f, s in self.expected_values]
        self.assertEqual(exp, [f for f in handler])
        self.assertEqual(0, handler.get_active_atom_counts())
        self.assertEqual(0, handler.get_old_atom_counts())

    @change_wd_to_root
    def test_max_seed(self):
        from modules.element_simulation import ERDFileHandler
        handler = ERDFileHandler([], self.elem_4he)

        self.assertEqual(None, handler.get_max_seed())

        handler.add_active_file(self.valid_erd_files[0])
        self.assertEqual(101, handler.get_max_seed())

        handler.add_active_file(self.valid_erd_files[1])
        self.assertEqual(102, handler.get_max_seed())


    @change_wd_to_root
    def test_erdfilehandler_add(self):
        from modules.element_simulation import ERDFileHandler
        handler = ERDFileHandler(self.valid_erd_files, self.elem_4he)

        # already existing files, or files belonging to another
        # recoil element cannot be added
        self.assertRaises(ValueError,
                          lambda: handler.add_active_file(
                              self.valid_erd_files[0]))
        self.assertRaises(ValueError,
                          lambda: handler.add_active_file("4He-New.101.erd"))

        # new file can be added, but only once
        new_file = "4He-Default.103.erd"
        handler.add_active_file(new_file)

        self.assertRaises(ValueError, lambda: handler.add_active_file(new_file))

        # new file appears as the first element when iterating
        # over the handler and its status is active
        exp = [(new_file, 103, True)] + [(f, s, False)
                                         for f, s, in self.expected_values]

        self.assertEqual(exp, [f for f in handler])

    @change_wd_to_root
    def test_atom_counts(self):
        """Tests atom counting by writing lines to temporary files"""
        from modules.element_simulation import ERDFileHandler

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Create files in the tmp dir
            for file in self.valid_erd_files:
                self.write_line(os.path.join(tmp_dir, file))

            # Initialise a handler from the tmp_dir and add an active file
            handler = ERDFileHandler.from_directory(tmp_dir, self.elem_4he)
            handler.add_active_file(os.path.join(tmp_dir,
                                                 "4He-Default.103.erd"))

            # Append a line to each file
            for erd_file, _, _ in handler:
                self.write_line(erd_file)

            self.assertEqual(1, handler.get_active_atom_counts())
            self.assertEqual(4, handler.get_old_atom_counts())

            # As the results of old files are cached, only counts in active
            # files are incremented
            for erd_file, _, _ in handler:
                self.write_line(erd_file)

            self.assertEqual(2, handler.get_active_atom_counts())
            self.assertEqual(4, handler.get_old_atom_counts())

            # If the handler is updated, active file is moved to old files
            handler.update()
            self.assertEqual(0, handler.get_active_atom_counts())
            self.assertEqual(6, handler.get_old_atom_counts())

            # Now the atom count will no longer update in the added file
            for erd_file, _, _ in handler:
                self.write_line(erd_file)

            self.assertEqual(0, handler.get_active_atom_counts())
            self.assertEqual(6, handler.get_old_atom_counts())

        # Assert that tmp dir got deleted
        self.assertFalse(os.path.exists(tmp_dir))

    def write_line(self, file):
        with open(file, "a") as file:
            # ERDFileHandler is only counting lines,
            # it does not care if the file contains
            # nonsensical data.
            file.write("foo\n")



### SPDX-License-Identifier: GPL-2.0-or-later

"""Test cases for rsk_mt.model.Model"""

from unittest import TestCase

from rsk_mt.model import Model

class TestModel(TestCase):
    """Tests for rsk_mt.model.Model."""
    def test_abstract(self):
        """Test rsk_mt.model.Model is abstract:"""
        self.assertRaises(NotImplementedError, Model, {}, 'must-understand')

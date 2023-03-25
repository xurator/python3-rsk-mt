### SPDX-License-Identifier: GPL-2.0-or-later

"""Common procedures for JSON Schema object test cases"""

class Procedures(): # pylint: disable=no-member
    """Mixin of common procedures for JSON Schema object test cases."""
    def proc_setitem(self, dct, key, val, after):
        """Test set `key` to `val` in `dct`, resulting value `after`."""
        dct[key] = val
        self.assertEqual(dct[key], val)
        self.assertEqual(dct.get(key), val)
        self.assertEqual(dct, after)
    def proc_delitem(self, dct, key, after):
        """Test del `key` from `dct`, resulting value `after`."""
        del dct[key]
        # test using dct.get() not dct[key], which may return a default value
        self.assertEqual(dct.get(key), None)
        self.assertEqual(dct, after)
    def proc_clear(self, dct, after):
        """Test clear `dct`, resulting value `after`."""
        dct.clear()
        self.assertEqual(dct, after)
    def proc_pop(self, dct, key, val, after):
        """Test pop `key` from `dct` returns `val`, resulting value `after`."""
        popped = dct.pop(key)
        self.assertEqual(popped, val)
        self.assertEqual(dct, after)
    def proc_popitem_no_pairs(self, dct):
        """Test popitem on `dct`, ensure no pairs are popped."""
        ini = dict(dct)
        popped = {}
        while True:
            try:
                (key, val) = dct.popitem()
            except KeyError:
                break
            else:
                popped[key] = val
        self.assertEqual(popped, {})
        self.assertEqual(dct, ini)
    def proc_popitem_all_pairs(self, dct):
        """Test popitem on `dct`, ensure all pairs are popped."""
        ini = dict(dct)
        popped = {}
        while True:
            try:
                (key, val) = dct.popitem()
            except KeyError:
                break
            else:
                popped[key] = val
        self.assertEqual(popped, ini)
        self.assertEqual(dct, {})
    def proc_update(self, dct, other, after):
        """Test update `dct` with `other`, resulting value `after`."""
        before = dict(dct)
        self.assertEqual(dct.update({}), None)
        self.assertEqual(before, dct)
        self.assertEqual(dct.update(other), None)
        self.assertEqual(dct, after)

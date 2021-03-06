"""This module tests functions in the Tag class.

    Packages(s) required:
    - pytest

"""

# Imports
import pytest

import sys, os
sys.path.append(os.path.realpath('html'))
import atom


class TestTag:
    """Test the Tag class."""

    def setup_method(self, method):
        """Setup each test."""
        pass

    def test_empty_constructor(self):
        t = atom.Tag()
        assert t.name == None
        assert t.attributes == None
        assert t.data == None
        assert t.parent == None
        assert t.children == None
        assert t.string_concat_list == []

    def test_full_constructor(self):
        n = "Name"
        a = [('name', 'val'), ('name2', 'val2')]
        d = "Data"
        p = atom.Tag()
        c = [atom.Tag(), atom.Tag()]
        t = atom.Tag(name=n, attributes=a, data=d, parent=p, children=c)
        assert t.name == n
        assert t.attributes == a
        assert t.data == d
        assert t.parent == p
        assert t.children == c
        assert t.string_concat_list == []


"""This module provides an HTML tag class."""

# Imports


class Tag(object):
    """Describes an HTML tag.

    Attributes:
        name: The name/type of a tag. e.g., 'table'.
        attributes: A list of attribute tuples.
        data: The content of the Tag.
        parent: The parent of the Tag.
        children: A list of Tag children objects.
        string_concat_list: A list used for string concatenations.

    """
    # Public member variables
    name = None
    attributes = None
    data = None
    parent = None
    children = None
    string_concat_list = None # List used for string concatenations

    def __init__(self, name=None, attributes=None, data=None, parent=None,
                 children=None):
        """Create and initialize a Tag.

        Args:
            name: The name/type of a tag. e.g., 'table'.
            attributes: A list of attribute tuples.
            data: The content of the Tag.
            parent: The parent of the Tag.
            children: A list of Tag children objects.

        """
        self.name = name
        self.attributes = attributes
        self.data = data
        self.parent = parent
        self.children = children
        self.string_concat_list = []


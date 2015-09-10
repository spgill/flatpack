import xml.etree.ElementTree as ET
import sys
import io

import tkinter
import tkinter.ttk
import tkinter.font

import bottle
import yaml

import flatpack_pieces
import namespace

import storage
storage.init()

# import storage

# Main method. Takes XML file and packs widgets into given master.


def unpack(widget_master, olive_path, local_vars={}):
    """Source must be a string-like object or a file-like object"""
    # Pass the xml through the bottle templating engine first
    tree_src = bottle.SimpleTemplate(
        source=storage.resources[olive_path]).render(local_vars)
    tree_src = io.StringIO(tree_src)

    # Parse the file into an ElementTree unless an ElementTree is passed
    tree = ET.parse(tree_src)

    # Get the root Element
    tree_root = tree.getroot()

    # Create a namespace inside the master for storing the widget references
    # widget_master.flatpack = namespace.Namespace()
    widget_registry = namespace.Namespace()

    # Start the recursion process (and the night-sweats)
    for child in tree_root:
        _unpack_recurse(widget_registry, widget_master, widget_master, child)

    return widget_registry

_widgets = {
    'button': tkinter.ttk.Button,
    'label': tkinter.ttk.Label,
    'progressbar': tkinter.ttk.Progressbar,
}

_pieces = {}
for attr in dir(flatpack_pieces):
    if attr.startswith('piece_'):
        name = attr[6:]
        _pieces[name] = getattr(flatpack_pieces, attr)

_managers = [
    'pack',
    'grid',
    'row',
    'cell',
]


def _unpack_recurse(widget_registry, master, parent, element, level=0):
    # print(('    ' * level), element.tag)

    # If tag is a piece, then construct the widget
    if element.tag in _pieces:
        widget_constructor = _pieces[element.tag]
        widget_kwargs = element.attrib

        # Take olive image paths and run them through the storage resources jar
        if 'image' in widget_kwargs:
            widget_kwargs['image'] = storage.resources[widget_kwargs['image']]

        # Take font options in yaml format and turn them into Font objects
        if 'font' in widget_kwargs:
            widget_kwargs['font'] = tkinter.font.Font(
                **yaml.load(widget_kwargs['font']))

        # Pop the id attribute
        widget_id = widget_kwargs.pop('id', None)

        # Construct the widget
        widget = widget_constructor(
            widget_registry, parent, element, widget_kwargs)

        # If a widget id was given in the attributes, cache the widget in the
        # master's flatpack namespace
        if widget_id:
            # setattr(master.flatpack, widget_id, widget)
            setattr(widget_registry, widget_id, widget)

    # If not a widget, make this element "transparent" to tcl
    else:
        widget = parent

    # Process the children (this is where recursion comes in)
    children = []
    for child in element:
        children.append(
            _unpack_recurse(widget_registry, master, widget, child, level + 1))

    # If a widget, return
    if element.tag in _pieces:
        return widget

    if element.tag in _managers:
        manager = element.tag

        if manager == 'pack':
            for child in children:
                child.pack(**element.attrib)

        if manager == 'cell':
            return (element.attrib, children[0] if children else None)

        if manager == 'row':
            return (element.attrib, children)

        if manager == 'grid':
            column_max = 0

            for i, row in enumerate(children):
                for j, cell in enumerate(row[1]):
                    if cell[1] is None:
                        continue
                    if j > column_max:
                        column_max = j
                    kwargs = {'row': i, 'column': j}
                    kwargs.update(element.attrib)
                    kwargs.update(row[0])
                    kwargs.update(cell[0])
                    cell[1].grid(**kwargs)

            for i in range(len(children)):
                parent.grid_rowconfigure(i, weight=1)

            for i in range(column_max + 1):
                parent.grid_columnconfigure(i, weight=1)

    else:
        raise KeyError('"{0}" is not a valid element tag'.format(element.tag))

if __name__ == '__main__':
    unpack(None, sys.argv[1])._root.mainloop()

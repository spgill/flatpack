import tkinter
import tkinter.ttk

import yaml

import flatpack
import scrolled
import storage


def piece_tk(registry, parent, element, kwargs):
    title = kwargs.pop('title', 'tk')
    icon = kwargs.pop('iconphoto', None)
    resize = kwargs.pop('resizable', None)

    root = tkinter.Tk(**kwargs)
    root.update()
    registry['_root'] = root

    root.title(title)

    if icon:
        root.iconphoto(True, storage.resources[icon])

    if resize:
        root.resizable(*yaml.load(resize))

    return root


def piece_toplevel(registry, parent, element, kwargs):
    title = kwargs.pop('title', 'tk')
    icon = kwargs.pop('iconphoto', None)
    transient = kwargs.pop('transient', None)
    resize = kwargs.pop('resizable', None)

    root = tkinter.Toplevel(parent, **kwargs)
    root.update()

    root.title(title)

    if icon:
        root.iconphoto(True, storage.resources[icon])

    if transient:
        root.transient(registry[transient])

    if resize:
        root.resizable(*yaml.load(resize))

    return root


def piece_flatpack(registry, parent, element, kwargs):
    source = kwargs.pop('src')
    frame = tkinter.ttk.Frame(parent, **kwargs)
    flatpack.unpack(frame, source)


def piece_label(registry, parent, element, kwargs):
    kwargs['text'] = element.text
    return tkinter.ttk.Label(parent, **kwargs)


def piece_frame(registry, parent, element, kwargs):
    return tkinter.ttk.Frame(parent, **kwargs)


def piece_labelframe(registry, parent, element, kwargs):
    kwargs['text'] = element.text.strip()
    print('"' + element.text.strip() + '"')
    return tkinter.ttk.LabelFrame(parent, **kwargs)


def piece_button(registry, parent, element, kwargs):
    kwargs['text'] = element.text
    return tkinter.ttk.Button(parent, **kwargs)


def piece_progressbar(registry, parent, element, kwargs):
    return tkinter.ttk.Progressbar(parent, **kwargs)


def piece_scrolled_treeview(registry, parent, element, kwargs):
    return scrolled.Treeview(parent, **kwargs)

def piece_separator(registry, parent, element, kwargs):
    return tkinter.ttk.Separator(parent, **kwargs)

def piece_optionmenu(registry, parent, element, kwargs):
    return tkinter.ttk.OptionMenu(parent, tkinter.StringVar(), **kwargs)

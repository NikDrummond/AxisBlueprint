"""Application entry points for launching the layout designer."""

import tkinter as tk

from .designer import LayoutDesigner


def BlueprintBuilder():
    root = tk.Tk()
    LayoutDesigner(root)
    root.mainloop()


def main():
    BlueprintBuilder()

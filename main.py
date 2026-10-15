# -*- coding: utf-8 -*-
"""Entry point."""
import os
import sys
import tkinter as tk

# Allow running this file directly: add parent dir to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from aisecuritytest.app import AISecurityTestApp


def main():
    root = tk.Tk()
    AISecurityTestApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
import tkinter as tk

from barbell_gui import BarbellGUI


def main():
    root = tk.Tk()
    app = BarbellGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

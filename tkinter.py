import tkinter as tk

class MainWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("My Window")
        self.root.geometry("400x300")

if __name__ == "__main__":
    root = tk.Tk()
    main_window = MainWindow(root)
    root.mainloop()

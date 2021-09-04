if __name__ == '__main__':
    from App import App
    from utils import *
    from tkinter import ttk
    app = App()
    app.protocol("WM_DELETE_WINDOW", delete_video_thumbnail())
    # app.tk.call("source", ".\\ttk-Breeze-master\\breeze.tcl")
    # app.configure(style=ttk.Style().theme_use("Breeze"))
    app.mainloop()


if __name__ == '__main__':
    from App import App
    from utilitis import *
    from tkinter import ttk
    app = App()
    app.protocol("WM_DELETE_WINDOW", delete_video_thumbnail())
    # app.configure(style=ttk.Style().theme_use('clam'))
    app.mainloop()


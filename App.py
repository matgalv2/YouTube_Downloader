import sys
import tkinter.filedialog
from tkinter import ttk
from tkinter import *
from tkinter.ttk import Combobox

from utilitis import *

video: YouTube = None


askForResolution = "Select a resolution"
askForBitrate = "Select a bitrate"


class App(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.title("YouTube Downloader")

        self.geometry('800x450')
        self.resizable(height=False, width=False)
        self.__container = ttk.Frame(self)
        self.__frames = {}
        self.__container.pack(expand=True)

        self.__container.pack(side='top', fill='both', expand=True)
        self.__container.grid_rowconfigure(0, weight=1)
        self.__container.grid_columnconfigure(0, weight=1)

        self.add_pages(SearchPage)
        self.__frames[SearchPage].tkraise()

    def add_pages(self, *args):
        for arg in args:
            frame = arg(self.__container, self)
            frame.grid(row=0, column=0, sticky='nsew')
            self.__frames[arg] = frame

    def show_page(self, page):
        self.__frames[page].tkraise()

    @property
    def frames(self):
        return self.__frames


class SearchPage(ttk.Frame):
    def __init__(self, master, controller: App):
        ttk.Frame.__init__(self, master)
        controller.geometry('300x300')

        ttk.Label(self, text="Enter a link below:").place(x=20, y=30)

        text = ttk.Entry(self, width=36, font="Calibri 11")
        text.place(x=20, y=50, height=20)

        ttk.Button(self, text="Search", command=lambda: search_command(text.get())).place(x=200, y=200)

        nIc_Label = ttk.Label(self)
        sdne_Label = ttk.Label(self)
        vyl_Label = ttk.Label(self)


        def search_command(link):
            if not network_connection_is_valid():
                nIc_Label.place(x=84, y=120)
                nIc_Label.configure(text="No Internet connection.")
                # controller.after(5000, lambda: nIc_Label.configure(text=""))
                controller.after(3000, lambda: nIc_Label.place_forget())

            elif not site_exists(text.get()):
                sdne_Label.place(x=94, y=120)
                sdne_Label.configure(text="Site does not exist.")
                # controller.after(5000, lambda: sdne_Label.configure(text=""))
                controller.after(3000, lambda: sdne_Label.place_forget())

            elif not is_youtube_link(text.get()):
                vyl_Label.place(x=60, y=120)
                vyl_Label.configure(text="Please enter a valid youtube link.")
                controller.after(3000, lambda: vyl_Label.place_forget())
            else:
                global video
                video = YouTube(link)
                prepare_video(video)
                controller.add_pages(DetailsPage)
                controller.show_page(DetailsPage)
                controller.geometry("400x300")


class DetailsPage(ttk.Frame):
    img = None

    def __init__(self, master, controller: App):
        ttk.Frame.__init__(self, master)

        image = loadImage(path + "\\" + image_name)
        DetailsPage.img = image
        videoImg = ttk.Label(self, image=image)
        videoImg.place(x=20, y=20)

        sharedVariable = IntVar()
        sharedVariable.set(0)

        radioButton1 = ttk.Radiobutton(self, text="Audio & video", variable=sharedVariable, value=1, command=lambda: radioButton1_3())
        radioButton2 = ttk.Radiobutton(self, text="Only audio", variable=sharedVariable, value=2, command=lambda: radioButton2())
        radioButton3 = ttk.Radiobutton(self, text="Only video", variable=sharedVariable, value=3, command=lambda: radioButton1_3())

        radioButton1.place(x=210, y=40)
        radioButton2.place(x=210, y=60)
        radioButton3.place(x=210, y=80)

        quality = ttk.Combobox(self, state="readonly")
        quality.place(x=210, y=120)

        downloadButton = ttk.Button(self, text="Download", command=lambda: download_video())
        downloadButton.place(x=30, y=250)

        backButton = ttk.Button(self, text="Back", command=lambda: back())
        backButton.place(x=300, y=250)

        warningLabel = ttk.Label(self, text="Please select a quality.")
        nIc_Label = ttk.Label(self, text="No Internet connection.")
        errorLabel = ttk.Label(self, text="Something failed, check your Internet connection.")

        # errorLabel.place(x=75, y=210)
        # warningLabel.place(x=140, y=210)
        # nIc_Label.place(x=130, y=210)


        def download_video():

            chosenOption = sharedVariable.get()

            # check if both needed things are selected
            if chosenOption == 0:
                warningLabel.configure(text="Please select a type and a quality.")
                warningLabel.place(x=110, y=210)
                controller.after(3000, lambda: warningLabel.place_forget())
                return

            elif quality.get() == askForBitrate or quality.get() == askForResolution:
                warningLabel.configure(text="Please select a quality.")
                warningLabel.place(x=140, y=210)
                controller.after(3000, lambda: warningLabel.place_forget())
                return

            elif not network_connection_is_valid():
                nIc_Label.place(x=130, y=210)
                controller.after(3000, lambda: nIc_Label.place_forget())
                return

            else:
                # TODO:
                #   1. Wybranie miejsca dla pliku. ✓
                #   2. Pobranie odpowieniego streamu.
                #   3. Sprawdzić, czy video.title pobiera tytuł z Internetu. ✓

                # getting right extension
                if chosenOption in {1,3}:
                    extension = "mp4"
                    extensionName = "MP4 Video File"
                else:
                    extension = "mp3"
                    extensionName = "MPEG Audio"

                # attempt of getting video title
                videoTitle = get_video_title(video)
                if videoTitle is None:
                    errorLabel.place(x=75, y=210)
                    controller.after(4000, lambda: errorLabel.place_forget())
                    return

                # picking a folder
                filePath = tkinter.filedialog.asksaveasfilename(initialfile=normalise_filename(video.title), filetype=[(extensionName, "*."+extension), ("Wszystkie pliki", "*.*")] , defaultextension=extension)

                # download
                if chosenOption == 1:
                    # dash or progressive
                    if int(str(quality.get()).replace('p', '')) <= 720:
                        # progressive
                        video.streams.filter(resolution=quality.get(), is_dash=False).first().download(filename=filePath)
                    else:
                        # dash
                        video.streams.filter(abr=quality.get(), only_audio=True).first().download(filename=filePath)

                        video.streams.filter(resolution=quality.get(), only_video=True).first().download(filename=filePath)

                        # i tu merguje audio i video

                        # video_stream = ffmpeg.input('Of Monsters and Men - Wild Roses.mp4')
                        # audio_stream = ffmpeg.input('Of Monsters and Men - Wild Roses_audio.mp4')
                        # ffmpeg.output(audio_stream, video_stream, 'out.mp4').run()
                        pass

                elif chosenOption == 2:
                    video.streams.filter(abr=quality.get(), only_audio=True).first().download(filename=filePath)

                else:
                    video.streams.filter(resolution=quality.get(), only_video=True).first().download(filename=filePath)

        def radioButton1_3():
            quality.configure(values=sort_quality(get_dash_resolutions(video)))
            quality.set(askForResolution)

        def radioButton2():
            quality.configure(values=sort_quality(get_audio_bit_rates(video)))
            quality.set(askForBitrate)

        def back():
            global video
            video = None
            delete_video_thumbnail()
            controller.geometry("300x300")
            controller.show_page(SearchPage)
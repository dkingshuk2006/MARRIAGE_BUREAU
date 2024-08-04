# loading_screen.py
from customtkinter import *
import os
from PIL import Image


def open_signup_page():
    # Start the signup page process
    os.system('python signup.py')


def close_loading_and_open_signup():
    loading_window.destroy()  # Close the loading window
    open_signup_page()  # Open the signup page


def show_loading_screen():
    global loading_window
    loading_window = CTk()
    loading_window.title("Loading")
    loading_window.geometry('600x600+400+60')
    loading_window.iconbitmap("icon.ico")
    loading_window.resizable(0,0)

    # Add a heading label with styling
    heading_label = CTkLabel(
        loading_window,
        text="Welcome to the Marriage Bureau",
        font=("Arial", 24, "bold"),
        text_color="#4A4A4A"
    )
    heading_label.pack(pady=(20, 10))

    subtitle_label = CTkLabel(
        loading_window,
        text="Connecting Hearts and Souls",
        font=("Arial", 14),
        text_color="#6A6A6A",
    )
    subtitle_label.pack(pady=(0, 20))

    bg_image = Image.open('logo.png')
    bg_image = CTkImage(dark_image=bg_image, size=(350, 373))
    image_label = CTkLabel(loading_window, image=bg_image, text="")
    image_label.pack(padx=20)
    CTkLabel(loading_window, text="Loading, please wait...", font=("Arial", 16)).pack(pady=20)

    progress_bar = CTkProgressBar(loading_window, mode="indeterminate")
    progress_bar.pack(pady=20, padx=20)
    progress_bar.start()

    # Schedule the close_loading_and_open_signup function to run after 10 seconds
    loading_window.after(10000, close_loading_and_open_signup)

    loading_window.mainloop()


# Show the loading screen
show_loading_screen()

from customtkinter import *
from PIL import Image, ImageTk
import pymysql
import sys
import shutil
import smtplib
import threading
import email_password
from tkinter import messagebox
import os


def fade_in(widget, steps=20, interval=50):
    def increment_opacity(current_step):
        if current_step <= steps:
            opacity = int((current_step / steps) * 255)
            widget.configure(fg_color=f'#{opacity:02x}{opacity:02x}{opacity:02x}')
            widget.after(interval, increment_opacity, current_step + 1)

    increment_opacity(0)


def slide_in(widget, start_x, end_x, steps=20, interval=50):
    delta_x = (end_x - start_x) / steps

    def increment_position(current_step):
        if current_step <= steps:
            widget.place(x=start_x + current_step * delta_x, y=widget.winfo_y())
            widget.after(interval, increment_position, current_step + 1)
        else:
            widget.place(x=end_x, y=widget.winfo_y())  # Ensure the widget is at the final position

    increment_position(0)


def fetch_data(gender, search_query=''):
    try:
        connection = pymysql.connect(
            host='localhost',
            user='root',
            password='1234',
            database='marriage_bureau'
        )
        cursor = connection.cursor()

        # Determine opposite gender
        opposite_gender = 'Female' if gender == 'Male' else 'Male'

        # Query to search profiles
        query = """
                       SELECT * FROM users
                       WHERE gender = %s AND (city LIKE %s OR occupation LIKE %s OR religion LIKE %s OR marital_status LIKE %s)
                       """
        search_pattern = f"%{search_query}%"
        cursor.execute(query, (opposite_gender, search_pattern, search_pattern, search_pattern, search_pattern))
        results = cursor.fetchall()

        return results

    except pymysql.MySQLError as e:
        print(f'Error: {e}')
        return []

    finally:
        connection.close()


def send_interest_email(to_email, sender_email):
    t = threading.Thread(target=lambda: send_email(to_email, sender_email))
    t.setDaemon = True
    t.start()


def send_email(to_email, sender_email):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        email_ = email_password.my_email
        password_ = email_password.my_password
        server.login(email_, password_)
        subj = 'Interest Notification- Marriage Bureau'
        msg = f"Hello,\n\nYou have received an interest from {sender_email}.\n\nBest Regards,\nMarriage Bureau"
        msg = f'Subject:{subj}\n\n{msg}'
        server.sendmail(email_, to_email, msg)
        check = server.ehlo()
        if check[0] == 250:
            messagebox.showinfo('Success', f"Interest email sent to {to_email}")
        else:
            messagebox.showerror('Error', 'Connection error, try again')
    except Exception as e:
        messagebox.showerror('Error', f'Error due to {e}')


def create_card(container_frame, user_data, row, col):
    # Create a frame for the card
    card_frame = CTkFrame(container_frame, corner_radius=15, fg_color='white', width=320, height=450)
    card_frame.grid(row=row, column=col, padx=10, pady=10)
    card_frame.grid_propagate(False)  # Prevent the frame from resizing

    # Display user photo if available
    photo_path = user_data[14]  # Adjust index based on your table schema
    if photo_path and os.path.isfile(photo_path):
        photo_image = Image.open(photo_path)
        photo_image_tk=CTkImage(dark_image=photo_image, size=(80, 80))
        photo_label = CTkLabel(card_frame, image=photo_image_tk, text='')
        photo_label.grid(row=0, column=0, rowspan=8, padx=10, pady=10)
        photo_label.image = photo_image_tk  # Keep reference to avoid garbage collection

    # Display user information
    info_labels = [
        f"Name: {user_data[1]}",
        f"Phone: {user_data[4]}",
        f"Age: {user_data[6]}",
        f"City: {user_data[7]}",
        f"Annual Income: {user_data[8]}",
        f"Occupation: {user_data[9]}",
        f"Education: {user_data[10]}",
        f"Religion: {user_data[11]}",
        f"Caste: {user_data[12]}",
        f"Marital Status: {user_data[13]}",
    ]

    for i, text in enumerate(info_labels):
        label = CTkLabel(card_frame, text=text)
        label.grid(row=i, column=1, sticky='w', padx=10, pady=5)

    # Add "Interest" button
    interest_button = CTkButton(card_frame, text="Show Interest", border_color='#BFA250', hover_color='#66216E',
                                width=30, corner_radius=20, fg_color='#66316E',
                                command=lambda: send_interest_email(user_data[2], sender_email))
    interest_button.grid(row=len(info_labels) + 1, column=1, columnspan=2, pady=10, sticky='w')

    # Apply fade-in animation
    fade_in(card_frame)


def on_mouse_wheel(event, canvas):
    canvas.yview_scroll(-1 * int(event.delta / 120), "units")


def logout(root):
    root.destroy()
    os.system('python login.py')


def search_profiles(container, master_frame, search_entry):
    search_query = search_entry.get()
    data = fetch_data(gender, search_query)
    # Clear existing data
    container.destroy()
    # Create a new container frame
    container = CTkFrame(master_frame, corner_radius=15, fg_color='#66316E')
    container.grid(row=1, column=0, pady=20, sticky='nsew')
    # Add new data
    row, col = 0, 0
    for user_data in data:
        create_card(container, user_data, row, col)
        col += 1
        if col > 2:  # Move to the next row after 3 columns
            col = 0
            row += 1


def show_all(container, master_frame):
    data = fetch_data(gender)
    # Clear existing data
    container.destroy()
    # Create a new container frame
    container = CTkFrame(master_frame, corner_radius=15, fg_color='#66316E')
    container.grid(row=1, column=0, pady=20, sticky='nsew')

    # Add new data
    row, col = 0, 0
    for user_data in data:
        create_card(container, user_data, row, col)
        col += 1
        if col > 2:  # Move to the next row after 3 columns
            col = 0
            row += 1


def create_data_window(gender):
    root = CTk()
    opposite_gender = 'Female' if gender == 'Male' else 'Male'
    root.title(f'{opposite_gender} Profiles')
    root.geometry('1040x680+100+10')
    root.configure(fg_color='#66316E')

    # Create a canvas and scrollbar to hold the frames
    canvas = CTkCanvas(root, bg='#66316E')
    canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)

    scrollbar = CTkScrollbar(root, orientation=VERTICAL, command=canvas.yview)
    scrollbar.pack(side=RIGHT, fill=Y)

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

    canvas.bind_all("<MouseWheel>", lambda event: on_mouse_wheel(event, canvas))

    # Create a master frame to hold header and container
    master_frame = CTkFrame(canvas, corner_radius=0, fg_color='#66316E')
    canvas.create_window((0, 0), window=master_frame, anchor='nw')

    # Header frame
    header_frame = CTkFrame(master_frame, corner_radius=15, fg_color='#66316E')
    header_frame.grid(row=0, column=0, columnspan=3, pady=10, sticky='ew')

    # Add heading
    heading_label = CTkLabel(header_frame, text='Discover Your Perfect Match!', font=('Arial', 22, 'bold'),
                             text_color='white')
    heading_label.grid(row=0, column=0, pady=10, sticky='w', padx=20)

    # Add search bar
    search_frame = CTkFrame(header_frame, corner_radius=15, fg_color='#66316E')
    search_frame.grid(row=0, column=1, padx=20, sticky='e')

    search_entry = CTkEntry(search_frame, placeholder_text="Search Profiles", width=220, corner_radius=20)
    search_entry.grid(row=0, column=0, padx=10)

    search_button = CTkButton(search_frame, text="Search", corner_radius=20, width=100,
                              fg_color='#4D89F9', hover_color='#3D6ABF', border_color='#4A6CF9',
                              command=lambda: search_profiles(container, master_frame, search_entry))
    search_button.grid(row=0, column=1, padx=10)

    show_button = CTkButton(search_frame, text="Show All", corner_radius=20, width=100,
                            fg_color='#28A745', hover_color='#218838', border_color='#1E7D32',
                            command=lambda: show_all(container, master_frame))
    show_button.grid(row=0, column=2, padx=10)

    # Add logout button
    logout_button = CTkButton(header_frame, text="Logout", corner_radius=20, fg_color='#C82333', border_color='#BD2130',
                              hover_color='#A71D2A', width=80, command=lambda: logout(root))
    logout_button.grid(row=0, column=2, padx=(50, 10), sticky='e')

    # Create a frame to hold all cards
    container = CTkFrame(master_frame, corner_radius=15, fg_color='#66316E')
    container.grid(row=1, column=0, pady=10, sticky='nsew')

    # Fetch and display data
    data = fetch_data(gender)
    row, col = 0, 0
    for user_data in data:
        create_card(container, user_data, row, col)
        col += 1
        if col > 2:  # Move to the next row after 3 columns
            col = 0
            row += 1

    root.mainloop()


if __name__ == "__main__":
    gender = sys.argv[1]  # Get gender from command-line arguments
    sender_email = sys.argv[2]
    create_data_window(gender)

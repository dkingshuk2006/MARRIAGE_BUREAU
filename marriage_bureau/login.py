from customtkinter import *
from PIL import Image
import os
from tkinter import messagebox
import pymysql, threading
import smtplib, email_password
import time


# Functionality Part

def signup_window():
    root.destroy()
    os.system('python signup.py')


def login():
    global connection, cursor
    if username_entry.get() == '' or password_entry.get() == '':
        messagebox.showerror('Error', 'All fields are required')
    else:
        try:
            connection = pymysql.connect(host='localhost', user='root', password='1234', )
            cursor = connection.cursor()
        except:
            messagebox.showerror('Title', 'Incorrect MySQL credentials or MySQL client not open.')
            return
        cursor.execute("USE marriage_bureau")
        # Query to check if the username and password match
        query = """
                SELECT * FROM users
                WHERE (email = %s OR full_name = %s) AND password = %s
                """
        cursor.execute(query, (username_entry.get(), username_entry.get(), password_entry.get()))

        # Fetch one record
        result = cursor.fetchone()

        if result:
            email = result[2]
            gender = result[5]
            # Credentials match
            messagebox.showinfo('Success', 'Login is successful')
            if remember_me_var.get() == 'yes':
                with open('credentials.txt', 'w') as f:
                    f.write(f'{username_entry.get()}\n{password_entry.get()}')
            else:
                # Delete credentials file if "Remember Me" is not checked
                if os.path.exists('credentials.txt'):
                    os.remove('credentials.txt')
            root.destroy()
            os.system(f'python main.py {gender} {email}')
        else:
            # Credentials do not match
            messagebox.showerror('Error', 'Username or Password is Incorrect')


def load_credentials():
    try:
        with open('credentials.txt', 'r') as f:
            lines = f.readlines()
            if len(lines) == 2:
                username_entry.insert(0, lines[0].strip())
                password_entry.insert(0, lines[1].strip())
                remember_me_var.set('yes')
    except FileNotFoundError:
        pass


def email_thread(to_, name):
    t = threading.Thread(target=lambda: send_email(to_, name))
    t.setDaemon = True
    t.start()


def send_email(to_, name):
    global otp
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()
    email_ = email_password.my_email
    password_ = email_password.my_password
    s.login(email_, password_)
    otp = int(time.strftime('%H%M%S')) + int(time.strftime('%S'))
    subj = 'Marriage Bureau- One Time Password'
    msg = f'Dear {name},\n\nYour OTP is {otp}.\n\nWith Regards,\nMarriage Bureau Team'
    msg = f'Subject:{subj}\n\n{msg}'
    s.sendmail(email_, to_, msg)
    check = s.ehlo()
    if check[0] == 250:
        return 'success'
    else:
        return 'fail'


def forget_password():
    global cursor, connection

    def verify():
        if otpEntry.get() == str(otp):
            submitButton.configure(state=NORMAL)
            verifyButton.configure(state=DISABLED)
            messagebox.showinfo('Success', 'Verification is successful', parent=forget_window)

        else:
            messagebox.showerror('Error', 'Invalid OTP, try again', parent=forget_window)

    def submit():
        if newpassEntry.get() == '' or confirmEntry.get() == '':
            messagebox.showerror('Error', 'All fields are required', parent=forget_window)
        elif newpassEntry.get() != confirmEntry.get():
            messagebox.showerror('Error', 'Password mismatch', parent=forget_window)
        else:

            cursor.execute('UPDATE users SET password=%s WHERE email=%s', (newpassEntry.get(), username_entry.get()))
            connection.commit()
            messagebox.showinfo('Success', 'Password is changed', parent=forget_window)
            forget_window.destroy()

    if username_entry.get() == '':
        messagebox.showerror('Error', 'Please enter your email address')
    else:
        connection = pymysql.connect(host='localhost', user='root', password='1234')
        cursor = connection.cursor()
        cursor.execute("USE marriage_bureau")
        cursor.execute('SELECT full_name, email FROM users WHERE email=%s',
                       (username_entry.get()))
        user_data = cursor.fetchone()
        if user_data is None:
            messagebox.showerror('Error', 'Invalid email address, try again')
        else:
            name,email = user_data
            check = email_thread(email, name)
            if check == 'fail':
                messagebox.showerror('Error', 'Connection error, try again')
            else:

                forget_window = CTkToplevel()
                forget_window.grab_set()
                forget_window.title('Change Password')
                # forget_window.config(bg='white')
                forget_image = Image.open('forget.png')
                # Convert the image to a CTkImage
                forget_image = CTkImage(dark_image=forget_image, size=(128, 128))
                forgetLogoLabel = CTkLabel(forget_window, image=forget_image, text='')
                forgetLogoLabel.grid(row=0, column=0, pady=(10, 20))
                otpLabel = CTkLabel(forget_window, text='Check your Email for the OTP',
                                    )
                otpLabel.grid(row=1, column=0, padx=50)
                otpEntry = CTkEntry(forget_window)
                otpEntry.grid(row=2, column=0, padx=50, pady=(5, 0))

                verifyButton = CTkButton(forget_window, text='Verify', command=verify)
                verifyButton.grid(row=3, column=0, pady=(20, 30), padx=50)

                newpassLabel = CTkLabel(forget_window, text='New Password', )
                newpassLabel.grid(row=4, column=0, padx=50)
                newpassEntry = CTkEntry(forget_window, show='*')
                newpassEntry.grid(row=5, column=0, padx=50, pady=(5, 10))

                confirmLabel = CTkLabel(forget_window, text='Confirm Password', )
                confirmLabel.grid(row=6, column=0, padx=50)
                confirmEntry = CTkEntry(forget_window, show='*')
                confirmEntry.grid(row=7, column=0, padx=50, pady=(5, 0))

                submitButton = CTkButton(forget_window, text='Submit', command=submit, state=DISABLED)
                submitButton.grid(row=8, column=0, pady=(20, 30), padx=50)

                forget_window.mainloop()

def toggle_password():
    if password_entry.cget('show') == '*':
        password_entry.configure(show='')
        toggle_button.configure(image=open_eye)
    else:
        password_entry.configure(show='*')
        toggle_button.configure(image=close_eye)

# GUI Part
root = CTk()
root.title('Login- Marriage Bureau')
root.geometry('650x650+400+30')
root.iconbitmap("icon.ico")
root.resizable(0,0)

bgImage = Image.open('login.png')

# Convert the image to a CTkImage
bgImage = CTkImage(dark_image=bgImage, size=(650, 650))

image_label = CTkLabel(root, image=bgImage, text="")
image_label.pack()

welcome_label = CTkLabel(root, text="Welcome Back", font=("Arial", 30), bg_color='#66316E', text_color='white')
welcome_label.place(x=365, y=100)

username_entry = CTkEntry(root, width=200, placeholder_text='Username or Email Address:', border_width=2,
                          bg_color='#66316E', border_color='#BFA250')
username_entry.place(x=365, y=180)

password_entry = CTkEntry(root, show="*", width=200, placeholder_text='Password:', border_width=2, bg_color='#66316E',
                          border_color='#BFA250')  # show="*" masks the input
password_entry.place(x=365, y=230)

open_eye = Image.open('open_eye.png')
open_eye = CTkImage(dark_image=open_eye, size=(24, 24))

close_eye = Image.open('close_eye.png')
close_eye = CTkImage(dark_image=close_eye, size=(24, 24))


toggle_button = CTkButton(root, image=close_eye, command=toggle_password,text='',width=8,fg_color='#66316E',bg_color='#66316E',hover_color='#66316E')
toggle_button.place(x=570, y=230)

remember_me_var = StringVar()
remember_me_checkbox = CTkCheckBox(root, text="Remember Me", text_color='white', variable=remember_me_var,
                                   onvalue="yes", offvalue="no", border_width=2, bg_color='#66316E',
                                   border_color='#BFA250')
remember_me_checkbox.place(x=365, y=270)

load_credentials()

# Create and place the login button
login_button = CTkButton(root, text="Login", fg_color='#66316E', border_width=2, bg_color='#66316E',
                         border_color='#BFA250', hover_color='#66216E',
                         command=login)
login_button.place(x=365, y=330)

# Create and place the forgot password and sign-up links
forgot_password_button = CTkButton(root, text="Forgot Password?", fg_color='#66316E', cursor="hand2",
                                   bg_color='#66316E', text_color='white', border_width=0, hover_color='#66216E',
                                   command=forget_password)
forgot_password_button.place(x=365, y=365)

not_member_label = CTkLabel(root, text="Not a Member?", bg_color='#66316E', text_color='white')
not_member_label.place(x=365, y=400)

signup_button = CTkButton(root, text="Signup", fg_color='#66316E', cursor="hand2",
                          bg_color='#66316E', text_color='#BFA250', hover_color='#66316E', width=50,
                          command=signup_window)
signup_button.place(x=460, y=401)

root.mainloop()

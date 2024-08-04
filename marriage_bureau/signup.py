from customtkinter import *
from PIL import Image, ImageTk
import os
import pymysql
from tkinter import messagebox, filedialog
import shutil

# Functionality Part
file_path = None

def upload_photo():
    global file_path
    file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png")])
    print(file_path)
    if file_path:
        photo_image = Image.open(file_path)
        # Convert the PIL image to CTkImage
        photo_image_ctk = CTkImage(dark_image=photo_image, size=(120, 120))

        # Update the label with the new image
        photo_label.configure(image=photo_image_ctk, text='')
        photo_label.image = photo_image_ctk  # Keep a reference to avoid garbage collection

    else:
        file_path = None

def signup_window():
    root.destroy()
    os.system('python login.py')

def signup():
    global file_path
    # Retrieve data from the form fields
    full_name = full_name_entry.get()
    email = email_entry.get()
    password = password_entry.get()
    confirm_password = confirm_password_entry.get()
    phone = phone_entry.get()
    gender = gender_combobox.get()
    age = age_entry.get()
    city = city_entry.get()
    annual_income = annual_income_entry.get()
    occupation = occupation_combobox.get()
    education = education_combobox.get()
    religion = religion_combobox.get()
    caste = caste_combobox.get()
    marital_status = marital_status_combobox.get()

    if (not full_name or
            not email or
            not password or
            not confirm_password or
            not phone or
            gender == 'Select Gender*' or
            not city or
            not annual_income or
            not age or
            education == 'Select Education Level' or
            occupation == 'Select Occupation*' or
            religion == 'Select Religion*' or
            caste == 'Select Caste*' or
            marital_status == 'Select Marital Status*'):

        messagebox.showerror("Error", "Please fill in all required fields")
        return

    elif password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match")
        return
    elif int(age) < 18:
        messagebox.showerror("Error", "Sorry, you must be at least 18 years old to create a profile.")
        return

    elif file_path is None:
        messagebox.showerror("Error", "Please upload your profile picture")
        return

    # Move uploaded photo to the 'uploaded_images' directory
    try:
        # Ensure directory exists
        if not os.path.exists('uploaded_images'):
            os.makedirs('uploaded_images')

        # Define new file path
        new_file_path = os.path.join('uploaded_images', os.path.basename(file_path))
        shutil.copy(file_path, new_file_path)

        # Database connection
        try:
            connection = pymysql.connect(host='localhost', user='root', password='1234')
            cursor = connection.cursor()

            # Create database
            cursor.execute("CREATE DATABASE IF NOT EXISTS marriage_bureau")
            cursor.execute("USE marriage_bureau")

            # Create table
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS users (
                                id INT AUTO_INCREMENT PRIMARY KEY,
                                full_name VARCHAR(100),
                                email VARCHAR(100) UNIQUE,
                                password VARCHAR(255),
                                phone VARCHAR(20),
                                gender VARCHAR(10),
                                age VARCHAR(20),
                                city VARCHAR(100),
                                annual_income VARCHAR(30),
                                occupation VARCHAR(50),
                                education VARCHAR(50),
                                religion VARCHAR(50),
                                caste VARCHAR(50),
                                marital_status VARCHAR(20),
                                photo VARCHAR(100)
                            )
                            """)

            # Check if email already exists
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                messagebox.showerror("Error", "Email address already exists")
                return

            query = """
            INSERT INTO users (full_name, email, password, phone, gender, age, city, annual_income, occupation, education, religion, caste, marital_status, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(query, (
                full_name, email, password, phone, gender, age, city, annual_income, occupation, education, religion,
                caste, marital_status, new_file_path))
            connection.commit()
            messagebox.showinfo("Success", "Signup successful!")
            root.destroy()
            os.system('python login.py')
        except pymysql.MySQLError as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        finally:
            connection.close()
    except Exception as e:
        messagebox.showerror("Error", f"Error moving file: {e}")

# GUI Part
root = CTk()
root.title('Sign Up - Marriage Bureau')
root.geometry('850x680+250+10')
root.configure(fg_color='#66316E')
root.iconbitmap("icon.ico")
root.resizable(0,0)


# Load and set background image (optional)
bg_image = Image.open('signup.png')
bg_image = CTkImage(dark_image=bg_image, size=(850, 680))
image_label = CTkLabel(root, image=bg_image, text="")
image_label.pack(side=LEFT)

create_profile_label = CTkLabel(root, text="Create Your Perfect Match Profile", font=("Arial", 30), bg_color='#66316E',
                                text_color='white')
create_profile_label.place(x=340, y=40)

# Full Name entry (Column 1)
full_name_entry = CTkEntry(root, width=200, placeholder_text='Full Name*', border_width=2, bg_color='#66316E',
                           corner_radius=20, border_color='#BFA250')
full_name_entry.place(x=340, y=100)

# Email Address entry (Column 2)
email_entry = CTkEntry(root, width=200, placeholder_text='Email Address*', border_width=2, bg_color='#66316E',
                       corner_radius=20, border_color='#BFA250')
email_entry.place(x=600, y=100)

# Password entry (Column 1)
password_entry = CTkEntry(root, show="*", width=200, placeholder_text='Password*', border_width=2, bg_color='#66316E',
                          corner_radius=20, border_color='#BFA250')
password_entry.place(x=340, y=150)

# Confirm Password entry (Column 2)
confirm_password_entry = CTkEntry(root, show="*", width=200, placeholder_text='Confirm Password*', border_width=2,
                                  bg_color='#66316E', corner_radius=20, border_color='#BFA250')
confirm_password_entry.place(x=600, y=150)

# Phone Number entry (Column 1)
phone_entry = CTkEntry(root, width=200, placeholder_text='Phone Number*', border_width=2, bg_color='#66316E',
                       corner_radius=20, border_color='#BFA250')
phone_entry.place(x=340, y=200)

# Gender combobox (Column 2)
gender_combobox = CTkOptionMenu(root, values=['Male', 'Female', 'Other'], fg_color='white', width=200, corner_radius=20,
                                button_color='white', text_color='black', button_hover_color='white')
gender_combobox.set('Select Gender*')
gender_combobox.place(x=600, y=200)

# Date of Birth entry (Column 1)
age_entry = CTkEntry(root, width=200, placeholder_text='Age*', border_width=2,
                     bg_color='#66316E',
                     border_color='#BFA250', corner_radius=20)
age_entry.place(x=340, y=250)

# city entry (Column 2)
city_entry = CTkEntry(root, width=200, placeholder_text='City*', border_width=2, bg_color='#66316E',
                      corner_radius=20, border_color='#BFA250')
city_entry.place(x=600, y=250)

# Annual Income entry
annual_income_entry = CTkEntry(root, width=200, placeholder_text='Annual Income*', border_width=2, bg_color='#66316E',
                               border_color='#BFA250', corner_radius=20)
annual_income_entry.place(x=340, y=300)

# Occupation combobox
occupation_combobox = CTkOptionMenu(root, values=['Engineer', 'Doctor', 'Teacher', 'Business', 'Student', 'Other'],
                                    fg_color='white', width=200, corner_radius=20, button_color='white',
                                    button_hover_color='white', text_color='black')
occupation_combobox.set('Select Occupation*')
occupation_combobox.place(x=600, y=300)

# Education combobox
education_combobox = CTkOptionMenu(root, values=[
    'High School',
    'Associate Degree',
    'Bachelor\'s Degree',
    'Master\'s Degree',
    'Doctorate',
    'Other'
], fg_color='white', width=200, corner_radius=20, button_color='white', text_color='black', button_hover_color='white')
education_combobox.set('Select Education Level*')
education_combobox.place(x=340, y=350)

# Religion combobox
religion_combobox = CTkOptionMenu(root, values=['Hindu', 'Muslim', 'Christian', 'Sikh', 'Buddhist', 'Jain', 'Other'],
                                  fg_color='white', width=200, corner_radius=20, button_color='white',
                                  text_color='black', button_hover_color='white')
religion_combobox.set('Select Religion*')
religion_combobox.place(x=600, y=350)

# Caste combobox
caste_combobox = CTkOptionMenu(root, values=['General', 'OBC', 'SC', 'ST', 'Other'], fg_color='white', width=200,
                               corner_radius=20, button_color='white', text_color='black', button_hover_color='white')
caste_combobox.set('Select Caste*')
caste_combobox.place(x=340, y=400)

# Marital Status combobox
marital_status_combobox = CTkOptionMenu(root, values=['Single', 'Divorced', 'Widowed'], fg_color='white', width=200,
                                        corner_radius=20, button_color='white', text_color='black',
                                        button_hover_color='white')
marital_status_combobox.set('Select Marital Status*')
marital_status_combobox.place(x=600, y=400)

# Photo upload button
upload_button = CTkButton(root, text="Upload Photo", fg_color='#66316E', border_width=2, bg_color='#66316E',
                          border_color='#BFA250', hover_color='#66216E', width=30, corner_radius=20,
                          command=upload_photo)
upload_button.place(x=380, y=460)

# Photo preview label
photo_label = CTkLabel(root, text="No photo selected", width=120, height=120, bg_color='#F0F0F0', )
photo_label.place(x=375, y=500)

# Signup button (Centered)
signup_button = CTkButton(root, text="Sign Up", fg_color='#66316E', border_width=2, bg_color='#66316E',
                          border_color='#BFA250', hover_color='#66216E', command=signup)
signup_button.place(x=550, y=530)

already_member_label = CTkLabel(root, text="Already a Member?", bg_color='#66316E', text_color='white')
already_member_label.place(x=540, y=580)

login_button = CTkButton(root, text="Login", fg_color='#66316E', cursor="hand2",
                         bg_color='#66316E', text_color='#BFA250', hover_color='#66316E', width=50,
                         command=signup_window)
login_button.place(x=655, y=580)

# Run the application
root.mainloop()

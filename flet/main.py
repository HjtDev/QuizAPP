import flet as ft
import os
import requests

theme_color = ft.Colors.BLUE_400
button_style = ft.ButtonStyle(
    bgcolor=theme_color,
    color=ft.Colors.WHITE,
    shape=ft.RoundedRectangleBorder(radius=8),
    elevation=5,
)

CREDENTIALS_FILE = "credentials.txt"
user_id = None
user_phone = None
user_password = None

def main(page: ft.Page):
    page.title = "Quiz Application"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

    if os.path.exists(CREDENTIALS_FILE):
        try:
            with open(CREDENTIALS_FILE, 'r') as f:
                phone, password = f.read().strip().split(',')
                if authenticate_user(page, phone, password):
                    global user_phone, user_password
                    user_phone = phone
                    user_password = password
                    show_main_menu(page)
                else:
                    show_login_form(page, phone, password)
        except ValueError:
            show_login_form(page)
    else:
        show_login_form(page)

def show_login_form(page: ft.Page, phone: str = "", password: str = "", error_message: str = ""):
    page.clean()

    title = ft.Text("Login", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    phone_field = ft.TextField(label="Phone", value=phone, autofocus=True)
    password_field = ft.TextField(label="Password", value=password, password=True)
    remember_me = ft.Checkbox(label="Remember Me")

    if error_message:
        error_text = ft.Text("Invalid credentials", color=ft.Colors.RED)
        page.add(error_text)

    def on_login_click(e):
        global user_phone, user_password
        phone_value = phone_field.value
        password_value = password_field.value
        if authenticate_user(page, phone_value, password_value):
            user_phone = phone_value
            user_password = password_value

            if remember_me.value:
                with open(CREDENTIALS_FILE, 'w') as f:
                    f.write(f"{phone_value},{password_value}")
            show_main_menu(page)

    login_button = ft.ElevatedButton("Login", on_click=on_login_click, style=button_style)

    page.add(title, phone_field, password_field, remember_me, login_button)

def authenticate_user(page: ft.Page, phone: str, password: str) -> bool:
    response = requests.post("http://localhost:8000/api/account/login/", json={"phone": phone, "password": password})

    if response.status_code == 200:
        player_data = response.json()
        global user_id
        user_id = player_data['id']
        print("Authentication successful:", player_data)
        return True
    else:
        print("Authentication failed")
        show_login_form(page, phone, password, "Invalid credentials")
        return False

def show_main_menu(page: ft.Page):
    page.clean()

    title = ft.Text("Welcome to the Quiz App", size=30, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE)

    start_quiz_button = ft.ElevatedButton("Start a Quiz", on_click=start_quiz, style=button_style, width=200)
    make_quiz_button = ft.ElevatedButton("Make a Quiz", on_click=make_quiz, style=button_style, width=200)
    account_button = ft.ElevatedButton("Account", on_click=account_settings, style=button_style, width=200)
    exit_button = ft.ElevatedButton("Exit", on_click=lambda e: page.window_destroy(), style=button_style, width=200)

    page.add(title,
             start_quiz_button,
             make_quiz_button,
             account_button,
             exit_button)

def start_quiz(e):
    print("Starting a quiz...")

def make_quiz(e):
    print("Making a quiz...")

def account_settings(e):
    print("Opening account settings...")

ft.app(target=main)

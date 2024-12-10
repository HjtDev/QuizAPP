import flet as ft

theme_color = ft.Colors.BLUE_400
button_style = ft.ButtonStyle(
    bgcolor=theme_color,
    color=ft.Colors.WHITE,
    shape=ft.RoundedRectangleBorder(radius=8),
    elevation=5,
)

def main(page: ft.Page):
    page.title = "Quiz Application"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.theme_mode = ft.ThemeMode.DARK

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

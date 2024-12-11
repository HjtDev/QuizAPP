import flet as ft
import os
import requests

theme_color = ft.Colors.BLUE_400
card_color = ft.Colors.GREY_800
text_color = ft.Colors.WHITE

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
user_name = None
user_display_name = None


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
    title = ft.Text("Login", size=30, weight=ft.FontWeight.BOLD, color=text_color)
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
        global user_id, user_name, user_display_name
        user_id = player_data['id']
        user_name = player_data['name']
        user_display_name = player_data['display_name']
        return True
    else:
        show_login_form(page, phone, password, "Invalid credentials")
        return False


def show_main_menu(page: ft.Page):
    page.clean()

    title = ft.Text("Welcome to the Quiz App", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    start_quiz_button = ft.ElevatedButton("Start a Quiz", on_click=lambda e: show_start_quiz_menu(page),
                                          style=button_style, width=200)
    make_quiz_button = ft.ElevatedButton("Make a Quiz", on_click=make_quiz, style=button_style, width=200)
    account_button = ft.ElevatedButton("Account", on_click=lambda e: show_account_info(page), style=button_style,
                                       width=200)
    exit_button = ft.ElevatedButton("Exit", on_click=lambda e: page.window_destroy(), style=button_style, width=200)

    page.add(title,
             start_quiz_button,
             make_quiz_button,
             account_button,
             exit_button)


def show_account_info(page: ft.Page):
    if user_id is not None and user_phone is not None and user_password is not None:
        response = requests.get(f"http://localhost:8000/api/account/profile/{user_id}/",
                                auth=(user_phone, user_password))

        if response.status_code == 200:
            player_data = response.json()
            display_account_info(page, player_data)
        else:
            page.add(ft.Text("Error retrieving account information.", color=ft.Colors.RED))
    else:
        page.add(ft.Text("User not authenticated.", color=ft.Colors.RED))


def display_account_info(page: ft.Page, player_data):
    page.clean()

    title = ft.Text("Account Information", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    league_name = player_data['league'].replace('_', ' ').title()

    info_list = [
        ("Phone:", player_data['phone']),
        ("Name:", player_data['name']),
        ("Display Name:", player_data['display_name']),
        ("Score:", str(player_data['score'])),
        ("League:", league_name)
    ]

    card_content = []

    for label, value in info_list:
        card_content.append(
            ft.Row([
                ft.Text(label, size=20, weight=ft.FontWeight.BOLD),
                ft.Text(value, size=20)
            ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)
        )

    info_card_container = ft.Container(
        content=ft.Column(card_content),
        bgcolor=card_color,
        border_radius=10,
        margin=10,
        padding=15,
        shadow=[ft.BoxShadow(blur_radius=10, color="rgba(0, 0, 0, 0.2)", offset=ft.Offset(0, 4))]
    )

    update_button = ft.ElevatedButton("Update Info", on_click=lambda e: show_update_info(page), style=button_style)

    back_to_menu_button = ft.ElevatedButton("Back to Main Menu", on_click=lambda e: show_main_menu(page),
                                            style=button_style)

    button_row = ft.Row([update_button, back_to_menu_button], alignment=ft.MainAxisAlignment.CENTER)

    page.add(title, info_card_container, button_row)


def show_update_info(page: ft.Page):
    page.clean()

    title = ft.Text("Update Information", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    phone_field = ft.TextField(label="Phone", value=user_phone)
    name_field = ft.TextField(label="Name", value=user_name)
    display_name_field = ft.TextField(label="Display Name", value=user_display_name)

    save_button = ft.ElevatedButton("Save", on_click=lambda e: update_user_info(phone_field.value, name_field.value,
                                                                                display_name_field.value, page),
                                    style=button_style)

    back_button = ft.ElevatedButton("Back to Account Info", on_click=lambda e: show_account_info(page),
                                    style=button_style)

    button_row = ft.Row([save_button, back_button], alignment=ft.MainAxisAlignment.CENTER)

    page.add(title, phone_field, name_field, display_name_field, button_row)


def update_user_info(updated_phone: str, updated_name: str, updated_display_name: str, page: ft.Page):
    global user_phone, user_name, user_display_name

    data_to_update = {
        "phone": updated_phone,
        "name": updated_name,
        "display_name": updated_display_name,
    }

    response = requests.patch(f"http://localhost:8000/api/account/profile/{user_id}/update/", json=data_to_update,
                              auth=(user_phone, user_password))

    if response.status_code == 200:
        user_phone = updated_phone
        user_name = updated_name
        user_display_name = updated_display_name

        show_account_info(page)

    else:
        error_message = response.json()
        error_display_text = ""

        if 'phone' in error_message:
            error_display_text += "\n".join(error_message['phone']) + "\n"

        if 'name' in error_message:
            error_display_text += "\n".join(error_message['name']) + "\n"

        if 'display_name' in error_message:
            error_display_text += "\n".join(error_message['display_name']) + "\n"

        page.add(ft.Text(error_display_text.strip(), color=ft.Colors.RED))


def show_start_quiz_menu(page: ft.Page):
    page.clean()

    title = ft.Text("Available Quizzes", size=30, weight=ft.FontWeight.BOLD, color=text_color)
    reload_button = ft.ElevatedButton("Reload", on_click=lambda e: load_quizzes(page), style=button_style)

    quiz_list_container = ft.Column()

    page.add(title, reload_button, quiz_list_container)

    load_quizzes(page)

    back_button = ft.ElevatedButton("Back to Main Menu", on_click=lambda e: show_main_menu(page), style=button_style)
    page.add(back_button)


def load_quizzes(page: ft.Page):
    try:
        response = requests.get("http://localhost:8000/api/quiz/", auth=(user_phone, user_password))
        response.raise_for_status()

        data = response.json()
        quizzes = data.get('results', [])

        page.controls[2].controls.clear()

        if quizzes:
            for quiz in quizzes:
                author_display_name = quiz['author']['display_name']
                quiz_info = f"{quiz['title']} by {author_display_name} | Score: {quiz['score']}"

                quiz_box = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(quiz['title'], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"By: {author_display_name}", size=16),
                            ft.Text(f"Score: {quiz['score']}", size=16),
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.ElevatedButton("Play", on_click=lambda e: None, style=button_style)
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=card_color,
                    border_radius=10,
                    margin=10,
                    padding=15,
                    shadow=[ft.BoxShadow(blur_radius=10, color="rgba(0, 0, 0, 0.2)", offset=ft.Offset(0, 4))]
                )

                page.controls[2].controls.append(quiz_box)

            page.update()
        else:
            page.controls[2].controls.append(ft.Text("No available quizzes.", size=20))
            page.update()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching quizzes: {e}")
        page.controls[2].controls.append(ft.Text("Failed to load quizzes.", color=ft.Colors.RED))
        page.update()


def make_quiz(e):
    print("Making a quiz...")


ft.app(target=main)

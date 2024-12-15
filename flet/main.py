import flet as ft
import os
import requests
from time import sleep

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
selected_answers = {}


def main(page: ft.Page):
    page.title = "Quiz Application"
    page.scroll = ft.ScrollMode.AUTO
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

    # Add Create Account Button
    create_account_button = ft.ElevatedButton("Create a New Account",
                                              on_click=lambda e: show_create_account_page(page),
                                              style=button_style)

    page.add(title, phone_field, password_field, remember_me,
             ft.Row([login_button, create_account_button], spacing=10, alignment=ft.MainAxisAlignment.CENTER))


def show_create_account_page(page: ft.Page):
    page.clean()
    title = ft.Text("Create Account", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    phone_field = ft.TextField(label="Phone", autofocus=True)
    name_field = ft.TextField(label="Name")
    display_name_field = ft.TextField(label="Display Name")
    password_field = ft.TextField(label="Password", password=True)
    confirm_password_field = ft.TextField(label="Confirm Password", password=True)

    error_text = ft.Text("", color=ft.Colors.RED)

    def on_register_click(e):
        data = {
            "phone": phone_field.value,
            "name": name_field.value,
            "display_name": display_name_field.value,
            "password": password_field.value,
        }

        # Check if passwords match
        if password_field.value != confirm_password_field.value:
            error_text.value = "Passwords do not match."
            page.add(error_text)
            return

        try:
            response = requests.post("http://localhost:8000/api/account/register/", json=data)
            print(response.json())
            if response.status_code == 201:
                # Successful registration
                success_message = ft.Text("Account created successfully! You can now log in.", color=ft.Colors.GREEN)
                page.add(success_message)
                # Redirect to login form after a short delay
                page.update()
                sleep(2)  # Wait for 2 seconds to show the message
                show_login_form(page)  # Redirect to login form
            else:
                # Handle errors
                error_message = response.json()
                error_text.value = ""
                for field, messages in error_message.items():
                    if field == 'non_field_errors':
                        error_text.value += "\n".join(messages) + "\n"
                    else:
                        error_text.value += f"{field.capitalize()}: " + "\n".join(messages) + "\n"

                page.add(error_text)

        except requests.exceptions.RequestException as e:
            print(f"Error during registration: {e}")
            error_text.value = "Failed to create account."
            page.add(error_text)

    register_button = ft.ElevatedButton("Register", on_click=on_register_click, style=button_style)
    back_button = ft.ElevatedButton("Back to Login", on_click=lambda e: show_login_form(page), style=button_style)

    page.add(title,
             phone_field,
             name_field,
             display_name_field,
             password_field,
             confirm_password_field,
             register_button,
             back_button)

    page.update()


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
    make_quiz_button = ft.ElevatedButton("Make a Quiz", on_click=lambda e: show_make_quiz_menu(page),
                                         style=button_style, width=200)
    account_button = ft.ElevatedButton("Account", on_click=lambda e: show_account_info(page), style=button_style,
                                       width=200)
    exit_button = ft.ElevatedButton("Exit", on_click=lambda e: page.window_destroy(), style=button_style, width=200)

    # Create a column to hold all items and center them
    menu_column = ft.Column(
        controls=[
            title,
            start_quiz_button,
            make_quiz_button,
            account_button,
            exit_button
        ],
        alignment=ft.MainAxisAlignment.CENTER,  # Center items vertically
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,  # Center items horizontally
        spacing=20,  # Add some spacing between items
        height=page.window.height
    )

    # Add the column to the page
    page.add(menu_column)
    page.update()


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


def show_quiz_details(page: ft.Page, quiz_id: int):
    page.clean()
    try:
        response = requests.get(f"http://localhost:8000/api/quiz/{quiz_id}", auth=(user_phone, user_password))
        response.raise_for_status()
        quiz_data = response.json()

        title = ft.Text(quiz_data['title'], size=30, weight=ft.FontWeight.BOLD, color=text_color)
        author_text = ft.Text(f"Author: {quiz_data['author']['display_name']}", size=20)
        description_text = ft.Text(f"Description: {quiz_data['description']}", size=16)
        available_time_text = ft.Text(f"Available Time: {quiz_data['available_time']}", size=16)
        score_text = ft.Text(f"Score: {quiz_data['score']}", size=16)
        created_at_date = quiz_data['created_at'].split("T")[0]
        created_at_text = ft.Text(f"Created At: {created_at_date}", size=16)

        back_button = ft.ElevatedButton("Back", on_click=lambda e: show_start_quiz_menu(page), style=button_style)

        # Implementing the Start button functionality
        start_button = ft.ElevatedButton("Start", on_click=lambda e: start_quiz(page, quiz_id), style=button_style)

        button_row = ft.Row([back_button, start_button], alignment=ft.MainAxisAlignment.CENTER)

        info_container = ft.Container(
            content=ft.Column(
                [title, author_text, description_text, available_time_text, score_text, created_at_text, button_row],
                alignment=ft.MainAxisAlignment.START
            ),
            bgcolor=card_color,
            border_radius=10,
            margin=10,
            padding=15,
            shadow=[ft.BoxShadow(blur_radius=10, color="rgba(0, 0, 0, 0.2)", offset=ft.Offset(0, 4))]
        )

        page.add(info_container)
        page.update()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching quiz details: {e}")
        page.add(ft.Text("Failed to load quiz details.", color=ft.Colors.RED))


def start_quiz(page: ft.Page, quiz_id: int):
    data = {
        "player_id": user_id,
        "quiz_id": quiz_id
    }

    try:
        response = requests.post("http://localhost:8000/api/quiz/start_quiz/", json=data,
                                 auth=(user_phone, user_password))

        if response.status_code == 200:
            # Navigate to the questions page
            show_quiz_questions(page, quiz_id)
        else:
            error_message = response.json().get('error', 'An unknown error occurred.')
            page.add(ft.Text(error_message, color=ft.Colors.RED))

    except requests.exceptions.RequestException as e:
        print(f"Error starting the quiz: {e}")
        page.add(ft.Text("Failed to start the quiz.", color=ft.Colors.RED))


def show_quiz_questions(page: ft.Page, quiz_id: int):
    global selected_answers  # Declare it as global to modify it

    page.clean()  # Clear current content

    try:
        # Fetch quiz questions from the API
        response = requests.get(f"http://localhost:8000/api/quiz/{quiz_id}/questions", auth=(user_phone, user_password))
        response.raise_for_status()
        questions_data = response.json()

        # Create a scrollable column for questions
        question_column = ft.Column(scroll=ft.ScrollMode.ALWAYS)  # Make this column scrollable

        selected_answers.clear()  # Clear previous answers

        for question in questions_data:
            question_text = ft.Text(question['question'], size=18, weight=ft.FontWeight.BOLD)

            # Create a RadioGroup for each question with its options in a Column
            radio_group = ft.RadioGroup(
                content=ft.Column([
                    ft.Radio(value='a', label=question['option_a']),
                    ft.Radio(value='b', label=question['option_b']),
                    ft.Radio(value='c', label=question['option_c']),
                    ft.Radio(value='d', label=question['option_d']),
                ]),
                on_change=lambda e, q_id=question['id']: selected_answers.update({q_id: e.control.value})
                # Update selection
            )

            # Create a container for the question and its options
            question_container = ft.Container(
                content=ft.Column([question_text, radio_group], scroll=ft.ScrollMode.AUTO),
                padding=10,
                bgcolor=card_color,
                border_radius=10,
                margin=10,
                shadow=[ft.BoxShadow(blur_radius=5, color="rgba(0, 0, 0, 0.2)", offset=ft.Offset(0, 2))]
            )

            question_column.controls.append(question_container)

        # Create a submit button that calls submit_quiz when clicked
        submit_button = ft.ElevatedButton("Submit", on_click=lambda e: submit_quiz(page, quiz_id), style=button_style)

        # Add everything to a container with fixed height to enable scrolling
        scrollable_container = ft.Container(
            content=ft.Column([question_column, submit_button], scroll=ft.ScrollMode.AUTO),
            height=page.height - 100  # Adjust height as needed
        )

        page.add(scrollable_container)
        page.update()

    except requests.exceptions.RequestException as e:
        print(f"Error fetching quiz questions: {e}")
        page.add(ft.Text("Failed to load quiz questions.", color=ft.Colors.RED))


def submit_quiz(page: ft.Page, quiz_id: int):
    global selected_answers  # Declare it as global to access it

    # Prepare data for submission
    data = {
        "player_id": user_id,
        "quiz_id": quiz_id,
        "answers": selected_answers  # This should be populated with the selected answers
    }

    try:
        # Send POST request to finish the quiz
        response = requests.post("http://localhost:8000/api/quiz/finish_quiz/", json=data,
                                 auth=(user_phone, user_password))

        if response.status_code == 200:
            result_data = response.json()
            score = result_data.get('score', 0)

            # Navigate to results page
            show_quiz_result(page, score)
        else:
            error_message = response.json().get('error', 'An unknown error occurred.')
            page.add(ft.Text(error_message, color=ft.Colors.RED))

    except requests.exceptions.RequestException as e:
        print(f"Error submitting quiz: {e}")
        page.add(ft.Text("Failed to submit quiz.", color=ft.Colors.RED))


def show_quiz_result(page: ft.Page, score: float):
    page.clean()  # Clear current content

    title = ft.Text("Quiz Result", size=30, weight=ft.FontWeight.BOLD, color=text_color)
    score_text = ft.Text(f"You scored: {score}XP", size=24, color=text_color)

    back_button = ft.ElevatedButton("Back to Quiz List", on_click=lambda e: show_start_quiz_menu(page),
                                    style=button_style)

    page.add(title, score_text, back_button)
    page.update()


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

                play_button = ft.ElevatedButton("Play",
                                                on_click=lambda e, quiz_id=quiz['id']: show_quiz_details(page, quiz_id),
                                                style=button_style)

                quiz_box = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(quiz['title'], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"By: {author_display_name}", size=16),
                            ft.Text(f"Score: {quiz['score']}", size=16),
                        ], alignment=ft.MainAxisAlignment.START),
                        play_button
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


def show_make_quiz_menu(page: ft.Page):
    page.clean()  # Clear current content

    title = ft.Text("My Quizzes", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    # Fetch quizzes for the player
    try:
        response = requests.get(f"http://localhost:8000/api/quiz/{user_id}/my_quizzes",
                                auth=(user_phone, user_password))
        response.raise_for_status()
        quizzes_data = response.json()

        quiz_list = ft.Column(scroll=ft.ScrollMode.ALWAYS)  # Make this column scrollable

        if quizzes_data:
            for quiz in quizzes_data:
                author_display_name = quiz['author']['display_name']
                verified_text = ft.Text("Verified", color=ft.Colors.GREEN) if quiz['verified'] else ft.Text(
                    "Not Verified", color=ft.Colors.RED)

                edit_button = ft.ElevatedButton("Edit",
                                                on_click=lambda e, quiz_id=quiz['id']: edit_quiz(page, quiz_id),
                                                style=button_style)

                delete_button = ft.ElevatedButton("Delete",
                                                  on_click=lambda e, quiz_id=quiz['id']: delete_quiz(page, quiz_id),
                                                  style=button_style)

                # Create a container for each quiz with buttons aligned properly
                quiz_container = ft.Container(
                    content=ft.Row([
                        ft.Column([
                            ft.Text(quiz['title'], size=20, weight=ft.FontWeight.BOLD),
                            ft.Text(f"By: {author_display_name}", size=16),
                            verified_text
                        ], alignment=ft.MainAxisAlignment.START),
                        ft.Row([edit_button, delete_button], spacing=10)  # Align buttons in a row
                    ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                    bgcolor=card_color,
                    border_radius=10,
                    margin=10,
                    padding=15,
                    shadow=[ft.BoxShadow(blur_radius=10, color="rgba(0, 0, 0, 0.2)", offset=ft.Offset(0, 4))]
                )

                quiz_list.controls.append(quiz_container)

        else:
            quiz_list.controls.append(ft.Text("No quizzes found.", size=20))

    except requests.exceptions.RequestException as e:
        print(f"Error fetching quizzes: {e}")
        quiz_list.controls.append(ft.Text("Failed to load quizzes.", color=ft.Colors.RED))

    # Add buttons for adding a new quiz and going back
    add_quiz_button = ft.ElevatedButton("Add Quiz", on_click=lambda e: show_add_quiz_page(page), style=button_style)
    back_button = ft.ElevatedButton("Back to Main Menu", on_click=lambda e: show_main_menu(page), style=button_style)

    # Add all components to the page
    page.add(title, quiz_list, add_quiz_button, back_button)
    page.update()


def delete_quiz(page: ft.Page, quiz_id: int):
    try:
        response = requests.delete(f"http://localhost:8000/api/quiz/{quiz_id}/", auth=(user_phone, user_password))
        if response.status_code == 204:
            page.add(ft.Text("Quiz deleted successfully!", color=ft.Colors.GREEN))
            show_make_quiz_menu(page)  # Refresh the list of quizzes
        else:
            error_message = response.json().get('error', 'An unknown error occurred.')
            page.add(ft.Text(error_message, color=ft.Colors.RED))

    except requests.exceptions.RequestException as e:
        print(f"Error deleting quiz: {e}")
        page.add(ft.Text("Failed to delete quiz.", color=ft.Colors.RED))


def show_add_quiz_page(page: ft.Page):
    page.clean()  # Clear current content

    title = ft.Text("Add a New Quiz", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    # Input fields for quiz details
    quiz_title_field = ft.TextField(label="Quiz Title", autofocus=True)
    quiz_description_field = ft.TextField(label="Description", multiline=True)
    available_time_field = ft.TextField(label="Available Time (HH:MM:SS)", value="00:10:00")  # Default to 10 minutes

    def save_quiz(e):
        data = {
            "title": quiz_title_field.value,
            "description": quiz_description_field.value,
            "available_time": available_time_field.value  # Ensure it's in HH:MM:SS format
        }

        try:
            response = requests.post("http://localhost:8000/api/quiz/", json=data, auth=(user_phone, user_password))
            if response.status_code == 201:
                page.add(ft.Text("Quiz created successfully!", color=ft.Colors.GREEN))
                show_make_quiz_menu(page)  # Navigate back to the quizzes menu
            else:
                error_message = response.json().get('error', 'An unknown error occurred.')
                page.add(ft.Text(error_message, color=ft.Colors.RED))

        except requests.exceptions.RequestException as e:
            print(f"Error creating quiz: {e}")
            page.add(ft.Text("Failed to create quiz.", color=ft.Colors.RED))

    save_button = ft.ElevatedButton("Save", on_click=save_quiz, style=button_style)
    cancel_button = ft.ElevatedButton("Cancel", on_click=lambda e: show_make_quiz_menu(page), style=button_style)

    page.add(title, quiz_title_field, quiz_description_field, available_time_field, save_button, cancel_button)
    page.update()


def edit_quiz(page: ft.Page, quiz_id):
    show_edit_quiz_page(page, quiz_id)  # Call the function to show the edit page


def show_edit_quiz_page(page: ft.Page, quiz_id: int):
    page.clean()  # Clear current content

    title = ft.Text("Edit Quiz", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    # Fetch quiz details
    try:
        response = requests.get(f"http://localhost:8000/api/quiz/{quiz_id}/", auth=(user_phone, user_password))
        response.raise_for_status()
        quiz_data = response.json()

        # Display quiz information
        quiz_title_field = ft.TextField(label="Quiz Title", value=quiz_data['title'], autofocus=True)
        quiz_description_field = ft.TextField(label="Description", value=quiz_data['description'], multiline=True)
        available_time_field = ft.TextField(label="Available Time (HH:MM:SS)", value=quiz_data['available_time'])

        # Display additional information
        score_text = ft.Text(f"Score: {quiz_data['score']}", size=16)
        created_at_date = quiz_data['created_at'].split("T")[0]  # Extract date part
        created_at_text = ft.Text(f"Created At: {created_at_date}", size=16)
        updated_at_date = quiz_data['updated_at'].split("T")[0]  # Extract date part
        updated_at_text = ft.Text(f"Updated At: {updated_at_date}", size=16)
        verified_text = ft.Text("Verified" if quiz_data['verified'] else "Not Verified",
                                color=ft.Colors.GREEN if quiz_data['verified'] else ft.Colors.RED)

        # Back button to return to the previous menu
        back_button = ft.ElevatedButton("Back", on_click=lambda e: show_make_quiz_menu(page), style=button_style)

        # Add question button
        add_question_button = ft.ElevatedButton("Add Question",
                                                on_click=lambda e: show_add_question_page(page, quiz_id),
                                                style=button_style)

        # Save button to update quiz details
        def save_quiz(e):
            data = {
                "title": quiz_title_field.value,
                "description": quiz_description_field.value,
                "available_time": available_time_field.value  # Ensure it's in HH:MM:SS format
            }

            try:
                response = requests.patch(f"http://localhost:8000/api/quiz/{quiz_id}/", json=data,
                                          auth=(user_phone, user_password))
                if response.status_code == 200:
                    page.add(ft.Text("Quiz updated successfully!", color=ft.Colors.GREEN))
                    show_make_quiz_menu(page)  # Navigate back to the quizzes menu
                else:
                    error_message = response.json().get('error', 'An unknown error occurred.')
                    page.add(ft.Text(error_message, color=ft.Colors.RED))

            except requests.exceptions.RequestException as e:
                print(f"Error updating quiz: {e}")
                page.add(ft.Text("Failed to update quiz.", color=ft.Colors.RED))

        save_button = ft.ElevatedButton("Save", on_click=save_quiz, style=button_style)

        # Fetch questions for this quiz
        questions_container = ft.Column(scroll=True)  # To hold the list of questions and make it scrollable
        try:
            questions_response = requests.get(f"http://localhost:8000/api/quiz/{quiz_id}/questions",
                                              auth=(user_phone, user_password))
            questions_response.raise_for_status()
            questions_data = questions_response.json()

            if questions_data:
                for question in questions_data:
                    question_title = ft.Text(question['question'], size=20)

                    edit_question_button = ft.ElevatedButton("Edit",
                                                             on_click=lambda e,
                                                                             question_id=question['id']: edit_question(
                                                                 page, question_id, quiz_id),
                                                             style=button_style)

                    delete_question_button = ft.ElevatedButton("Delete",
                                                               on_click=lambda e,
                                                                               question_id=question[
                                                                                   'id']: delete_question(
                                                                   page, quiz_id, question_id),
                                                               style=button_style)

                    question_container = ft.Container(
                        content=ft.Row([
                            question_title,
                            ft.Row([edit_question_button, delete_question_button], spacing=10),
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        bgcolor=card_color,
                        border_radius=10,
                        margin=10,
                        padding=10,
                        shadow=[ft.BoxShadow(blur_radius=5, color="rgba(0, 0, 0, 0.2)", offset=ft.Offset(0, 2))]
                    )

                    questions_container.controls.append(question_container)

            else:
                questions_container.controls.append(ft.Text("No questions found.", size=20))

        except requests.exceptions.RequestException as e:
            print(f"Error fetching questions: {e}")
            questions_container.controls.append(ft.Text("Failed to load questions.", color=ft.Colors.RED))

        # Add all components to the page
        page.add(title,
                 quiz_title_field,
                 quiz_description_field,
                 available_time_field,
                 score_text,
                 created_at_text,
                 updated_at_text,
                 verified_text,
                 save_button,
                 add_question_button,
                 back_button,
                 questions_container)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching quiz details: {e}")
        page.add(ft.Text("Failed to load quiz details.", color=ft.Colors.RED))

    page.update()


def delete_question(page: ft.Page, quiz_id: int, question_id: int):
    try:
        response = requests.delete(f"http://localhost:8000/api/quiz/{quiz_id}/questions/",
                                   json={"id": question_id},
                                   auth=(user_phone, user_password))

        if response.status_code == 204:
            page.add(ft.Text("Question deleted successfully!", color=ft.Colors.GREEN))
            show_edit_quiz_page(page, quiz_id)  # Refresh the question list
        else:
            error_message = response.json().get('error', 'An unknown error occurred.')
            page.add(ft.Text(error_message, color=ft.Colors.RED))

    except requests.exceptions.RequestException as e:
        print(f"Error deleting question: {e}")
        page.add(ft.Text("Failed to delete question.", color=ft.Colors.RED))


def edit_question(page: ft.Page, question_id: int, quiz_id: int):
    show_edit_question_page(page, quiz_id, question_id)  # Call the function to show the edit page


def show_edit_question_page(page: ft.Page, quiz_id: int, question_id: int):
    page.clean()  # Clear current content

    title = ft.Text("Edit Question", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    # Fetch question details
    try:
        response = requests.get(f"http://localhost:8000/api/quiz/{quiz_id}/questions/",
                                json={"id": question_id},
                                auth=(user_phone, user_password))
        response.raise_for_status()
        question_data = response.json()

        # Display question information
        question_field = ft.TextField(label="Question", value=question_data['question'], autofocus=True)
        option_a_field = ft.TextField(label="Option A", value=question_data['option_a'])
        option_b_field = ft.TextField(label="Option B", value=question_data['option_b'])
        option_c_field = ft.TextField(label="Option C", value=question_data['option_c'])
        option_d_field = ft.TextField(label="Option D", value=question_data['option_d'])
        correct_answer_field = ft.TextField(label="Correct Answer (a/b/c/d)", value=question_data['correct_answer'])

        # Back button to return to the previous menu
        back_button = ft.ElevatedButton("Back", on_click=lambda e: show_edit_quiz_page(page, quiz_id),
                                        style=button_style)

        # Save button to update question details
        def save_question(e):
            data = {
                "id": question_id,
                "question": question_field.value,
                "option_a": option_a_field.value,
                "option_b": option_b_field.value,
                "option_c": option_c_field.value,
                "option_d": option_d_field.value,
                "correct_answer": correct_answer_field.value  # Should be one of 'a', 'b', 'c', or 'd'
            }

            try:
                response = requests.patch(f"http://localhost:8000/api/quiz/{quiz_id}/questions/", json=data,
                                          auth=(user_phone, user_password))
                if response.status_code == 200:
                    page.add(ft.Text("Question updated successfully!", color=ft.Colors.GREEN))
                    show_edit_quiz_page(page, quiz_id)  # Navigate back to the edit quiz page
                else:
                    error_message = response.json().get('error', 'An unknown error occurred.')
                    page.add(ft.Text(error_message, color=ft.Colors.RED))

            except requests.exceptions.RequestException as e:
                print(f"Error updating question: {e}")
                page.add(ft.Text("Failed to update question.", color=ft.Colors.RED))

        save_button = ft.ElevatedButton("Save", on_click=save_question, style=button_style)

        # Add all components to the page
        page.add(title,
                 question_field,
                 option_a_field,
                 option_b_field,
                 option_c_field,
                 option_d_field,
                 correct_answer_field,
                 save_button,
                 back_button)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching question details: {e}")
        page.add(ft.Text("Failed to load question details.", color=ft.Colors.RED))

    page.update()


def show_add_question_page(page: ft.Page, quiz_id: int):
    page.clean()  # Clear current content

    title = ft.Text("Add a New Question", size=30, weight=ft.FontWeight.BOLD, color=text_color)

    # Input fields for question details
    question_field = ft.TextField(label="Question", autofocus=True)
    option_a_field = ft.TextField(label="Option A")
    option_b_field = ft.TextField(label="Option B")
    option_c_field = ft.TextField(label="Option C")
    option_d_field = ft.TextField(label="Option D")
    correct_answer_field = ft.TextField(label="Correct Answer (a/b/c/d)")

    def save_question(e):
        data = {
            "question": question_field.value,
            "option_a": option_a_field.value,
            "option_b": option_b_field.value,
            "option_c": option_c_field.value,
            "option_d": option_d_field.value,
            "correct_answer": correct_answer_field.value  # Should be one of 'a', 'b', 'c', or 'd'
        }

        try:
            response = requests.post(f"http://localhost:8000/api/quiz/{quiz_id}/questions/", json=data,
                                     auth=(user_phone, user_password))
            if response.status_code == 201:
                page.add(ft.Text("Question added successfully!", color=ft.Colors.GREEN))
                show_edit_quiz_page(page, quiz_id)  # Navigate back to the edit quiz page
            else:
                error_message = response.json().get('error', 'An unknown error occurred.')
                page.add(ft.Text(error_message, color=ft.Colors.RED))

        except requests.exceptions.RequestException as e:
            print(f"Error adding question: {e}")
            page.add(ft.Text("Failed to add question.", color=ft.Colors.RED))

    save_button = ft.ElevatedButton("Save", on_click=save_question, style=button_style)
    cancel_button = ft.ElevatedButton("Cancel", on_click=lambda e: show_edit_quiz_page(page, quiz_id),
                                      style=button_style)

    page.add(title,
             question_field,
             option_a_field,
             option_b_field,
             option_c_field,
             option_d_field,
             correct_answer_field,
             save_button,
             cancel_button)

    page.update()


ft.app(target=main)

# Quiz Application

## Description
This is a simple practical quiz app made with Django REST Framework (DRF) for the backend and Flet for the frontend. The application allows users to create, manage, and participate in quizzes.

## Educational Project
This project is primarily educational, and not much time has been spent on the security of the APIs and the app itself. It serves as a practical example of integrating a backend with a frontend application.

## Frontend
The frontend of this app is a Flet application written with the help of the [Flet documentation](https://flet.dev/docs/), AI assistance, and some prior experience I had with Flet. The focus was more on ensuring that the integration between the frontend and backend works flawlessly rather than on making the frontend visually appealing.

## Features
- **User Authentication**: 
  - Registration and login functionality.
  - Error messages are displayed clearly for each field.
  
- **Quiz Management**: 
  - Create quizzes and questions with the ability to edit and delete them.
  - View quiz details including score, creation date, and verification status.

- **Main Quiz Logic**: 
  - Core functionalities to play quizzes.
  
- **Account Info Page**: 
  - View and update user information.
  
- **Responsive Design**: 
  - The application is designed to be user-friendly with clear navigation.

## Instructions for Running the Project

1. **Clone the Repository**
   ```
    git clone https://github.com/HjtDev/QuizAPP.git
    cd QuizAPP
   ```

2. **Set Up the Django Backend**
   - Ensure you have Python and Django installed.
   - Install required packages:
     ```
     pip install -r requirements.txt
     ```
   - Configure your PostgreSQL database in `settings.py` of your Django project according to your local setup.
   - Ensure you have Redis installed and configured as well.

3. **Run Migrations**
   ```
    python manage.py migrate
   ```

4. **Create a Superuser (Optional)**
   ```
    python manage.py createsuperuser
   ```

5. **Run the Django Development Server**
   ```
    python manage.py runserver
   ```

6. **Set Up the Flet Frontend**
   - Ensure you have Flet installed:
     ```
     pip install flet
     ```
   - To run the app, create a new Flet environment:
     ```
     cd flet
     flet run main.py
     ```

7. **Access the Application**
   - Open your browser and navigate to `http://localhost:8000/admin` to access the admin pannel.

## Note on Database Configuration
Make sure you have PostgreSQL and Redis installed and configured for your own use case. Update your Django settings accordingly to connect to your PostgreSQL database.

## Flet Tutorial
For more information on how to use Flet, you can refer to their [official tutorial](https://flet.dev/docs/).

---

Feel free to contribute or suggest improvements!

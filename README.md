# Flask Task Manager App

## Overview

The Flask Task Manager App is a comprehensive, web-based task management system built using Flask, a lightweight web application framework in Python. This application enables users to create, view, update, and delete tasks efficiently. Designed to be user-friendly and straightforward, it helps users keep track of their tasks seamlessly, with tasks displayed on a calendar using FullCalendar for an intuitive and visual experience.

## Features

### User Authentication
- **Registration and Login**: Users can register for an account and log in securely.
- **Session Management**: User sessions are maintained, ensuring that tasks are personalized and securely managed.

### Task Management
- **Task Creation**: Users can add new tasks with a title & description.
- **Calendar View**: Tasks are displayed on a calendar using FullCalendar, providing an intuitive and visual representation of tasks.
- **Task Viewing**: Users can view their tasks, on the FullCalendar.
- **Task Editing**: Users can edit the details of their tasks, including title, description.
- **Task Deletion**: Users can delete tasks that are no longer needed.

### Advanced Task Features
- **Task Types**: Supports different task types, such as single-day or multi-day tasks.
- **Task Completion**: Users can mark tasks as complete or incomplete.
- **Search Functionality**: Users can search for tasks by title.
- **Position Update**: Users can update task positions and dates using drag-and-drop functionality on the calendar.

### User Profile and Account Management
- **Profile Viewing**: Users can view their profile information, including task statistics.
- **Password Management**: Users can change their password, with validation to ensure strong security.
- **Account Deletion**: Users can delete their account along with all associated tasks.

### Administrative Features
- **Admin User Management**: Admins can view and manage all user accounts.
- **Admin Task Management**: Admins can delete user accounts and all associated tasks.

### Security
- **Password Hashing**: User passwords are hashed using secure algorithms.
- **Input Sanitization**: User inputs are sanitized to prevent XSS and other attacks.
- **Session Management**: Secure session management practices to ensure user data is protected.

## Getting Started

### Prerequisites
- Python 3.x
- Flask
- Flask-Login
- Flask-SQLAlchemy
- Flask-WTF
- WTForms
- Bleach
- Werkzeug

### Installation
1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/flask-task-manager.git
    cd flask-task-manager
    ```

2. Create a virtual environment and activate it:
    ```sh
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the application:
    ```sh
    flask run
    ```

## Usage

### Home Page
- The home page displays the user's tasks on a calendar using FullCalendar, allowing them to add new tasks, edit existing ones, or mark them as complete.

### Task Management
- Users can navigate to the task management interface to create, view, update, and delete tasks.

### Profile Management
- The profile page displays user-specific information and allows users to change their password or delete their account.

### Admin Interface
- Admin users have access to a dedicated admin interface where they can manage all user accounts and associated tasks.

## Contribution

Contributions are welcome! Please follow these steps to contribute:

1. Fork the repository.
2. Create a new branch:
    ```sh
    git checkout -b feature/your-feature
    ```
3. Make your changes and commit them:
    ```sh
    git commit -m "Add some feature"
    ```
4. Push to the branch:
    ```sh
    git push origin feature/your-feature
    ```
5. Create a new pull request.

---

Feel free to reach out with any questions or feedback. Happy task managing!

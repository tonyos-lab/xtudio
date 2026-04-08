# Project Requirements — TaskFlow (Simple Todo App)

## Project Overview
TaskFlow is a simple task management application for individual users.
Users can create, organize, and track their personal tasks.

## Functional Requirements

### User Authentication
Users must be able to register for an account using their email address and a password.
Email verification is required before users can log in for the first time.
Users must be able to log in and log out of their accounts.
Users must be able to reset their password via an email link if they forget it.

### Task Management
Users must be able to create new tasks with a title and optional description.
Users must be able to mark tasks as complete or incomplete.
Users must be able to edit the title and description of existing tasks.
Users must be able to delete tasks they no longer need.
Users must be able to view a list of all their tasks, filtered by status (all, active, completed).

### Task Organisation
Users must be able to assign a due date to any task.
Tasks with a due date that has passed must be visually highlighted as overdue.

## Non-Functional Requirements

### Performance
The application must load the task list within 1 second for up to 50 concurrent users.

### Usability
The interface must be usable on both desktop and mobile devices.
All actions (create, edit, delete, complete) must be accessible without more than 2 clicks.

## Technical Requirements

### Stack
The application must be built using Django 5.1 and PostgreSQL.
The application must be deployable to a standard Linux VPS using gunicorn and nginx.

### Data
All user data must be isolated — users must never see another user's tasks.

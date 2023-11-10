import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from tkcalendar import DateEntry
import time
from datetime import datetime, timedelta
from plyer import notification
import sqlite3


class Task:
    def __init__(self, task, date):
        self.task = task
        self.date = date
        self.timer_hours = 0
        self.timer_minutes = 0
        self.timer_seconds = 0
        self.remaining_time = timedelta()
        self.timer_running = False

    def set_timer(self, hours, minutes, seconds):
        self.timer_hours = hours
        self.timer_minutes = minutes
        self.timer_seconds = seconds
        self.remaining_time = timedelta(hours=hours, minutes=minutes, seconds=seconds)

    def start_timer(self):
        self.timer_running = True
        while self.remaining_time.total_seconds() > 0:
            time_label.config(text=f"Time remaining: {self.remaining_time}")
            time.sleep(1)
            self.remaining_time -= timedelta(seconds=1)
        self.timer_running = False
        time_label.config(text="Timer finished!")
        show_notification(self.task)

    def __str__(self):
        return f"{self.task} ({self.date})"


def authenticate():
    username = username_entry.get()
    password = password_entry.get()

    # Connect to the database
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Check if the username and password match a record in the database
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()

    # Close the database connection
    conn.close()

    if user:
        show_todo_list()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password")


def show_todo_list():
    login_frame.destroy()

    global entry, listbox, cal, time_label, root, tasks, timer_hours, timer_minutes, timer_seconds

    root = tk.Tk()
    root.title("To-Do List")

    tasks = []

    # Create and pack the entry widget
    entry = tk.Entry(root, font=("Arial", 14))
    entry.pack(pady=10)

    # Create and pack the calendar widget
    cal = DateEntry(root, width=12, background='darkblue',
                    foreground='white', borderwidth=2, font=("Arial", 12))
    cal.pack(pady=5)

    # Create and pack the add task button
    add_button = tk.Button(root, text="Add Task", command=add_task)
    add_button.pack(pady=5)

    # Create and pack the listbox to display tasks
    listbox = tk.Listbox(root, width=50, height=10, font=("Arial", 12))
    listbox.pack()

    # Create and pack the timer dropdowns
    timer_frame = ttk.Frame(root)
    timer_frame.pack(pady=10)

    hours_label = ttk.Label(timer_frame, text="Hours:")
    hours_label.grid(column=0, row=0, padx=5)

    hours_var = tk.StringVar(root)
    hours_var.set("00")
    hours_dropdown = ttk.OptionMenu(timer_frame, hours_var, *["{:02d}".format(i) for i in range(24)])
    hours_dropdown.grid(column=1, row=0, padx=5)

    minutes_label = ttk.Label(timer_frame, text="Minutes:")
    minutes_label.grid(column=2, row=0, padx=5)

    minutes_var = tk.StringVar(root)
    minutes_var.set("00")
    minutes_dropdown = ttk.OptionMenu(timer_frame, minutes_var, *["{:02d}".format(i) for i in range(60)])
    minutes_dropdown.grid(column=3, row=0, padx=5)

    seconds_label = ttk.Label(timer_frame, text="Seconds:")
    seconds_label.grid(column=4, row=0, padx=5)

    seconds_var = tk.StringVar(root)
    seconds_var.set("00")
    seconds_dropdown = ttk.OptionMenu(timer_frame, seconds_var, *["{:02d}".format(i) for i in range(60)])
    seconds_dropdown.grid(column=5, row=0, padx=5)

    # Create and pack the start timer button
    timer_button = tk.Button(root, text="Start Timer", command=start_timer)
    timer_button.pack(pady=5)

    # Create and pack the label for displaying time remaining
    time_label = tk.Label(root, text="No task selected")
    time_label.pack(pady=10)

    root.mainloop()


def add_task():
    task = entry.get()
    date = cal.get_date()
    if task and date:
        tasks.append(Task(task, date))
        listbox.insert(tk.END, str(tasks[-1]))
        clear_entry_fields()


def clear_entry_fields():
    entry.delete(0, tk.END)
    cal.set_date(datetime.today())


def start_timer():
    try:
        index = listbox.curselection()[0]
        task = tasks[index]
        hours = int(hours_var.get())
        minutes = int(minutes_var.get())
        seconds = int(seconds_var.get())
        task.set_timer(hours, minutes, seconds)
        if not task.timer_running:
            task.start_timer()
    except IndexError:
        pass


def show_notification(task):
    notification_title = "To-Do List Timer"
    notification_message = f"The timer for '{task}' has finished!"
    notification_timeout = 10  # Display notification for 10 seconds

    notification.notify(
        title=notification_title,
        message=notification_message,
        timeout=notification_timeout
    )


def create_users_table():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()

    # Create the users table if it doesn't exist
    c.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")

    # Insert a default user for testing
    c.execute("INSERT INTO users VALUES (?, ?)", ("admin", "password"))

    conn.commit()
    conn.close()


def main():
    global username_entry, password_entry, login_frame

    # Create the users table and insert a default user
    create_users_table()

    root = tk.Tk()
    root.title("Login")

    login_frame = ttk.Frame(root, padding="20 10 20 10")
    login_frame.pack()

    # Username label and entry
    username_label = ttk.Label(login_frame, text="Username:")
    username_label.grid(column=0, row=0, sticky="W")
    username_entry = ttk.Entry(login_frame, width=30)
    username_entry.grid(column=1, row=0)

    # Password label and entry
    password_label = ttk.Label(login_frame, text="Password:")
    password_label.grid(column=0, row=1, sticky="W")
    password_entry = ttk.Entry(login_frame, width=30, show="*")
    password_entry.grid(column=1, row=1)

    # Login button
    login_button = ttk.Button(login_frame, text="Login", command=authenticate)
    login_button.grid(column=0, row=2, columnspan=2, pady=10)

    root.mainloop()


if __name__ == '__main__':
    main()

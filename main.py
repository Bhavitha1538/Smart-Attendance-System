import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import csv

DB_NAME = "attendance.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def setup_database():
    with connect_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_no TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                roll_no TEXT NOT NULL,
                attendance_date TEXT NOT NULL,
                status TEXT NOT NULL CHECK(status IN ('Present', 'Absent')),
                UNIQUE(roll_no, attendance_date),
                FOREIGN KEY (roll_no) REFERENCES students(roll_no)
            )
        """)


class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart Attendance System")
        self.root.geometry("900x600")
        self.root.minsize(760, 500)

        title = ttk.Label(
            root, text="Smart Attendance System",
            font=("Arial", 20, "bold")
        )
        title.pack(pady=12)

        form = ttk.LabelFrame(root, text="Add Student")
        form.pack(fill="x", padx=15, pady=6)

        ttk.Label(form, text="Roll Number:").grid(row=0, column=0, padx=8, pady=10)
        self.roll_entry = ttk.Entry(form, width=18)
        self.roll_entry.grid(row=0, column=1, padx=8, pady=10)

        ttk.Label(form, text="Student Name:").grid(row=0, column=2, padx=8, pady=10)
        self.name_entry = ttk.Entry(form, width=24)
        self.name_entry.grid(row=0, column=3, padx=8, pady=10)

        ttk.Label(form, text="Department:").grid(row=0, column=4, padx=8, pady=10)
        self.department_entry = ttk.Entry(form, width=16)
        self.department_entry.grid(row=0, column=5, padx=8, pady=10)

        ttk.Button(form, text="Add Student", command=self.add_student).grid(
            row=0, column=6, padx=8, pady=10
        )

        controls = ttk.Frame(root)
        controls.pack(fill="x", padx=15, pady=8)

        ttk.Label(controls, text="Date (YYYY-MM-DD):").pack(side="left")
        self.date_entry = ttk.Entry(controls, width=14)
        self.date_entry.insert(0, date.today().isoformat())
        self.date_entry.pack(side="left", padx=6)

        ttk.Label(controls, text="Status:").pack(side="left", padx=(15, 4))
        self.status_var = tk.StringVar(value="Present")
        ttk.Combobox(
            controls, textvariable=self.status_var,
            values=["Present", "Absent"], state="readonly", width=10
        ).pack(side="left")

        ttk.Button(
            controls, text="Mark Selected Student",
            command=self.mark_attendance
        ).pack(side="left", padx=10)

        ttk.Button(controls, text="Refresh", command=self.load_students).pack(side="left")
        ttk.Button(controls, text="Export Report (CSV)", command=self.export_report).pack(
            side="right"
        )

        table_frame = ttk.LabelFrame(root, text="Student List")
        table_frame.pack(fill="both", expand=True, padx=15, pady=8)

        columns = ("roll_no", "name", "department", "today_status")
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings", height=14
        )
        self.tree.heading("roll_no", text="Roll Number")
        self.tree.heading("name", text="Student Name")
        self.tree.heading("department", text="Department")
        self.tree.heading("today_status", text="Attendance Status")
        self.tree.column("roll_no", width=130, anchor="center")
        self.tree.column("name", width=240)
        self.tree.column("department", width=180)
        self.tree.column("today_status", width=160, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        self.summary_label = ttk.Label(root, text="")
        self.summary_label.pack(pady=(0, 10))

        self.load_students()

    def get_selected_date(self):
        selected_date = self.date_entry.get().strip()
        try:
            date.fromisoformat(selected_date)
            return selected_date
        except ValueError:
            messagebox.showerror("Invalid date", "Enter the date as YYYY-MM-DD.")
            return None

    def add_student(self):
        roll = self.roll_entry.get().strip()
        name = self.name_entry.get().strip()
        department = self.department_entry.get().strip()

        if not roll or not name:
            messagebox.showwarning("Missing details", "Enter roll number and student name.")
            return

        try:
            with connect_db() as conn:
                conn.execute(
                    "INSERT INTO students (roll_no, name, department) VALUES (?, ?, ?)",
                    (roll, name, department)
                )
            messagebox.showinfo("Success", "Student added successfully.")
            self.roll_entry.delete(0, tk.END)
            self.name_entry.delete(0, tk.END)
            self.department_entry.delete(0, tk.END)
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate roll number", "That roll number already exists.")

    def mark_attendance(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select student", "Choose a student from the list first.")
            return

        selected_date = self.get_selected_date()
        if not selected_date:
            return

        roll = self.tree.item(selected[0], "values")[0]
        status = self.status_var.get()

        with connect_db() as conn:
            conn.execute("""
                INSERT INTO attendance (roll_no, attendance_date, status)
                VALUES (?, ?, ?)
                ON CONFLICT(roll_no, attendance_date)
                DO UPDATE SET status = excluded.status
            """, (roll, selected_date, status))

        messagebox.showinfo("Saved", f"{status} attendance saved for {roll}.")
        self.load_students()

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        selected_date = self.date_entry.get().strip()
        with connect_db() as conn:
            rows = conn.execute("""
                SELECT s.roll_no, s.name, COALESCE(s.department, ''),
                       COALESCE(a.status, 'Not marked')
                FROM students s
                LEFT JOIN attendance a
                  ON s.roll_no = a.roll_no AND a.attendance_date = ?
                ORDER BY s.roll_no
            """, (selected_date,)).fetchall()

        for row in rows:
            self.tree.insert("", tk.END, values=row)

        marked = sum(1 for row in rows if row[3] in ("Present", "Absent"))
        present = sum(1 for row in rows if row[3] == "Present")
        self.summary_label.config(
            text=f"Students: {len(rows)}   |   Marked: {marked}   |   Present: {present}"
        )

    def export_report(self):
        selected_date = self.get_selected_date()
        if not selected_date:
            return

        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile=f"attendance_{selected_date}.csv"
        )
        if not filename:
            return

        with connect_db() as conn:
            rows = conn.execute("""
                SELECT s.roll_no, s.name, COALESCE(s.department, ''),
                       COALESCE(a.status, 'Not marked')
                FROM students s
                LEFT JOIN attendance a
                  ON s.roll_no = a.roll_no AND a.attendance_date = ?
                ORDER BY s.roll_no
            """, (selected_date,)).fetchall()

        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Roll Number", "Student Name", "Department", "Status"])
            writer.writerows(rows)

        messagebox.showinfo("Export complete", f"Report saved to:\n{filename}")


if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()

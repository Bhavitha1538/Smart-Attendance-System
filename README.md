# Smart Attendance System

A beginner-friendly Python college mini project for managing student attendance.

## Features
- Add students with roll number, name, and department.
- Mark attendance as Present or Absent.
- Save attendance by date.
- Update a student's attendance for the same date.
- View the day's attendance status.
- Export the selected day's report as a CSV file.
- Store data locally in an SQLite database (`attendance.db`).

## Technology
- Python 3
- Tkinter (desktop graphical interface)
- SQLite (built into Python)

## How to run
1. Install Python 3.
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Run:

   ```bash
   python main.py
   ```

Tkinter and SQLite are included with most standard Python installations. On some Linux systems, Tkinter may need to be installed separately.

## Project note
This is a working prototype of the attendance-recording and teacher/admin workflow described in the grant proposal. Bluetooth classroom verification, cryptographic hardware, face/liveness checks, AI review, push notifications, and the campus AI lab are **not implemented** in this starter version. Those would require separate hardware, services, testing, and privacy/security review.

## Suggested future improvements
- Add student attendance percentage across a date range.
- Add teacher/admin login.
- Add a class-wise report.
- Add a web or Android interface.

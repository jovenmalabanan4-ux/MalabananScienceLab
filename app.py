import os
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "malabanan-science-lab-secret-key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEACHER_FOLDER = os.path.join(BASE_DIR, "teacher_files")
STUDENT_FOLDER = os.path.join(BASE_DIR, "student_uploads")

os.makedirs(TEACHER_FOLDER, exist_ok=True)
os.makedirs(STUDENT_FOLDER, exist_ok=True)

STUDENT_PASSWORD = "Joven3031"


def list_files(folder_path):
    if not os.path.exists(folder_path):
        return []
    files = []
    for name in sorted(os.listdir(folder_path)):
        full_path = os.path.join(folder_path, name)
        if os.path.isfile(full_path):
            size_kb = round(os.path.getsize(full_path) / 1024, 1)
            files.append({"name": name, "size_kb": size_kb})
    return files


@app.route("/")
@app.route("/introduction")
def introduction():
    return render_template("index.html", active_page="introduction")


@app.route("/home")
def home():
    teacher_count = len(list_files(TEACHER_FOLDER))
    return render_template("index.html", active_page="home", teacher_count=teacher_count)


@app.route("/notes")
def notes():
    return render_template("index.html", active_page="notes")


@app.route("/files", methods=["GET", "POST"])
def files():
    # Always default to 'teacher' view when opening /files via GET
    view_mode = request.args.get("view", "teacher")
    student_unlocked = False

    if request.method == "POST":
        action = request.form.get("action")

        if action == "unlock_student":
            view_mode = "student"
            entered_password = request.form.get("password", "")
            if entered_password == STUDENT_PASSWORD:
                student_unlocked = True
            else:
                flash("Incorrect student password. Please try again.", "error")

        elif action == "upload_student":
            view_mode = "student"
            entered_password = request.form.get("password", "")
            if entered_password != STUDENT_PASSWORD:
                flash("Session locked. Enter password Joven3031 to upload.", "error")
            else:
                student_unlocked = True
                uploaded_file = request.files.get("student_file")
                if not uploaded_file or uploaded_file.filename == "":
                    flash("Please choose a file to upload.", "error")
                else:
                    safe_name = secure_filename(uploaded_file.filename)
                    save_path = os.path.join(STUDENT_FOLDER, safe_name)
                    uploaded_file.save(save_path)
                    flash(f"Uploaded '{safe_name}' successfully!", "success")

    teacher_files = list_files(TEACHER_FOLDER)
    student_files = list_files(STUDENT_FOLDER)

    return render_template(
        "index.html",
        active_page="files",
        view_mode=view_mode,
        student_unlocked=student_unlocked,
        teacher_files=teacher_files,
        student_files=student_files,
    )


@app.route("/files/teacher/<path:filename>")
def download_teacher_file(filename):
    return send_from_directory(TEACHER_FOLDER, filename, as_attachment=False)


@app.route("/files/student/<path:filename>")
def download_student_file(filename):
    return send_from_directory(STUDENT_FOLDER, filename, as_attachment=True)


@app.route("/game")
def game():
    return render_template("index.html", active_page="game")


if __name__ == "__main__":
    app.run(debug=True)
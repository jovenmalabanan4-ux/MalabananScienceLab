import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "malabanan-science-lab-dev-key-2026")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16 MB max upload size

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEACHER_FOLDER = os.path.join(BASE_DIR, "teacher_files")
STUDENT_FOLDER = os.path.join(BASE_DIR, "student_uploads")

os.makedirs(TEACHER_FOLDER, exist_ok=True)
os.makedirs(STUDENT_FOLDER, exist_ok=True)

STUDENT_PASSWORD = os.environ.get("STUDENT_PASSWORD", "Joven3031")


def list_files(folder_path):
    files = []
    if os.path.exists(folder_path):
        for filename in sorted(os.listdir(folder_path)):
            full_path = os.path.join(folder_path, filename)
            if os.path.isfile(full_path):
                size_kb = round(os.path.getsize(full_path) / 1024, 1)
                files.append({"name": filename, "size_kb": size_kb})
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


@app.route("/game")
def game():
    return render_template("index.html", active_page="game")


@app.route("/files", methods=["GET", "POST"])
def files():
    view_mode = request.args.get("view", "teacher")
    student_unlocked = session.get("student_unlocked", False)

    if request.method == "POST":
        action = request.form.get("action")

        if action == "unlock_student":
            entered_pw = request.form.get("password", "")
            if entered_pw == STUDENT_PASSWORD:
                session["student_unlocked"] = True
                student_unlocked = True
                flash("Student File Upload unlocked!", "success")
            else:
                flash("Incorrect password. Please try again.", "error")
            return redirect(url_for("files", view="student"))

        elif action == "lock_student":
            session.pop("student_unlocked", None)
            flash("Student upload locked.", "success")
            return redirect(url_for("files", view="student"))

        elif action == "upload_student":
            if not session.get("student_unlocked"):
                flash("Session locked. Please enter the student password first.", "error")
                return redirect(url_for("files", view="student"))

            uploaded_file = request.files.get("student_file")
            if not uploaded_file or uploaded_file.filename == "":
                flash("Please choose a file before uploading.", "error")
                return redirect(url_for("files", view="student"))

            safe_name = secure_filename(uploaded_file.filename)
            if not safe_name:
                flash("Invalid file name.", "error")
                return redirect(url_for("files", view="student"))

            uploaded_file.save(os.path.join(STUDENT_FOLDER, safe_name))
            flash(f"Uploaded '{safe_name}' successfully!", "success")
            return redirect(url_for("files", view="student"))

    teacher_files = list_files(TEACHER_FOLDER)
    student_files = list_files(STUDENT_FOLDER)

    return render_template(
        "index.html",
        active_page="files",
        view_mode=view_mode,
        teacher_files=teacher_files,
        student_files=student_files,
        student_unlocked=student_unlocked,
    )


@app.route("/download/teacher/<path:filename>")
def download_teacher_file(filename):
    return send_from_directory(TEACHER_FOLDER, filename)


@app.route("/download/student/<path:filename>")
def download_student_file(filename):
    if not session.get("student_unlocked"):
        flash("Please unlock Student File view first.", "error")
        return redirect(url_for("files", view="student"))
    return send_from_directory(STUDENT_FOLDER, filename)


if __name__ == "__main__":
    app.run(debug=False)
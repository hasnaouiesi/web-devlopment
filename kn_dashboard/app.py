import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///table.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":

        # Get the user's entry from the form
        name = request.form.get("Full name")
        age = request.form.get("Age")
        payed = request.form.get("payed") or "0"
        year = request.form.get("year")
        date = request.form.get("date")
        modules =" ,".join(request.form.getlist("modules"))
        contact = request.form.get("contact")

        # Add the birthday to the database
        if name and age and year and contact and modules:
            db.execute(
                "INSERT INTO app_tab (name, age, payed, year, contact, date, modules) VALUES (?, ?, ?, ?, ?, ?, ?)",
                name,
                age,
                payed,
                year,
                contact,
                date,
                modules
            )

        return redirect("/")

    else:
        # Get all birthdays from the database
        table = db.execute("SELECT * FROM app_tab")

        # Display the birthdays
        return render_template("index.html", app_tab=table)

@app.route("/deleting", methods=["POST"])
def deleting():
    if request.method == "POST":
        the_one = request.form.get("id")
        db.execute(
            "DELETE FROM tracking WHERE candidate_id = ?",
            the_one
        )
        db.execute(
            "DELETE FROM app_tab WHERE id = ?",
            the_one
        )

    return redirect("/")



@app.route("/tracking/<int:candidate_id>/<int:tracking_year>")
def get_tracking(candidate_id, tracking_year):

    rows = db.execute(
        "SELECT box, checked FROM tracking "
        "WHERE candidate_id = ? AND tracking_year = ?",
        candidate_id,
        tracking_year
    )

    return jsonify(rows)


@app.route("/tracking/<int:candidate_id>/<int:tracking_year>/<int:box>", methods=["POST"])
def save_tracking(candidate_id, tracking_year, box):

    data = request.get_json()
    checked = data["checked"]
    print("SAVING:", candidate_id, tracking_year, box, checked)
    existing = db.execute(
        "SELECT id FROM tracking "
        "WHERE candidate_id = ? AND tracking_year = ? AND box = ?",
        candidate_id,
        tracking_year,
        box
    )

    if existing:
        db.execute(
            "UPDATE tracking SET checked = ? WHERE id = ?",
            checked,
            existing[0]["id"]
        )
    else:
        db.execute(
            "INSERT INTO tracking (candidate_id, tracking_year, box, checked) "
            "VALUES (?, ?, ?, ?)",
            candidate_id,
            tracking_year,
            box,
            checked
        )

    return jsonify({"success": True})

@app.post("/update-data/<int:candidate_id>")
def update_data(candidate_id):

    data = request.get_json()

    field = data["field"]
    value = data["value"]

    allowed = ["payed", "year", "date", "modules"]

    if field not in allowed:
        return "Invalid field", 400

    db.execute(
        f"UPDATE app_tab SET {field} = ? WHERE id = ?",
        value,
        candidate_id
    )

    return "", 204
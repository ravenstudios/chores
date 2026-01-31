from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from .extensions import db
from .models import Chore
from collections import defaultdict
from datetime import datetime

main = Blueprint("main", __name__)

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
VALID_DAYS = set(DAYS)



@main.route("/")
def home():
    chores = Chore.query.all()

    chores_by_day = defaultdict(list)
    for chore in chores:
        chores_by_day[chore.day].append(chore)

    # Python: Mon=0 ... Sun=6, so map it to your labels
    days_by_py_index = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    today = days_by_py_index[datetime.now().weekday()]

    return render_template(
        "home.html",
        chores_by_day=chores_by_day,
        days=DAYS,
        today=today
    )




@main.route("/add-chore/<day>", methods=["GET", "POST"])
def add_chore(day):
    day = (day or "").strip()

    if request.method == "POST":
        title = request.form.get("title", "").strip()

        if not title:
            return render_template(
                "add-chore.html",
                error="Chore title is required",
                title=title,
                day=day
            )

        chore = Chore(title=title, day=day)
        db.session.add(chore)
        db.session.commit()
        return redirect(url_for("main.home"))

    return render_template("add-chore.html", day=day)





@main.route("/chore/<int:chore_id>/edit", methods=["GET", "POST"])
def edit_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        day = request.form.get("day", "").strip()
        notes = request.form.get("notes", "").strip()
        history = request.form.get("history", "").strip()
        done = (request.form.get("done") == "on")

        if not title:
            return render_template("edit-chore.html", chore=chore, error="Title is required")

        if day not in VALID_DAYS:
            return render_template("edit-chore.html", chore=chore, error="Please pick a valid day")

        # (Optional) log changes to history automatically
        changes = []
        if chore.title != title:
            changes.append(f"title: '{chore.title}' -> '{title}'")
        if chore.day != day:
            changes.append(f"day: {chore.day} -> {day}")
        if chore.done != done:
            changes.append(f"done: {chore.done} -> {done}")
        if chore.notes != notes:
            changes.append("notes updated")
        if changes:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            auto_entry = f"{ts} - edited ({', '.join(changes)})\n"
            chore.history = (chore.history or "") + auto_entry

        chore.title = title
        chore.day = day
        chore.done = done
        chore.notes = notes
        chore.history = history or chore.history  # keep existing if blank (optional)

        db.session.commit()
        return redirect(url_for("main.home"))

    return render_template("edit-chore.html", chore=chore)



@main.route("/chore/<int:chore_id>/delete", methods=["POST"])
def delete_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)
    title = chore.title  # grab before delete

    db.session.delete(chore)
    db.session.commit()

    # show a message page, then bounce home
    return render_template(
        "message.html",
        message=f'✅ Deleted "{title}"',
        redirect_url=url_for("main.home"),
        delay_ms=2500
    )



@main.route("/chore/<int:chore_id>/toggle", methods=["POST"])
def toggle_chore(chore_id):
    chore = Chore.query.get_or_404(chore_id)

    # checkbox sends "on" when checked, missing when unchecked
    new_done = (request.form.get("done") == "on")

    # Only log if it actually changed (prevents spam)
    if chore.done != new_done:
        chore.done = new_done

        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        action = "DONE" if new_done else "NOT DONE"

        entry = f"{ts} - set {action}\n"
        chore.history = (chore.history or "") + entry

        db.session.commit()

    return redirect(url_for("main.home"))


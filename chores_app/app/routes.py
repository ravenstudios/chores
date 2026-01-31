from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from .extensions import db
from .models import Chore

main = Blueprint("main", __name__)


@main.route("/api/health")
def health():
    return jsonify(status="ok")



@main.route("/")
def home():
    chores = Chore.query.order_by(Chore.created_at.desc()).all()
    return render_template("home.html", chores=chores)

@main.route("/about")
def about():
    return render_template("about.html", name="Rob")




@main.route("/add-chore", methods=["GET", "POST"])
def add_chore():
    if request.method == "POST":
        title = request.form.get("title", "").strip()

        if not title:
            # re-render page with error
            return render_template(
                "add-chore.html",
                error="Chore title is required",
                title=title
            )

        chore = Chore(title=title)
        db.session.add(chore)
        db.session.commit()

        return redirect(url_for("main.home"))

    # GET request
    return render_template("add-chore.html")



@main.route("/api/tasks", methods=["GET"])
def list_chores():
    chores = Chore.query.order_by(Chore.created_at.desc()).all()
    return jsonify([
        {"id": t.id, "title": t.title, "done": t.done, "created_at": t.created_at.isoformat()}
        for t in chores
    ])

@main.route("/api/tasks", methods=["POST"])
def create_chore():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify(error="title is required"), 400

    chore = Chore(title=title)
    db.session.add(chore)
    db.session.commit()
    return jsonify(id=chore.id, title=chore.title, done=chore.done), 201

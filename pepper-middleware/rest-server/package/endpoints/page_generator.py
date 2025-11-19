from flask import render_template, request
from ast import literal_eval

from ..server import app
from ..decorator import log

@app.route("/tablet")
@log("/tablet")
def get_tablet_page():
    text = literal_eval(request.args.get("text", default="Empty text"))
    return render_template("tablet.html", text=text)

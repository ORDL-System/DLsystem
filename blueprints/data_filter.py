from flask import (Blueprint,
                   render_template)

bp = Blueprint(name="data_filter", import_name=__name__, url_prefix="/data_filter")


@bp.route("/cls", methods=["GET", "POST"])
def cls_filter():
    return render_template("templates_cls/data_filter.html")
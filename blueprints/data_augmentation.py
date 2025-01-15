from flask import (Blueprint,
                   render_template)

bp = Blueprint(name="data_augmentation", import_name=__name__, url_prefix="/data_augmentation")


@bp.route("/da", methods=["GET", "POST"])
def data_augmentation():
    return render_template("templates_da/data_augmentation.html")
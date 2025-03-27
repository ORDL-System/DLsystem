from flask import (Blueprint,
                   render_template)

bp = Blueprint(name="data_augmentation", import_name=__name__, url_prefix="/data_augmentation")


@bp.route("/da", methods=["GET", "POST"])
def data_augmentation():
    return render_template("templates_da/data_augmentation.html")

@bp.route("/cls", methods=["GET", "POST"])
def cls_aug():
    return render_template("templates_cls/data_aug.html")
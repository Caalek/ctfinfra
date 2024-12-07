import os

from CTFd.plugins import override_template


def load(app):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    template_path = os.path.join(dir_path, "navbar.html")
    override_template("components/navbar.html", open(template_path).read())
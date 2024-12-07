import os
import functools

from flask import (
    render_template,
    jsonify,
    Blueprint,
    url_for,
    session,
    redirect,
    request,
    abort,
)
from sqlalchemy.sql import or_

from CTFd import utils, scoreboard
from CTFd.models import db, Solves, Challenges, Teams, TeamFieldEntries, Fields
from CTFd.plugins import override_template
from CTFd.utils.config import is_scoreboard_frozen, ctf_theme, is_users_mode
from CTFd.utils.config.visibility import challenges_visible, scores_visible
from CTFd.utils.dates import ctf_started, ctftime, view_after_ctf, unix_time_to_utc
from CTFd.views import views
from CTFd.utils.user import is_admin, authed
from CTFd.constants.config import (
    ConfigTypes,
    ScoreVisibilityTypes,
)
from CTFd.utils import get_config


def check_matrix_score_visibility(f):
    @functools.wraps(f)
    def _check_matrix_score_visibility(*args, **kwargs):
        v = get_config(ConfigTypes.SCORE_VISIBILITY)
        if v == ScoreVisibilityTypes.PUBLIC:
            return f(*args, **kwargs)

        elif v == ScoreVisibilityTypes.PRIVATE:
            if authed():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return redirect(url_for("auth.login", next=request.full_path))

        elif v == ScoreVisibilityTypes.HIDDEN:
            if is_admin():
                return f(*args, **kwargs)
            else:
                if request.content_type == "application/json":
                    abort(403)
                else:
                    return (
                        render_template(
                            "errors/403.html", error="Scores are currently hidden"
                        ),
                        403,
                    )

        elif v == ScoreVisibilityTypes.ADMINS:
            if is_admin():
                return f(*args, **kwargs)
            else:
                abort(404)

    return _check_matrix_score_visibility


def load(app):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    template_path = os.path.join(dir_path, "scoreboard-matrix.html")
    override_template("scoreboard-matrix.html", open(template_path).read())

    matrix = Blueprint("matrix", __name__, static_folder="static")
    app.register_blueprint(matrix, url_prefix="/matrix")

    def get_standings():
        standings = scoreboard.get_standings()
        # TODO faster lookup here
        jstandings = []
        for team in standings:
            teamid = team[0]
            solves = db.session.query(Solves.challenge_id.label("challenge_id")).filter(
                Solves.team_id == teamid
            )
            freeze = utils.get_config("freeze")
            if freeze:
                freeze = unix_time_to_utc(freeze)
                if teamid != session.get("id"):
                    solves = solves.filter(Solves.date < freeze)
            solves = solves.all()
            jsolves = []
            for solve in solves:
                jsolves.append(solve.challenge_id)
            jstandings.append(
                {
                    "teamid": team[0],
                    "score": team[3],
                    "name": team[2],
                    "solves": jsolves,
                }
            )
        db.session.close()
        return jstandings

    def get_challenges():
        if not is_admin():
            if not ctftime():
                if view_after_ctf():
                    pass
                else:
                    return []
        if challenges_visible() and (ctf_started() or is_admin()):
            chals = (
                db.session.query(Challenges.id, Challenges.name, Challenges.category)
                .filter(or_(Challenges.state != "hidden", Challenges.state is None))
                .all()
            )
            jchals = []
            for x in chals:
                jchals.append({"id": x.id, "name": x.name, "category": x.category})

            # Sort into groups
            categories = set(map(lambda x: x["category"], jchals))
            jchals = [j for c in categories for j in jchals if j["category"] == c]
            return jchals
        return []

    def get_teams(force_on_site: bool = True):
        if not is_admin():
            if not ctftime():
                if view_after_ctf():
                    pass
                else:
                    return []
        on_site_field_name = "on-site Team"
        on_site_field_id = (
            db.session.query(Fields.id).filter(Fields.name == on_site_field_name).first()
        )
        if force_on_site and on_site_field_id:
            results = (
                db.session.query(Teams.name, TeamFieldEntries.value)
                .filter(
                    Teams.id == TeamFieldEntries.team_id,
                )
                .filter(TeamFieldEntries.field_id == on_site_field_id[0])
                .all()
            )
            results = [r for r in results if r.value == True]
        else:
            results = db.session.query(Teams).all()
        return [t.name for t in results]

    @app.route("/scoreboard-matrix", methods=["GET"])
    @check_matrix_score_visibility
    def scoreboard_matrix():
        force_on_site = bool(request.args.get("on_site", False))
        standings = get_standings()
        team_names = get_teams(force_on_site=force_on_site)
        if force_on_site:
            standings = [s for s in standings if s["name"] in team_names]
        return render_template(
            "scoreboard-matrix.html",
            standings=standings,
            score_frozen=is_scoreboard_frozen(),
            mode="users" if is_users_mode() else "teams",
            challenges=get_challenges(),
            theme=ctf_theme(),
        )

    # Deprecated on behalve of CTFd_scores_ctftime
    def scores():
        json = {"standings": []}
        if scores_visible() and not authed():
            return redirect(url_for("auth.login", next=request.path))
        if not scores_visible():
            return jsonify(json)

        standings = get_standings()

        for i, x in enumerate(standings):
            json["standings"].append(
                {
                    "pos": i + 1,
                    "id": x["name"],
                    "team": x["name"],
                    "score": int(x["score"]),
                    "solves": x["solves"],
                }
            )
        return jsonify(json)

    # app.view_functions["scoreboard.listing"] = scoreboard_view
    # app.view_functions['scoreboard.score'] = scores
    # Can be dependend on CTFd_scores_ctftime plugin

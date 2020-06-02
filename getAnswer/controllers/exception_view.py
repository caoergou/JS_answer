from flask import Blueprint, current_app, jsonify, request, session, url_for

from ..models import GlobalApiException

exception_view = Blueprint('exception', __name__)


@exception_view.app_errorhandler(GlobalApiException)
def api_exception(ex):
    return jsonify(ex.code_msg)

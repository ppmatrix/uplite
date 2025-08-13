"""Main views for UpLite application."""

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Home page - redirect to dashboard if logged in, otherwise show landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    return render_template('index.html')


@bp.route('/about')
def about():
    """About page."""
    return render_template('about.html')


@bp.route('/health')
def health():
    """Health check endpoint."""
    return {'status': 'ok', 'service': 'uplite'}, 200

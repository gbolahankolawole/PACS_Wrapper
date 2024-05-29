from flask import Blueprint, url_for


main_bp = Blueprint('main', __name__, url_prefix="")


#ROUTES
@main_bp.route('/')
async def home():
    info = f'''<h1>PACS Wrapper</h1>
    Visit the <a href="{url_for('pacs.doc')}">API documentation page</a> for the list of available endpoints'''

    return info



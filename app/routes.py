from flask import Blueprint
from flask_restx import Api

# LOCAL IMPORTS
from .api import studies_ns

pacs_bp = Blueprint('pacs', __name__, url_prefix="/api")
api_restx = Api(pacs_bp, doc='/doc', title='PACS Wrapper', 
          version='0.1', description='PACS Wrapper Documentation')

api_restx.add_namespace(studies_ns)



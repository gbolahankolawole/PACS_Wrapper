from flask_restx import fields

new_study_schema = {
    'server': fields.String,
    'dcm': fields.String
}

study_schema = {
    'server': fields.String
}



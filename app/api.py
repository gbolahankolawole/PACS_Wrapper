from flask_restx import Resource, Namespace

# LOCAL IMPORTS
from .pac_utils import send_file_to_pacs, retrieve_all, retrieve_metadata, delete_study
from .route_utils import responsify
from .schema import new_study_schema

studies_ns = Namespace('Studies', description='Studies related operations')


@studies_ns.route('')
class Study_Without_ID(Resource):   
    @studies_ns.expect(new_study_schema)
    def post(self):
        pacs_server = studies_ns.payload.get('server','microsoft')
        dcm_url = studies_ns.payload.get('dcm',None)
        pacs_status = send_file_to_pacs(dcm_url, pacs_server) if dcm_url else dcm_url #'/home/ubuntu/pacs/488365FB'
        return responsify(status=200, message='OK', data=pacs_status)
    
    def get(self):
        all_studies = []
        for pacs_server in ['dcm4chee', 'micosoft']:
            pacs_status = retrieve_all(pacs_server)
            if isinstance(pacs_status, list): all_studies + pacs_status

        return responsify(status=200, message='OK', data=all_studies)
    

@studies_ns.route('/<int:study_uid>')
class Study_With_ID(Resource):
    def get(self, study_uid):
        study_details = retrieve_metadata(study_uid, 'microsoft')
        is_not_found = study_details.get('error', None)
        if is_not_found:
            study_details = retrieve_metadata(study_uid, 'dcm4chee')

        return responsify(status=200, message='OK', data=study_details)
        
    
    def delete(self, study_uid):
        delete_response = delete_study(study_uid, 'microsoft')
        is_not_found = delete_response.get('error', None)
        if is_not_found:
            delete_response = delete_study(study_uid, 'dcm4chee')

        return responsify(status=200, message='OK', data=delete_response)
        
        




from flask import Flask, Response, request
from flask_cors import CORS
import requests
import json
from bs4 import BeautifulSoup
from urllib3.filepost import encode_multipart_formdata, choose_boundary

def responsify(status,message,data={}):
    code = int(status)
    a_dict = {"data":data,"message":message,"code":code}
    try:
        return Response(json.dumps(a_dict), status=code, mimetype='application/json')
    except:
        return Response(str(a_dict), status=code, mimetype='application/json')

app = Flask(__name__)
CORS(app)

metadata = {
    'patient': {'00080050': 'Accession Number',
        '00100010': 'Patient Name',
        '00100020': 'Patient ID',
        '00100030': 'Patient Birth Date',
        '00100040': 'Patient Sex',
        '00101010': 'Patient Age'},

    'modality': { '00080060': 'Modality',
                '00080070': 'Manufacturer',
                '00080080': 'Institution Name',
                '00080081': 'Institution Address',
                '00081010': 'Station Name',
                '00081070': 'Operator Name',
                '00081090': 'Manufacturer Model Name',
                '00181000': 'Device Serial Number',
                '00181020': 'Software Version(s)',
                '00181030': 'Protocol Name'},

    'study': {'00180015': 'Body Part Examined',
            '00080005': 'Specific Character Set',
            '00080008': 'Image Type',
            '00080016': 'SOP Class UID',
            '00080020': 'Study Date',
            '00080022': 'Acquisition Date',
            '00080030': 'Study Time',
            '00080032': 'Acquisition Time',
            '00081030': 'Study Description',
            '00080090': 'Referring Physician Name',
            '00081050': 'Performing Physician Name',
            '00200010': 'Study ID',
            '00200012': 'Acquisition Number',
            '00321060': 'Requested Procedure Description'},

    'series': {'00080021': 'Series Date',
            '00080031': 'Series Time',
            '0008103E': 'Series Description',
            '0020000E': 'Series Instance UID',
            '00200011': 'Series Number'},

    'instance': {'0020000D': 'Study Instance UID',
                '00080018': 'SOP Instance UID',
                '00080023': 'Content Date',
                '00080033': 'Content Time',
                '00082111': 'Derivation Description',
                '00200013': 'Instance Number',
                '00200032': 'Image Position (Patient)',
                '00200037': 'Image Orientation (Patient)',
                '00204000': 'Image Comments'}
}

meta_keys = {'00080020': 'Study Date',
  '00080030': 'Study Time',
  '00080050': 'Ascension Number',
  '00080090': 'Referring Physician Name',
  '00100010': 'Patient Name',
  '00100020': 'Patient ID',
  '00100030': 'Patient Birth Date',
  '00100040': 'Patient Sex',
  '0020000D': 'Study Instance UID',
  '00200010': 'Study ID'
}

META_REF = {}
for group in metadata:
    META_REF.update(metadata[group])

response_tags = {
    "00081150": "ReferencedSOPClassUID",
    "00081155": "ReferencedSOPInstanceUID",
    "00081190": "RetrieveURL",
    "00081196": "WarningReason",
    "00081198": "FailedSOPSequence",
    "00081197": "FailureReason",
    "00081199": "Referenced SOP Sequence"
    }

MS_failure_reasons = {
    '272':'The store transaction did not store the instance because of a general failure in processing the operation.',
    '43264':'The DICOM instance failed the validation.',
    '43265':'The provided instance StudyInstanceUID did not match the specified StudyInstanceUID in the store request.',
    '45070':'A DICOM instance with the same StudyInstanceUID, SeriesInstanceUID and SopInstanceUID has already been stored. If you wish to update the contents, delete this instance first.',
    '45071':'A DICOM instance is being created by another process, or the previous attempt to create has failed and the cleanup process has not had chance to clean up yet. Please delete the instance first before attempting to create again.'
    }

DCM_failure_reasons = {
    "42752 - 43007": "The Studies Store Transaction did not store the instance because it was out of resources.",
    "43264 - 43519": "The Studies Store Transaction did not store the instance because the instance does not conform to its specified SOP Class.",
    "49152 - 53247": "The Studies Store Transaction did not store the instance because it cannot understand certain Data Elements.",
    "49442": "The Studies Store Transaction did not store the instance because it does not support the requested Transfer Syntax for the instance.",
    "272": "The Studies Store Transaction did not store the instance because of a general failure in processing the operation.",
    "290": "The Studies Store Transaction did not store the instance because it does not support the requested SOP Class."
    }

DCM_warning_reasons = {
    "45056": "The Studies Store Transaction modified one or more data elements during storage of the instance",
    "45062": "The Studies Store Transaction discarded some data elements during storage of the instance.",
    "45063": "The Studies Store Transaction observed that the Data Set did not match the constraints of the SOP Class during storage of the instance."
    }

#HELPER FXNS
def select_server(pacs_server):
    available_pacs ={
        'microsoft' :'https://xcelsolutions-msdicom.azurewebsites.net/v1.0-prerelease',
        'dcm4chee':'http://20.185.24.194:8080/dcm4chee-arc/aets/DCM4CHEE/rs'
    }
    called_server = available_pacs[pacs_server] if pacs_server in available_pacs else available_pacs['microsoft']
    return called_server


def encode_multipart_related(fields, boundary=None):
    #The Requests library (and most Python libraries) do not work with multipart\related in a way that supports DICOMweb
    #add boundary to file to be pushed to pacs
    if boundary is None:
        boundary = choose_boundary()
    #print('INFO: encoding as multipart')
    body, _ = encode_multipart_formdata(fields, boundary)
    content_type = str('multipart/related; boundary=%s' % boundary)
    #print(content_type)
    return body, content_type

def prepare_file(filepath, pacs_server):
    #read in file
    '''
    with open(filepath,'rb') as reader:
        rawfile = reader.read()
    '''
    # download file data
    rawfile = requests.get(filepath).content

    files = {'file': ('dicomfile', rawfile, 'application/dicom')}
    #print('INFO: Preparing File')
    body, content_type = encode_multipart_related(fields = files)
    headers = {'Accept':'application/dicom+json', "Content-Type":content_type}
    if pacs_server == 'dcm4chee': headers['Accept'] = 'application/dicom+xml'

    return body, headers

def destructure_metadata(meta_value):
    destructured_meta = ''
    
    for val in meta_value:
        if type(val) == str: destructured_meta = destructured_meta + val
        elif type(val) == dict: destructured_meta = destructured_meta + val['Alphabetic']
        else: 
            if len(meta_value) == 1: destructured_meta = val
            else: destructured_meta = meta_value
            break
    #print(meta_value, '<= destructured =>', destructured_meta)
    return destructured_meta

#FXNS TO CREATE PAYLOADS
def create_studies_payload(pacs_response, pacs_server, filepath):
    payload = {}
    payload['status_code'] = pacs_response.status_code
    #print('INFO: ', payload['status_code'])
    #print('INFO: creating studies payload')
    if payload['status_code'] == 200:
        payload['payload'] = {}

        if pacs_server == 'dcm4chee':
            xml_parser = BeautifulSoup(pacs_response.text, 'xml')
            payload['payload']['ReferencedSOPClassUID'] = xml_parser.find('DicomAttribute', attrs ={'keyword':'ReferencedSOPClassUID'}).text
            payload['payload']['ReferencedSOPInstanceUID'] = xml_parser.find('DicomAttribute', attrs ={'keyword':'ReferencedSOPInstanceUID'}).text
            payload['payload']['RetrieveURL'] = xml_parser.find_all('DicomAttribute', attrs ={'keyword':"RetrieveURL"})[1].text
            
        else:
            pacs_json = pacs_response.json()
            payload['payload']['ReferencedSOPClassUID'] = pacs_json['00081199']['Value'][0]['00081150']['Value'][0]
            payload['payload']['ReferencedSOPInstanceUID'] = pacs_json['00081199']['Value'][0]['00081155']['Value'][0]
            payload['payload']['RetrieveURL'] = pacs_json['00081199']['Value'][0]['00081190']['Value'][0]

        payload['payload']['studyUID'] = payload['payload']['RetrieveURL'].split('studies')[1].split('/')[1]
        payload['payload']['seriesUID']  = payload['payload']['RetrieveURL'].split('series')[1].split('/')[1]
        payload['payload']['instanceUID']  = payload['payload']['RetrieveURL'].split('instances')[1].split('/')[1]

        # call metadata api and retrieve metadata
        metadata_payload = retrieve_metadata(payload['payload']['studyUID'], pacs_server)
        for metadata_key in metadata_payload:
            if metadata_key == 'status_code': continue
            payload['payload'][metadata_key] = metadata_payload[metadata_key]

    elif pacs_response.status_code == 500:
        # try again with dcm4chee
        if pacs_server == 'microsoft': 
            send_file_to_pacs(filepath, 'dcm4chee')
            return
        payload['error'] = pacs_response.text
    else:
        if pacs_server == 'dcm4chee':
            payload['error'] = pacs_response.text
        else:
            pacs_json = pacs_response.json()
            failure = pacs_json['00081198']['Value'][0]['00081197']['Value'][0]
            payload['error'] = MS_failure_reasons[str(failure)]

    return payload

def create_metadata_payload(pacs_response):
    payload = {}
    payload['status_code'] = pacs_response.status_code
    #print('INFO: ', payload['status_code'])
    #print('INFO: creating meta payload')    
    if payload['status_code'] == 200:
        pacs_json = pacs_response.json()[0]

        for metadata_key in metadata:
            payload[metadata_key] = {}
            #print('INFO: extracting ', metadata_key)
            for metadata_field in metadata[metadata_key]:
                #print('INFO: extracting ', metadata_field)
                if metadata_field in pacs_json:
                    root = pacs_json[metadata_field]
                    payload[metadata_key][META_REF[metadata_field]] = destructure_metadata(root['Value']) if 'Value' in root else None
                else:
                    payload[metadata_key][META_REF[metadata_field]] = None
    else:
        payload['error'] = pacs_response.text
    return payload

def create_studies_list_payload(pacs_response):
    payload = {}
    payload['status_code'] = pacs_response.status_code
    #print('INFO: ', payload['status_code'])
    #print('INFO: creating meta payload')    
    if payload['status_code'] == 200:
        pacs_json = pacs_response.json()
        payload['study_list'] = []

        for study_json in pacs_json:
            study_details = {}
            #print('INFO: extracting ', metadata_key)
            for metadata_key in meta_keys:
                #print('INFO: extracting ', metadata_field)
                if metadata_key in study_json:
                    root = study_json[metadata_key]
                    study_details[meta_keys[metadata_key]] = destructure_metadata(root['Value']) if 'Value' in root else None
                else:
                    study_details[meta_keys[metadata_key]]= None
            payload['study_list'].append(study_details)
    else:
        payload['error'] = pacs_response.text
    return payload

def create_delete_payload(pacs_response):
    payload = {}
    payload['status_code'] = pacs_response.status_code
    if payload['status_code'] == 204:
        payload['studies'] = pacs_response.text
    else:
        payload['error'] = pacs_response.text
    return payload


#FXNS THAT CALL PACS API
def retrieve_metadata(study_uid, pacs_server):
    BASE_URL = select_server(pacs_server)
    url = f'{BASE_URL}/studies/{study_uid}/metadata'
    headers = {"Accept": "application/dicom+json"}
    #print('INFO: retrieving metadata')
    client = requests.session()
    metadata_response = client.get(url, headers=headers, verify=False)
    metadata_payload = create_metadata_payload(metadata_response)

    return metadata_payload

def send_file_to_pacs(filepath, pacs_server):
    body, headers = prepare_file(filepath, pacs_server)
    BASE_URL = select_server(pacs_server)
    url = f'{BASE_URL}/studies'
    client = requests.session()
    #print('INFO: sending file to PACs')
    studies_response = client.post(url, body, headers=headers, verify=False)
    studies_payload = create_studies_payload(studies_response, pacs_server, filepath)

    return studies_payload

def retrieve_all(pacs_server):
    BASE_URL = select_server(pacs_server)
    url = f'{BASE_URL}/studies'
    headers = {"Accept": "application/dicom+json"}
    client = requests.session()
    s_response = client.get(url, headers=headers, verify=False)
    # print(s_response)
    studies_payload_list = create_studies_list_payload(s_response)

    return studies_payload_list

def delete_study(study_uid, pacs_server):
    BASE_URL = select_server(pacs_server)
    url = f'{BASE_URL}/studies/{study_uid}'
    client = requests.session()
    d_response = client.delete(url)
    delete_payload = create_delete_payload(d_response)

    return delete_payload

#ROUTES
# ['GET', 'POST', 'DELETE']
@app.route('/studies', methods = ['POST', 'GET'])
def studies():
    # print('im in')
    if request.method == 'POST':
        payload = request.get_json(force=True, silent=True)
        if payload:
            pacs_server = payload['server'] if 'server' in payload else 'microsoft'
            dcm_url = payload['dcm'] if 'dcm' in payload else None
        else: 
            pacs_server = 'microsoft'
            dcm_url = None
        pacs_server = payload['server'] if 'server' in payload else 'microsoft'
        pacs_status = send_file_to_pacs(dcm_url, pacs_server) if dcm_url else dcm_url #'/home/ubuntu/pacs/488365FB'
        return responsify(status=200, message='OK', data=pacs_status)
    
    elif request.method == 'GET':
        # print('getting lists studies')
        payload = request.get_json(force=True, silent=True)
        if payload:
            pacs_server = payload['server'] if 'server' in payload else 'microsoft'
        else: pacs_server = 'microsoft'
        pacs_status = retrieve_all(pacs_server)
        return responsify(status=200, message='OK', data=pacs_status)

@app.route('/studies/<study_uid>', methods = ['GET', 'DELETE'])
def study_details(study_uid):
    if request.method == 'GET':
        study_uid = str(study_uid)
        payload = request.get_json(force=True, silent=True)
        if payload:
            pacs_server = payload['server'] if 'server' in payload else 'microsoft'
        else: pacs_server = 'microsoft'
        study_details = retrieve_metadata(study_uid, pacs_server)
        return responsify(status=200, message='OK', data=study_details)

    elif request.method == 'DELETE':
        study_uid = str(study_uid)
        payload = request.get_json(force=True, silent=True)
        if payload:
            pacs_server = payload['server'] if 'server' in payload else 'microsoft'
        else: pacs_server = 'microsoft'
        delete_response = delete_study(study_uid, pacs_server)
        return responsify(status=200, message='OK', data=delete_response)

if __name__ == "__main__":
    app.run(host='localhost', port=11110, threaded=True)

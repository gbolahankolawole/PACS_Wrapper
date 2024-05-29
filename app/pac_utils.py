import requests
from urllib3.filepost import encode_multipart_formdata, choose_boundary
from bs4 import BeautifulSoup

# LOCAL IMPORTS
from .constants import metadata, meta_keys, MS_failure_reasons, META_REF

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




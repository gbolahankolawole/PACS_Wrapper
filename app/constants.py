

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




from rest_framework.exceptions import APIException


class DataNotProvided(APIException):
    status_code = 400
    default_detail = 'Please provide lyrics file or composition id.'


class CompositionException(APIException):
    status_code = 404
    default_detail = 'Given composition_id does not exist.'


class AlignmentException(APIException):
    status_code = 404
    default_detail = 'Given alignment_id does not exist.'

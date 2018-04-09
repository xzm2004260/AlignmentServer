from rest_framework.exceptions import APIException


class DataNotProvided(APIException):
    status_code = 404
    default_detail = 'Please provide lyrics file or composition id.'

from rest_framework.exceptions import APIException


class DataNotProvided(APIException):
    status_code = 400
    default_detail = 'Please provide lyrics file or composition id.'

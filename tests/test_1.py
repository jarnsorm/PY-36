from tests.config import SERVICE_URL
from tests.classes import Response

import requests


def test_connection():
    response = requests.get(SERVICE_URL)
    test_obj = Response(response)
    test_obj.assert_status(200)

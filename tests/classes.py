

class Response:
    def __init__(self, response):
        self.response = response
        self.response_status = response.status_code

    def assert_status(self, status_code):
        if isinstance(status_code, list):
            assert self.response_status in status_code, "wrong status code"
        else:
            assert self.response_status == status_code, "wrong status code"
        return self

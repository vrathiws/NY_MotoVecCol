import abc
import json
import urllib.request

class Comparator(abc.ABC):
    @abc.abstractmethod
    def equals(self, a, b):
        return

class StructComparator(Comparator):
    def equals(self, a, b):
        return a == b

class JsonComparator(Comparator):
    def __init__(self, delegate = StructComparator()):
        self.delegate = delegate

    def equals(self, a, b):
        if a == None or b == None:
            raise RuntimeError("Not a valid JSON string")
        
        if type(a) is not str or type(b) is not str:
            raise RuntimeError("Not a valid JSON string")

        try:
            a = json.loads(a)
            b = json.loads(b)

            return self.delegate.equals(a, b)
        except json.decoder.JSONDecodeError:
            raise RuntimeError("Not a valid JSON string")

class HttpClient:
    def get(self, url):
        return urllib.request.urlopen(url)

class HttpComparator(Comparator):
    def __init__(self, check_headers = True,
                    body_comparator = JsonComparator(), 
                    header_comparator = StructComparator(),
                    http_client = HttpClient()):

        self.body_comparator = body_comparator
        self.header_comparator = header_comparator
        self.client = http_client
        self.check_headers = check_headers

    def equals(self, a, b):
        if a == None or b == None:
            raise RuntimeError("Not a URL string")
        
        if type(a) is not str or type(b) is not str:
            raise RuntimeError("Not a URL string")

        try:
            a_response = self.client.get(a)
            b_response = self.client.get(b)
        except:
            raise RuntimeError("Cannot fetch API")

        if a_response.status != b_response.status:
            print("status diff")
            return False

        if self.check_headers:
            a_headers = dict(a_response.headers.items())
            b_headers = dict(b_response.headers.items())
            if not self.header_comparator.equals(a_headers, b_headers):
                return False

        try:
            a_body = a_response.read().decode("utf-8")
            b_body = b_response.read().decode("utf-8")
        except:
            raise RuntimeError("Cannot parse API response body")

        return self.body_comparator.equals(a_body, b_body)

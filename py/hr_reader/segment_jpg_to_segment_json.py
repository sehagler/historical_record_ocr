# Imports
from base64 import b64encode
from os.path import basename
import json
import requests

#
class segment_jpg_to_segment_json(object):
    
    #
    def __init__(self, gcv_url, api_key):
        
        #
        self._api_key = api_key
        self._gcv_url = gcv_url
    
    #
    def _make_image_data_request(self, filename):
        request = []
        with open(filename, 'rb') as f:
            ctxt = b64encode(f.read()).decode()
            request.append({
                    'image': {'content': ctxt},
                    'features': [{
                            'type': 'TEXT_DETECTION',
                            'maxResults': 1
                        }]
                })
        return request

    #
    def _make_image_data(self, filename):
        request = self._make_image_data_request(filename)
        return json.dumps({"requests": request }).encode()

    #
    def _request_ocr(self, filename):
        response = requests.post(self._gcv_url,
                                 data=self._make_image_data(filename),
                                 params={'key': self._api_key},
                                 headers={'Content-Type': 'application/json'})
        return response
    
    #
    def do_ocr(self, jpg_filename, json_filename):
        
        response = self._request_ocr(jpg_filename)
        if response.status_code != 200 or response.json().get('error'):
            print(response.text)
        else:
            with open(json_filename, 'w') as f:
                json_data = json.dumps(response.json()['responses'][0], indent=2)
                f.write(json_data)
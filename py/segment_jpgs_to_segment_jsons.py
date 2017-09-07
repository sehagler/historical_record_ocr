# Imports
from base64 import b64encode
from os.path import basename
import json
import requests

#
class segment_jpgs_to_segment_jsons(object):
    
    #
    def __init__(self, api_key):
        
        #
        self._api_key = api_key
        self._google_cloud_vision_url = \
            'https://vision.googleapis.com/v1/images:annotate'
    
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
        response = requests.post(self._google_cloud_vision_url,
                                 data=self._make_image_data(filename),
                                 params={'key': self._api_key},
                                 headers={'Content-Type': 'application/json'})
        return response
    
    #
    def do_ocr(self, segment_jpgs_dir, segment_jsons_dir, filename):
        
        filename = segment_jpgs_dir + filename
        
        response = self._request_ocr(filename)
        if response.status_code != 200 or response.json().get('error'):
            print(response.text)
        else:
            json_file = segment_jsons_dir + basename(filename[:len(filename)-4]) + '.json'
            with open(json_file, 'w') as f:
                json_data = json.dumps(response.json()['responses'][0], indent=2)
                f.write(json_data)
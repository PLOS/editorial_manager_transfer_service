import json, jsonpath, logging
from ..Config import API_BASE_HOST
from .base_json import BaseJSON

QUOTE_API = API_BASE_HOST + '/api/quote?cloudGuid={0}'
DEFAULT_HEADERS = {'Content-Type': 'application/json'}

class QuoteJSON(BaseJSON):
    def get_quote(self):
        guid = self.document.get('guid')
        self.doGet(QUOTE_API.format(guid))

    def verify_field(self, field_name):
        responce_value = jsonpath.jsonpath(self._json, ('$.{0}'.format(field_name)))[0]
        expected_value = self.manuscript_dict.get('quote').get(field_name)
        assert responce_value == expected_value, \
            'Value of {0} don\'t match. Actual: {1}, expected: {2}'.format(field_name, responce_value, expected_value)

    def get_field_value(self, field_name):
        return jsonpath.jsonpath(self._json, ('$.{0}'.format(field_name)))[0]




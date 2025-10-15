import json, pytest, jsonschema, requests, uuid
import logging

from ...Base.Config import EM_HOOK_HOST, em_user_name, em_user_password, client_id, client_secret
from .base_json import BaseJSON
from requests.structures import CaseInsensitiveDict

TOKEN_API = EM_HOOK_HOST + '/token'
NEW_MANUSCRIPT_API = EM_HOOK_HOST + '/manuscripts.json'
GET_MANUSCRIPT_API = EM_HOOK_HOST + '/publishers/PLOS/journals/{journal}/manuscripts.json?externalReferenceId='
UPDATE_MANUSCRIPT_API = EM_HOOK_HOST + '/manuscripts/{manuscript_id}.json'
DEFAULT_HEADERS = {'Content-Type': 'application/json'}
TEST_DATA_PATH = './api/TestData/'

class EmHookJSON(BaseJSON):
    def init_document(self, document_name, journal):
        super(EmHookJSON, self).init_document(document_name)
        self.document['journal'] = journal
        self.document['id'] = self.document.get('journal') + '-' + self.document.get('referenceId')

    def fetch_doc(self):
        pass

    def get_token(self, wrong_field = ''):
        form_data = {
            "username":  (None, em_user_name if not wrong_field == 'em_user_name' else em_user_name + '1'),
            "password":  (None, em_user_password if not wrong_field == 'em_user_password' else em_user_password + '1')
        }

        self.doPost(TOKEN_API, files = form_data,
                    user = client_id if not wrong_field == 'client_id' else client_id + '1',
                    password = client_secret if not wrong_field == 'client_secret' else client_secret + '1')

        if not pytest.if_token_only:
            self.verify_response_code(200)
            self.parse_response_as_json()

    def post_new_manuscript(self):
        self.delete_doc()

        with open(TEST_DATA_PATH + self.document.get('docFile'), 'r') as f:
            manuscript_body = f.read()

        manuscript_body = manuscript_body.replace('{MANUSCRIPT_ID}', self.document.get('referenceId'))
        manuscript_body = manuscript_body.replace('{MANUSCRIPT_JOURNAL}', self.document.get('journal'))
        pytest.test_field_uuid = str(uuid.uuid4())
        manuscript_body = manuscript_body.replace('{TEST_FIELD}', pytest.test_field_uuid)
        self.parse_token()

        self._response = requests.post(NEW_MANUSCRIPT_API, data = manuscript_body, headers = self._bearer_headers )

    def update_manuscript(self, updateMethod):
        with open(TEST_DATA_PATH + self.document.get('docFile'), 'r') as f:
            manuscript_body = f.read()

        update_manuscript_api = UPDATE_MANUSCRIPT_API.replace('{manuscript_id}', self.document.get('id'))
        manuscript_body = manuscript_body.replace('{MANUSCRIPT_ID}', self.document.get('referenceId'))
        manuscript_body = manuscript_body.replace('{MANUSCRIPT_JOURNAL}', self.document.get('journal'))
        pytest.test_field_uuid = str(uuid.uuid4())
        manuscript_body = manuscript_body.replace('{TEST_FIELD}', pytest.test_field_uuid)
        self.parse_token()

        if updateMethod == 'POST':
            self._response = requests.post(update_manuscript_api, data = manuscript_body, headers = self._bearer_headers )
        elif updateMethod == 'PUT':
            self._response = requests.put(update_manuscript_api, data = manuscript_body, headers = self._bearer_headers )
        else:
            assert False, 'You passed not supported HTTP method ' + updateMethod

    def get_manuscript(self):
        get_manuscript_api = GET_MANUSCRIPT_API.replace('{journal}', self.document.get('journal'))
        get_manuscript_api += self.document.get('referenceId')
        self.parse_token()

        self._response = requests.get(get_manuscript_api, headers = self._bearer_headers)

    def verify_schema(self):
        if pytest.if_token_only:
            fileName = 'tokenSchema.json'
        else:
            fileName = self.document.get('schemaFile')

        with open(TEST_DATA_PATH + fileName, 'r') as f:
            schema = json.load(f)

        validator = jsonschema.Draft7Validator(schema)
        errors = validator.iter_errors(self._json)

        errorMessage = ''

        for error in sorted(errors, key=lambda e: e.path):
            errorMessage += str(error.absolute_schema_path) + ' ==> ' + error.message + '\n'

        assert len(errorMessage) == 0, errorMessage

    def verify_manuscript_data(self):
        if hasattr(pytest, 'test_field_uuid'):
            test_field_value = pytest.test_field_uuid
            del pytest.test_field_uuid
        else:
            super().fetch_doc()
            firestore_em_data = self.manuscript_dict.get('emData')
            assert 'testField' in firestore_em_data.keys(), 'testField node is not present in FireStore'
            test_field_value = firestore_em_data.get('testField')

        em_data = self._json.get('emData')

        assert 'testField' in em_data.keys(), 'testField node is not present in JSON response'
        actual_value = em_data.get('testField')
        assert actual_value == test_field_value, \
            'testField value is wrong in JSON response. Expected: {0}, Actual:{1}'.format(test_field_value, actual_value)

    def parse_token(self):
        self.token = self.get_json_field_value('$.access_token')

        if hasattr(pytest, 'if_wrong_token') and pytest.if_wrong_token:
            auth_header = 'Bearer ' + self.token + '1'
            del pytest.if_wrong_token
        else:
            auth_header = 'Bearer ' + self.token

        self._bearer_headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }









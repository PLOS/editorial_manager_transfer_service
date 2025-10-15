import json, jsonpath, logging
from urllib.parse import urlparse
from google.cloud import firestore
from plos_test.BaseServiceEndpoint import BaseServiceEndpoint
from ..resources import documents
from ..Config import firestore_project_ic, firestore_collection_name

class BaseJSON(BaseServiceEndpoint):

    def init_document(self, document_name):
        self.document = [x for x in documents if x.get('name') == document_name][0]

    def _get_db_collection(self, collection_name):
        """Return an instance of a firestore db collection for querying"""
        db = firestore.Client(project=firestore_project_ic)
        return db.collection(collection_name)

    def _query_firestore(self, document_id):
        """Queries firestore for the document id. Done so we can easily mock it."""
        db_collection = self._get_db_collection(firestore_collection_name)
        return db_collection.document(document_id).get()

    def update_doc(self, field_dict):
        document_id = self.document.get('id')
        manuscript = self._query_firestore(document_id)
        if manuscript.exists:
            db_collection = self._get_db_collection(firestore_collection_name)
            db_collection.document(document_id).update(field_dict)

    def delete_doc(self):
        document_id = self.document.get('id')
        manuscript = self._query_firestore(document_id)
        if manuscript.exists:
            db_collection = self._get_db_collection(firestore_collection_name)
            db_collection.document(document_id).delete()

    def fetch_doc(self):
        """Fetch a document from firestore"""
        document_id = self.document.get('id')
        manuscript = self._query_firestore(document_id)
        if not manuscript.exists:
            # Manuscript doesn't exist in the billing system, send a 404.
            raise Exception(
                f"{document_id} not found in collection {firestore_collection_name}"
            )
        self.manuscript_dict = manuscript.to_dict()

        # with open("my_dict.json", "w") as json_file:
        #     json.dump(self.manuscript_dict , json_file, indent=4, sort_keys=True, default=str)

    def query_doc(self, cloud_guid):
        collection = self._get_db_collection(firestore_collection_name)
        query = collection.where('cloudGuid', '==', cloud_guid).limit(1)
        docs = query.stream()
        manuscript = next(docs, None)
        if not manuscript.exists:
            raise Exception(
                f"{cloud_guid} not found in collection {firestore_collection_name}"
            )
        self.manuscript_dict = manuscript.to_dict()

    def verify_manuscript_field(self, field, expected_value):
        return self.manuscript_dict.get(field) == expected_value

    def parse_response_as_json(self):
        try:
            self._json = json.loads(self.get_http_response().text)
        except Exception as e:
            logging.info('Error while trying to parse response as JSON!')
            logging.info('Actual response was: "{0}"'.format(self.get_http_response().text))
            raise e

    def get_json_field_value(self, path):
        return jsonpath.jsonpath(self._json, path)[0]

    def verify_response_code(self, code):
        response = self.get_http_response()
        assert response.status_code == int(code), \
            'Wrong Status Code. Expected: {0}, Actual: {1}. Response Body: {2}'.format(code, response.status_code, response.text)

    def verify_response_body_text(self, text):
        response = self.get_http_response()
        assert text in response.text, \
            'Wrong Response Body Text. Expected to have: "{0}", Actual: "{1}"'.format(text, response.text)

    def verify_response_body_text_desnt_have(self, text):
        response = self.get_http_response()
        assert not text.lower() in response.text.lower(), \
            'Wrong Response Body Text. Expected not to have: "{0}", Actual: "{1}"'.format(text, response.text)

    def is_valid_url(self, url):
        try:
            parsed_url = urlparse(url)
            # Check if the URL has both a scheme (e.g., "http") and a network location (e.g., "www.google.com")
            return bool(parsed_url.scheme) and bool(parsed_url.netloc)
        except:
            return False

import datetime,pytest
from ...Base.Config import API_BASE_HOST
from .base_json import BaseJSON

ACCEPT_CHARGES_API = API_BASE_HOST + '/api/accept-charges?cloudGuid={0}'
DEFAULT_HEADERS = {'Content-Type': 'application/json'}

class AcceptChargesJSON(BaseJSON):
    def set_doc_status_to_quote(self):
        self.update_doc({'quote.status': 'requested'})

    def save_modified_date(self):
        self.fetch_doc()
        pytest.old_modified_date = self.manuscript_dict.get('modified')

    def post_accept_charges(self):
        guid = self.document.get('guid')
        self.doPost(ACCEPT_CHARGES_API.format(guid))

    def verify_modified_date(self):
        modified_date = self.manuscript_dict.get('modified')
        assert pytest.old_modified_date != modified_date, 'Modified date wasn\'t updated'

    def verify_quote_status(self):
        status = self.manuscript_dict.get('quote').get('status')
        assert status == 'accepted',  \
            'Value of {0} don\'t match. Actual: {1}, expected: {2}'.format('quote.status', status, 'accepted')

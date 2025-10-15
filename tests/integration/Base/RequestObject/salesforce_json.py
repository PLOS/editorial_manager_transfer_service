import json, pytest, requests, uuid
import logging

from ...Base.Config import salesforce_credentials
from .base_json import BaseJSON
from ..Config import pfa_email

TOKEN_API = 'https://test.salesforce.com/services/oauth2/token'
QUERY_API = '/services/data/v58.0/query/?q='
DEFAULT_HEADERS = {'Content-Type': 'application/json'}

class SaleseForceJSON(BaseJSON):
    def __init__(self, journal, cloud_guid):
        self.cloud_guid = cloud_guid
        self.journal = journal

        self.query_doc(cloud_guid)

        self.document_id = self.manuscript_dict.get('emData').get('externalReferenceId')

    def get_access_token(self):
        form_data = {
            "grant_type":  (None, 'password'),
            "client_id":  (None, salesforce_credentials['client_id']),
            "client_secret":  (None, salesforce_credentials['client_secret']),
            "username":  (None, salesforce_credentials['username']),
            "password":  (None, salesforce_credentials['password'] + salesforce_credentials['token']),
        }

        self.doPost(TOKEN_API, files = form_data)

        self.verify_response_code(200)
        self.parse_response_as_json()
        self.parse_token_respnse()

    def query_cases(self):
        query = "SELECT Id, CaseNumber, Subject, Document_ID__c, Journal_Code__c, SuppliedEmail, PFA_Able_to_Pay_R__c, " \
                "Supporting_Document_Link__c  FROM Case where Journal_Code__c = '{}'  and Document_ID__c = " \
                "'{}' LIMIT 1".format(self.journal, self.document_id)
        get_manuscript_api = self._sf_base_url  + QUERY_API + query

        self._BaseServiceEndpoint__response = requests.get(get_manuscript_api, headers = self._bearer_headers)

        self.verify_response_code(200)
        self.parse_response_as_json()

    def verify_case(self, expected_able_to_page):
        case_number = self.get_json_field_value('$.records[0].CaseNumber')
        file_url = self.get_json_field_value('$.records[0].Supporting_Document_Link__c')
        email = self.get_json_field_value('$.records[0].SuppliedEmail')
        able_to_pay = self.get_json_field_value('$.records[0].PFA_Able_to_Pay_R__c')

        assert case_number.isdigit(), f'Case number {case_number} in not integer'
        assert self.is_valid_url(file_url), f'Case file url {file_url} in not a valid url'
        assert email == pfa_email, f'Case email {email} is not equal to expected email {pfa_email}'
        assert able_to_pay == expected_able_to_page, f'Case able to pay {able_to_pay} is not equal to ' \
                                                     f'expected able to pay {expected_able_to_page}'


    def parse_token_respnse(self):
        self.token = self.get_json_field_value('$.access_token')

        auth_header = 'Bearer ' + self.token

        self._bearer_headers = {
            'Authorization': auth_header,
            'Content-Type': 'application/json'
        }

        self._sf_base_url = self.get_json_field_value('$.instance_url')

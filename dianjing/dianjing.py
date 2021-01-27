'''A lightweight wrapper for the 360 dianjing API'''
import os
import hashlib
import requests
from Crypto.Cipher import AES

API_KEY = os.environ['360_API_KEY']
API_SECRET = os.environ['360_API_SECRET']

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 ' \
             '(KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

Q360_ACCESS_TOKEN_URL = 'https://api.e.360.cn/account/clientLogin'


class Q360Base:
    '''Session object'''
    def __init__(self, account=None, encrypted_pwd=None, password=None, access_token=None):
        self.account = account
        self.encrypted_pwd = encrypted_pwd
        self.password = password
        self.access_token = access_token
        self._check_pwd()

    def _check_pwd(self):

        if not self.encrypted_pwd:
            self._create_encrypted_pwd()
        else:
            print('Could not encrypt password.')

        return True

    def _create_encrypted_pwd(self):

        origin_pwd = self.password
        m_5 = hashlib.md5()
        m_5.update(origin_pwd)
        md5_pwd = m_5.hexdigest()

        crypt_object = AES.new(
            key=str.encode(API_SECRET)[:16],
            mode=AES.MODE_CBC,
            IV=str.encode(API_SECRET)[16:]
            )
        encrypted_text = crypt_object.encrypt(str.encode(md5_pwd))
        encrypted_pwd = encrypted_text.hex()

        self.encrypted_pwd = encrypted_pwd
        return True

    def _get_access_token(self):

        headers = dict()
        headers['User-Agent'] = USER_AGENT
        headers['apiKey'] = API_KEY

        data = dict(
            format='json',
            username=self.account,
            passwd=self.encrypted_pwd
            )
        req = requests.post(Q360_ACCESS_TOKEN_URL, data=data, verify=True, headers=headers)
        if req.status_code != 200:
            return False

        self.access_token = req.json().get('accessToken', '')
        return self.access_token

    def _cycle_base_report_pages(self, url, headers, start, end, device='all'):
        responses = []
        page = 1
        while page:
            data = dict(
                format='json',
            	type=device,
                ad_type='base_report',
                startDate=start,
                endDate=end,
                page=page
                )
            req = requests.post(url, data=data, verify=True, headers=headers)
            json_response = req.json()
            data = json_response.get(list(json_response.keys())[0])
            if data:
                responses.append(data)
                page += 1
            else:
                break
        return responses

    '''Returns a campaign report.'''
    def get_campaign_report(self, start, end, device='all'):
        campaign_url = 'https://api.e.360.cn/dianjing/report/campaign'
        headers = self._get_360_headers()
        responses = self._cycle_base_report_pages(
            url=campaign_url,
            headers=headers,
            start=start,
            end=end,
            device=device
            )
        return responses

    '''Returns a dictionary of regions and their ids.'''
    def get_region_dict(self):
        region_url = 'https://api.e.360.cn/dianjing/tool/area'
        headers = self._get_360_headers()
        req = requests.post(region_url, verify=True, headers=headers)
        json_response = req.json().get('area')
        return json_response

    '''Returns a fengwu report.'''
    def get_fengwu_report(self, start, end):
        fengwu_url = 'https://api.e.360.cn/dianjing/report/fengwu'
        headers = self._get_360_headers()
        responses = self._cycle_base_report_pages(
            url=fengwu_url,
            headers=headers,
            start=start,
            end=end
            )
        return responses

    '''Returns a fengwu now report.'''
    def get_fengwu_now_report(self):
        fengwu_now_url = 'https://api.e.360.cn/dianjing/report/fengwuNow'
        headers = self._get_360_headers()
        data = dict(
            format='json',
        	type='all',
            ad_type='base_report',
            page=1
            )
        req = requests.post(fengwu_now_url, data=data, verify=True, headers=headers)
        json_response = req.json()
        return json_response.get(list(json_response.keys())[0])

    '''Returns a region report.'''
    def get_region_report(self, start, end):
        region_url = 'https://api.e.360.cn/dianjing/report/region'
        headers = self._get_360_headers()
        responses = self._cycle_base_report_pages(
            url=region_url,
            headers=headers,
            start=start,
            end=end
            )
        return responses

    def _get_360_headers(self):

        if not self.access_token:
            access_token = self._get_access_token()
            if not access_token:
                print('FAILED TO RETRIEVE ACCESS TOKEN')
                return False
        else:
            access_token = self.access_token

        headers = dict()
        headers['User-Agent'] = USER_AGENT
        headers['accessToken'] = access_token
        headers['apiKey'] = API_KEY

        return headers


if __name__ == '__main__':
    pass

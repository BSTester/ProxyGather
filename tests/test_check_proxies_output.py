import json
import os
import sys
import tempfile
import types
import unittest

fake_proxy_checker_module = types.ModuleType("checker.proxy_checker")
fake_proxy_checker_module.ProxyChecker = object
sys.modules.setdefault("checker.proxy_checker", fake_proxy_checker_module)

import CheckProxies


class SaveWorkingProxiesTests(unittest.TestCase):
    def test_country_json_uses_rest_api_payload(self):
        proxy_data = {'all': {'1.1.1.1:80', '2.2.2.2:80'}, 'http': {'1.1.1.1:80', '2.2.2.2:80'}, 'socks4': set(), 'socks5': set()}
        country_proxy_data = {
            'US': {
                'name': 'United States of America (the)',
                'protocols': {'all': {'1.1.1.1:80', '2.2.2.2:80'}, 'http': {'1.1.1.1:80', '2.2.2.2:80'}, 'socks4': set(), 'socks5': set()}
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            CheckProxies._save_working_proxies(
                proxy_data,
                prepend_protocol=False,
                output_base=os.path.join(temp_dir, 'proxies', 'working-proxies.txt'),
                is_final=True,
                country_proxy_data=country_proxy_data
            )

            json_path = os.path.join(temp_dir, 'proxies', 'by-country', 'US', 'working-proxies-http.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()

            self.assertTrue(content.startswith('{'))
            self.assertFalse(content.startswith('['))

            payload = json.loads(content)
            self.assertEqual(
                payload,
                {
                    'proxies': [
                        {
                            'proxy': '1.1.1.1:80',
                            'protocol': 'http',
                            'country_code': 'US',
                            'country': 'United States of America (the)'
                        },
                        {
                            'proxy': '2.2.2.2:80',
                            'protocol': 'http',
                            'country_code': 'US',
                            'country': 'United States of America (the)'
                        }
                    ]
                }
            )

    def test_save_working_proxies_writes_country_lists_and_index(self):
        proxy_data = {
            'all': {'1.1.1.1:80', '2.2.2.2:1080'},
            'http': {'1.1.1.1:80'},
            'socks4': set(),
            'socks5': {'2.2.2.2:1080'}
        }
        country_proxy_data = {
            'US': {
                'name': 'United States',
                'protocols': {
                    'all': {'1.1.1.1:80'},
                    'http': {'1.1.1.1:80'},
                    'socks4': set(),
                    'socks5': set()
                }
            },
            'DE': {
                'name': 'Germany',
                'protocols': {
                    'all': {'2.2.2.2:1080'},
                    'http': set(),
                    'socks4': set(),
                    'socks5': {'2.2.2.2:1080'}
                }
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_base = os.path.join(temp_dir, 'proxies', 'working-proxies.txt')
            CheckProxies._save_working_proxies(
                proxy_data,
                prepend_protocol=True,
                output_base=output_base,
                is_final=True,
                country_proxy_data=country_proxy_data
            )

            with open(os.path.join(temp_dir, 'proxies', 'working-proxies-all.txt'), 'r', encoding='utf-8') as f:
                self.assertEqual(f.read().splitlines(), ['1.1.1.1:80', '2.2.2.2:1080'])

            with open(os.path.join(temp_dir, 'proxies', 'working-proxies-http.txt'), 'r', encoding='utf-8') as f:
                self.assertEqual(f.read().splitlines(), ['http://1.1.1.1:80'])

            with open(os.path.join(temp_dir, 'proxies', 'by-country', 'DE', 'working-proxies-socks5.txt'), 'r', encoding='utf-8') as f:
                self.assertEqual(f.read().splitlines(), ['socks5://2.2.2.2:1080'])

            with open(os.path.join(temp_dir, 'proxies', 'by-country', 'DE', 'working-proxies-socks5.json'), 'r', encoding='utf-8') as f:
                self.assertEqual(
                    json.load(f),
                    {
                        'proxies': [{
                            'proxy': '2.2.2.2:1080',
                            'protocol': 'socks5',
                            'country_code': 'DE',
                            'country': 'Germany'
                        }]
                    }
                )

            with open(os.path.join(temp_dir, 'proxies', 'by-country', 'index.json'), 'r', encoding='utf-8') as f:
                self.assertEqual(
                    json.load(f),
                    [
                        {'country': 'Germany', 'country_code': 'DE', 'protocols': ['all', 'socks5']},
                        {'country': 'United States', 'country_code': 'US', 'protocols': ['all', 'http']}
                    ]
                )

    def test_save_working_proxies_clears_stale_country_files(self):
        proxy_data = {'all': {'1.1.1.1:80'}, 'http': {'1.1.1.1:80'}, 'socks4': set(), 'socks5': set()}
        country_proxy_data = {
            'US': {
                'name': 'United States',
                'protocols': {'all': {'1.1.1.1:80'}, 'http': {'1.1.1.1:80'}, 'socks4': set(), 'socks5': set()}
            }
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            stale_dir = os.path.join(temp_dir, 'proxies', 'by-country', 'ZZ')
            os.makedirs(stale_dir, exist_ok=True)
            with open(os.path.join(stale_dir, 'working-proxies-http.txt'), 'w', encoding='utf-8') as f:
                f.write('old-proxy\n')

            CheckProxies._save_working_proxies(
                proxy_data,
                prepend_protocol=False,
                output_base=os.path.join(temp_dir, 'proxies', 'working-proxies.txt'),
                is_final=True,
                country_proxy_data=country_proxy_data
            )

            self.assertFalse(os.path.exists(stale_dir))

    def test_save_working_proxies_removes_stale_protocol_files_when_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            output_base = os.path.join(temp_dir, 'proxies', 'working-proxies.txt')
            os.makedirs(os.path.dirname(output_base), exist_ok=True)

            stale_file = os.path.join(temp_dir, 'proxies', 'working-proxies-http.txt')
            with open(stale_file, 'w', encoding='utf-8') as f:
                f.write('old-proxy\n')

            CheckProxies._save_working_proxies(
                {'all': set(), 'http': set(), 'socks4': set(), 'socks5': set()},
                prepend_protocol=False,
                output_base=output_base,
                is_final=True,
                country_proxy_data={}
            )

            self.assertFalse(os.path.exists(stale_file))
            with open(os.path.join(temp_dir, 'proxies', 'by-country', 'index.json'), 'r', encoding='utf-8') as f:
                self.assertEqual(json.load(f), [])


if __name__ == '__main__':
    unittest.main()

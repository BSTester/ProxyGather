import json
import os
import subprocess
import sys
import tempfile
import unittest


class UpdateReadmeCountryListsTests(unittest.TestCase):
    def test_script_renders_country_links_into_readme(self):
        repo_root = '/home/runner/work/ProxyGather/ProxyGather'
        script_path = os.path.join(repo_root, 'scripts', 'update_readme_country_lists.py')

        with tempfile.TemporaryDirectory() as temp_dir:
            readme_path = os.path.join(temp_dir, 'README.md')
            index_path = os.path.join(temp_dir, 'proxies', 'by-country', 'index.json')
            os.makedirs(os.path.dirname(index_path), exist_ok=True)

            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(
                    "Before\n"
                    "<!-- country-proxy-lists:start -->\n"
                    "old\n"
                    "<!-- country-proxy-lists:end -->\n"
                    "After\n"
                )

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(
                    [
                        {'country': 'United States', 'country_code': 'US', 'protocols': ['all', 'http']},
                        {'country': 'Germany', 'country_code': 'DE', 'protocols': ['all', 'socks5']}
                    ],
                    f
                )

            subprocess.run(
                [
                    sys.executable,
                    script_path,
                    '--readme', readme_path,
                    '--country-index', index_path,
                    '--repository', 'BSTester/ProxyGather',
                    '--branch', 'master'
                ],
                check=True
            )

            with open(readme_path, 'r', encoding='utf-8') as f:
                updated = f.read()

            self.assertIn("* **Germany (DE)**", updated)
            self.assertIn(
                "https://raw.githubusercontent.com/BSTester/ProxyGather/refs/heads/master/proxies/by-country/DE/working-proxies-socks5.txt",
                updated
            )
            self.assertIn("* **United States (US)**", updated)
            self.assertLess(updated.index("* **Germany (DE)**"), updated.index("* **United States (US)**"))


if __name__ == '__main__':
    unittest.main()

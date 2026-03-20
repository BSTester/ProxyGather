import pathlib
import subprocess
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


class GitIgnoreCountryJsonTests(unittest.TestCase):
    def test_country_json_outputs_are_committable(self):
        for output_path in (
            'proxies/by-country/US/working-proxies-http.json',
            'proxies/by-country/DE/working-proxies-socks5.json',
            'proxies/by-country/JP/working-proxies-all.json',
        ):
            with self.subTest(output_path=output_path):
                result = subprocess.run(
                    ['git', 'check-ignore', '-v', output_path],
                    cwd=REPO_ROOT,
                    check=False,
                    capture_output=True,
                    text=True
                )

                self.assertIn(
                    '!/proxies/by-country/*/*.json',
                    result.stdout,
                    'Country JSON outputs must be explicitly unignored, or GitHub Actions cannot commit them.'
                )


if __name__ == '__main__':
    unittest.main()

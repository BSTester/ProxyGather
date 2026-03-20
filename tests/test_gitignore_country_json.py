import pathlib
import subprocess
import unittest


REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]


class GitIgnoreCountryJsonTests(unittest.TestCase):
    def test_country_json_outputs_are_not_ignored(self):
        result = subprocess.run(
            ['git', 'check-ignore', '-v', 'proxies/by-country/US/working-proxies-http.json'],
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

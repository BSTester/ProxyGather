import argparse
import json
import os

START_MARKER = "<!-- country-proxy-lists:start -->"
END_MARKER = "<!-- country-proxy-lists:end -->"
PROTOCOL_LABELS = {
    'all': 'All Protocols',
    'http': 'HTTP',
    'socks4': 'SOCKS4',
    'socks5': 'SOCKS5'
}

def load_country_index(index_path):
    if not os.path.exists(index_path):
        return []

    with open(index_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return sorted(
        data,
        key=lambda item: ((item.get('country') or '').lower(), item.get('country_code') or '')
    )

def build_country_list_markdown(countries, repository, branch):
    if not countries:
        return "_No country-specific proxy lists are available yet. The next successful workflow run will populate this section._"

    lines = []
    for country in countries:
        country_name = country.get('country') or country.get('country_code') or 'Unknown'
        country_code = (country.get('country_code') or '').upper()
        protocols = country.get('protocols') or []
        lines.append(f"* **{country_name} ({country_code})**")
        for protocol in protocols:
            label = PROTOCOL_LABELS.get(protocol, protocol.upper())
            url = f"https://raw.githubusercontent.com/{repository}/refs/heads/{branch}/proxies/by-country/{country_code}/working-proxies-{protocol}.txt"
            lines.append(f"  * {label}: `{url}`")
    return "\n".join(lines)

def update_readme(readme_path, rendered_section):
    with open(readme_path, 'r', encoding='utf-8') as f:
        readme = f.read()

    if START_MARKER not in readme or END_MARKER not in readme:
        raise ValueError("README markers for country proxy lists were not found.")

    start = readme.index(START_MARKER) + len(START_MARKER)
    end = readme.index(END_MARKER)
    updated = readme[:start] + "\n" + rendered_section + "\n" + readme[end:]

    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated)

def main():
    parser = argparse.ArgumentParser(description="Update the README country proxy list section.")
    parser.add_argument('--readme', required=True, help='Path to README.md')
    parser.add_argument('--country-index', required=True, help='Path to proxies/by-country/index.json')
    parser.add_argument('--repository', required=True, help='GitHub repository in owner/name format')
    parser.add_argument('--branch', required=True, help='Git branch used for raw links')
    args = parser.parse_args()

    countries = load_country_index(args.country_index)
    rendered_section = build_country_list_markdown(countries, args.repository, args.branch)
    update_readme(args.readme, rendered_section)

if __name__ == "__main__":
    main()

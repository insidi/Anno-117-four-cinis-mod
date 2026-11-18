"""Publish a checked tag from GitHub Actions; credentials stay in environment/memory."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def publish(tag, commit):
    repository = os.environ['GITHUB_REPOSITORY']
    credential = os.environ['GH_TOKEN']
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', repository):
        raise ValueError('Invalid repository')
    api = 'https://api.github.com/repos/' + repository

    def request(url, method='GET', payload=None, content_type='application/json'):
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != 'https' or parsed.hostname not in ('api.github.com', 'uploads.github.com'):
            raise ValueError('Unexpected API destination')
        if not parsed.path.startswith('/repos/' + repository + '/'):
            raise ValueError('Unexpected repository destination')
        data = payload if isinstance(payload, bytes) else json.dumps(payload).encode('utf-8') if payload is not None else None
        req = urllib.request.Request(url, data=data, method=method, headers={
            'Authorization': 'Bearer ' + credential, 'Accept': 'application/vnd.github+json',
            'Content-Type': content_type, 'User-Agent': 'Four-Cinis-release',
            'X-GitHub-Api-Version': '2026-03-10',
        })
        try:
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.load(response)
        except urllib.error.HTTPError as error:
            details = json.loads(error.read().decode('utf-8'))
            raise RuntimeError(f'GitHub HTTP {error.code}: {details.get("message", "request failed")}') from None

    metadata = json.loads((ROOT / 'config/modinfo.json').read_text(encoding='utf-8'))
    version = metadata['Version']
    if tag != 'v' + version or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Release tag must match the mod version')
    settings = json.loads((ROOT / 'config/release.json').read_text(encoding='utf-8'))
    prerelease = settings['release_prerelease']
    if type(prerelease) is not bool:
        raise ValueError('Explicit boolean release_prerelease required')
    notes = (ROOT / f'docs/RELEASE-{version}.md').read_text(encoding='utf-8')
    files = [ROOT / f'dist/cinis-four-directions-{tag}.zip', ROOT / f'dist/cinis-four-directions-{tag}.zip.sha256']
    checksum = hashlib.sha256(files[0].read_bytes()).hexdigest()
    build = json.loads((ROOT / f'dist/build-{tag}.json').read_text(encoding='utf-8'))
    tests = json.loads((ROOT / f'dist/tests-{tag}.json').read_text(encoding='utf-8'))
    if any(r['version'] != version or r['zip_sha256'] != checksum for r in (build, tests)) or tests['result'] != 'PASS':
        raise ValueError('Build/test reports do not match the release ZIP')
    if files[1].read_text().strip() != checksum + '  ' + files[0].name:
        raise ValueError('Checksum file does not match the release ZIP')
    reference = request(api + '/git/ref/tags/' + tag)['object']
    for _ in range(5):
        if reference['type'] != 'tag':
            break
        reference = request(api + '/git/tags/' + reference['sha'])['object']
    if reference['type'] != 'commit' or reference['sha'] != commit:
        raise ValueError('Remote tag does not point at the checked commit')
    # Never replace a published release or retry by overwriting a draft.
    for page in range(1, 101):
        releases = request(api + f'/releases?per_page=100&page={page}')
        if any(r['tag_name'] == tag for r in releases):
            raise ValueError('Release already exists; inspect it instead of overwriting it')
        if len(releases) < 100:
            break
    else:
        raise ValueError('Could not finish checking existing releases')
    release = request(api + '/releases', 'POST', {
        'tag_name': tag, 'name': tag + ' - Vier Cinis: aktualisierte Baugrenzen',
        'body': notes, 'draft': True, 'prerelease': prerelease,
    })
    uploaded = []
    for path in files:
        data = path.read_bytes()
        url = release['upload_url'].split('{', 1)[0] + '?' + urllib.parse.urlencode({'name': path.name})
        asset = request(url, 'POST', data, 'application/zip' if path.suffix == '.zip' else 'text/plain')
        if asset['size'] != len(data) or asset.get('digest') != 'sha256:' + hashlib.sha256(data).hexdigest() or asset['state'] != 'uploaded':
            raise RuntimeError('Asset verification failed; release remains a draft: ' + path.name)
        uploaded.append(asset['name'])
    request(api + '/releases/' + str(release['id']), 'PATCH',
            {'draft': False, 'make_latest': 'false' if prerelease else 'true'})
    verified = request(api + '/releases/tags/' + tag)
    if verified['draft'] or verified['prerelease'] != prerelease or sorted(a['name'] for a in verified['assets']) != sorted(uploaded):
        raise RuntimeError('Published release verification failed')
    print(json.dumps({'release': verified['html_url'], 'tag': tag, 'commit': commit, 'prerelease': prerelease,
                      'assets': [{k: a[k] for k in ('name', 'size', 'digest', 'browser_download_url')} for a in verified['assets']]}, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--commit', required=True)
    args = parser.parse_args()
    publish(args.tag, args.commit)

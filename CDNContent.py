

import json
import re
from urllib.request import Request, urlopen

from sublime import load_settings


# This dictionary stores the CDN providers handled as long as their API link.
CDNPROVIDERS = {
    'cdnjs.cloudflare.com':
        'https://api.cdnjs.com/libraries?search={name}&fields=version',
    'maxcdn.bootstrapcdn.com':
        'https://api.github.com/repos/{owner}/{name}/tags',
    'code.jquery.com':
        'https://api.github.com/repos/{owner}/{name}/tags'
}

# This regex has been written by @sindresorhus for Semver.
# (https://github.com/sindresorhus/semver-regex)
SEMVER_REGEX = 'v?(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[\da-z-]+(?:\.[\da-z-]+)*)?(?:\+[\da-z-]+(?:\.[\da-z-]+)*)?'


# Simple object to store a CDN element (Sublime.Region + Urllib.ParseResult)
class CDNContent():
    def __init__(self, region, parsedResult):
        self.sublimeRegion = region
        self.parsedResult = parsedResult

        # This variable will store a status as the ones below :
        # ('up_to_date', 'to_update', 'not_found')
        self.status = None

        # We load the settings file to retrieve a GitHub API token afterwards.
        self.settings = load_settings('Preferences.sublime-settings')

    def handleProvider(self):
        # CDNJS.com will be handled here.
        if self.parsedResult.netloc == 'cdnjs.cloudflare.com':
            # We temporally store the result of the path split around '/'.
            # The library name will be in `[3]`, and its version in `[4]`.
            tmp = self.parsedResult.path.split('/')

            # We ask CDNJS API to retrieve information about this library.
            # We use the API link specified within `CDNPROVIDERS` and...
            # ... format it with the `name` of the library.
            request = urlopen(
                CDNPROVIDERS[self.parsedResult.netloc].format(name=tmp[3])
            )

            # If the request was a success...
            if request.getcode() == 200:
                # ... we fetch and decode the data from the payload
                data = json.loads(request.read().decode())

                # If there is at least one result, which matches our library...
                if data['total'] >= 1 and data['results'][0]['name'] == tmp[3]:
                    # ... let's compare its version with ours !
                    if data['results'][0]['version'] == tmp[4]:
                        self.status = 'up_to_date'

                    else:
                        self.status = 'to_update'

                else:
                    self.status = 'not_found'

            else:
                print('CDNUpdates: You should check your Internet connection.')

        elif self.parsedResult.netloc == 'maxcdn.bootstrapcdn.com':
            name = None
            tmp = self.parsedResult.path.split('/')

            if tmp[1] == 'bootstrap':
                owner = 'twbs'

            elif tmp[1] == 'font-awesome':
                owner, name = 'FortAwesome', 'Font-Awesome'

            elif tmp[1] == 'bootlint':
                owner = 'twbs'

            elif tmp[1] == 'bootswatch':
                owner = 'thomaspark'

            else:
                # We don't know such a content delivered by BOOTSTRAPCDN.COM...
                self.status = 'not_found'
                return

            # We ask directly the GitHub API for the latest tag name.
            request = urlopen(Request(
                CDNPROVIDERS[self.parsedResult.netloc].format(
                    owner=owner,
                    name=name or tmp[1]),
                headers={
                    'Authorization': 'token ' + self.settings.get('github_api')
                } if self.settings.get('github_api') else {}
            ))

            if request.getcode() == 200:
                data = json.loads(request.read().decode())

                if len(data) >= 1 and data[0]['name'].lstrip('v') == tmp[2]:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                print('CDNUpdates: You should check your Internet connection.')

        elif self.parsedResult.netloc == 'code.jquery.com':
            tmp = self.parsedResult.path.split('/')

            if tmp[1].startswith('jquery'):
                name = 'jquery'
                version = re.search(SEMVER_REGEX, tmp[1]).group(0)

            elif tmp[1] in ['ui', 'mobile', 'color']:
                name = 'jquery-' + tmp[1]
                version = tmp[2]

            elif tmp[1] == 'qunit':
                name = 'qunit'
                version = re.search(SEMVER_REGEX, tmp[2]).group(0)

            elif tmp[1] == 'pep':
                name = 'PEP'
                version = tmp[2]

            else:
                self.status = 'not_found'
                return

            request = urlopen(Request(
                CDNPROVIDERS[self.parsedResult.netloc].format(
                    # Only `QUnit` belongs to another organization.
                    owner=('qunitjs' if name == 'qunit' else 'jquery'),
                    name=name),
                headers={
                    'Authorization': 'token ' + self.settings.get('github_api')
                } if self.settings.get('github_api') else {}
            ))

            if request.getcode() == 200:
                data = json.loads(request.read().decode())

                if len(data) >= 1 and data[0]['name'].lstrip('v') == version:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                print('CDNUpdates: You should check your Internet connection.')

        elif False:
            # Additional CDN providers will have to be handled there
            pass

        else:
            print('CDNUpdates: This statement should not be reached.')

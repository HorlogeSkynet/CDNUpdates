

import json
import re
from urllib.request import Request, urlopen

from sublime import active_window, load_settings


# This dictionary stores the CDN providers handled as long as their API link.
CDNPROVIDERS = [
    'cdnjs.cloudflare.com',
    'maxcdn.bootstrapcdn.com',
    'code.jquery.com',
    'ajax.googleapis.com',
    'cdn.jsdelivr.net'
]

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
        """
        This is the most important method of CDNUpdates.
        This is where are comparing the versions in function of the provider...
        ... and their different formatting conventions.
        """

        # CDNJS.com will be handled here.
        if self.parsedResult.netloc == 'cdnjs.cloudflare.com':
            # We temporally store the result of the path split around '/'.
            # The library name will be in `[3]`, and its version in `[4]`.
            tmp = self.parsedResult.path.split('/')

            # We ask CDNJS API to retrieve information about this library.
            request = urlopen(
                'https://api.cdnjs.com/libraries?search={name}&fields=version'
                .format(name=tmp[3])
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
                self.status = 'not_found'
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

            self.getLatestTagFromGitHub(owner, name or tmp[1], tmp[2])

        # CDN from CODE.JQUERY.COM will be handled here.
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

            self.getLatestTagFromGitHub(
                # Only `QUnit` belongs to another organization.
                ('qunitjs' if name == 'qunit' else 'jquery'),
                name,
                version
            )

        # CDN from AJAX.GOOGLEAPIS.COM will be handled here.
        elif self.parsedResult.netloc == 'ajax.googleapis.com':
            tmp = self.parsedResult.path.split('/')

            # The CDNs provided by Google are well "formatted".
            # This dictionary will only store the "correspondences" with...
            # ... GitHub repositories.
            CORRESPONDENCES = {
                'dojo': {'owner': 'dojo', 'name': 'dojo'},
                'ext-core': {'owner': 'ExtCore', 'name': 'ExtCore'},
                'hammerjs': {'owner': 'hammerjs', 'name': 'hammer.js'},
                'indefinite-observable': {
                    'owner': 'material-motion',
                    'name':  'indefinite-observable-js'
                },
                'jquery':       {'owner': 'jquery', 'name': 'jquery'},
                'jquerymobile': {'owner': 'jquery', 'name': 'jquery-mobile'},
                'jqueryui':     {'owner': 'jquery', 'name': 'jquery-ui'},
                'mootools': {'owner': 'mootools', 'name': 'mootools-core'},
                'myanmar-tools': {
                    'owner': 'googlei18n',
                    'name': 'myanmar-tools'
                },
                'prototype': {'owner': 'sstephenson', 'name': 'prototype'},
                'scriptaculous': {
                    'owner': 'madrobby',
                    'name': 'scriptaculous'
                },
                'shaka-player': {'owner': 'google', 'name': 'shaka-player'},
                'spf': {'owner': 'youtube', 'name': 'spfjs'},
                'swfobject': {'owner': 'swfobject', 'name': 'swfobject'},
                'threejs': {'owner': 'mrdoob', 'name': 'three.js'},
                'webfont': {'owner': 'typekit', 'name': 'webfontloader'}
            }

            if tmp[3] not in CORRESPONDENCES.keys():
                self.status = 'not_found'
                return

            else:
                self.getLatestTagFromGitHub(
                    CORRESPONDENCES.get(tmp[3])['owner'],
                    CORRESPONDENCES.get(tmp[3])['name'],
                    tmp[4]
                )

        # CDN from CDN.JSDLIVR.NET will be handled here.
        elif self.parsedResult.netloc == 'cdn.jsdelivr.net':
            """
            The API from JSDLIVR is powerful. It implies we compute a
              "fuzzy" version checking (ex: 'jquery@3' is OK for '3.2.1')
            """
            tmp = self.parsedResult.path.split('/')

            try:
                if tmp[1] == 'npm':
                    name, version = tmp[2].split('@')
                    self.getLatestTagFromNPMSJ(name, version)

                elif tmp[1] == 'gh':
                    name, version = tmp[3].split('@')
                    self.getLatestTagFromGitHub(tmp[2], name, version,
                                                fuzzyCheck=True)

                elif tmp[1] == 'wp':
                    # This how we'll handle the latest version references, as :
                    # (https://cdn.jsdelivr.net/wp/wp-slimstat/trunk/wp-slimstat.js)
                    if len(tmp) < 6:
                        raise IndexError

                    self.getLatestTagFromWPSVN(tmp[2], tmp[4])

                else:
                    self.status = 'not_found'

            except (ValueError, IndexError):
                # This statement is here to handle `split()` errors.
                #
                # This page looks using a CDN without specifying a version.
                # Let's inform the user !
                self.status = 'to_update'

                # We'll log something on the console, let's open it !
                if active_window().active_panel() != 'console':
                    active_window().run_command(
                        'show_panel', {'panel': 'console', 'toggle': True}
                    )

                print('CDNUpdates: You should always specify a version for'
                      ' your CDN in production. ({})'.format(
                            self.parsedResult.geturl()))

        elif False:
            # Additional CDN providers will have to be handled there
            pass

        else:
            print('CDNUpdates: This statement should not be reached.')

    def getLatestTagFromGitHub(self, owner, name, version, fuzzyCheck=False):
        """
        This method fetches tags from the `owner/name` repository on GitHub...
        ... and compares it with `version`.
        `self.status` will be set according to the previous comparison.
        """
        request = urlopen(Request(
            'https://api.github.com/repos/{owner}/{name}/tags'.format(
                owner=owner,
                name=name),
            headers={
                'Authorization': 'token ' + self.settings.get('github_api')
            } if self.settings.get('github_api') else {}
        ))

        if request.getcode() == 200:
            data = json.loads(request.read().decode())

            if len(data) >= 1:
                if (not fuzzyCheck and data[0]['name'].lstrip('v') == version)\
                        or data[0]['name'].find(version, 0) == 0:

                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                # Should not be reached (GitHub issue or repository moved ?).
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            print('CDNUpdates: You should check your Internet connection.')

    def getLatestTagFromNPMSJ(self, name, version):
        request = urlopen(Request(
            'https://api.npms.io/v2/search?q={name}'.format(name=name),
            # The API of NPMJS blocks the scripts, we need to spoof a real UA.
            headers={
                'User-Agent': 'Mozilla/5.0(X11; U; Linux i686) '
                              'Gecko/20071127 Firefox/2.0.0.11'
            }
        ))

        if request.getcode() == 200:
            data = json.loads(request.read().decode())

            if data['total'] >= 1 and \
                    data['results'][0]['package']['name'] == name and \
                    data['results']['score']['searchScore'] >= 100000:

                # "Fuzzy" version checking below !
                if data['results'][0]['package']['version'].find(version, 0) \
                        == 0:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            print('CDNUpdates: You should check your Internet connection.')

    def getLatestTagFromWPSVN(self, name, version):
        request = urlopen(
            'https://plugins.svn.wordpress.org/{name}/tags/'.format(name=name),
        )

        if request.getcode() == 200:
            # A f*cked-up one-liner to retrieve the latest version from SVN...
            data = re.findall('<li><a href=\".*\">(.*)<\/a><\/li>',
                              request.read().decode())

            if len(data) >= 1:
                if data[-1].rstrip('/') == version:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            print('CDNUpdates: You should check your Internet connection.')

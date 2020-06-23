"""CDNUpdates' main logic"""

import json
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from sublime import load_settings

from .CDNConstants import (
    AJAX_GOOGLE_APIS_CORRESPONDENCES,
    AJAX_MICROSOFT_CORRESPONDENCES,
    CDN_STATIC_FILE_CORRESPONDENCES,
    MAXCDN_BOOTSTRAP_CORRESPONDENCES,
    OPENSOURCE_KEYCDN_CORRESPONDENCES,
    SEMVER_REGEXP_OBJECT
)
from .CDNUtils import log_message


class CDNContent:
    """
    This class run verifies whether found CDN are up to date.
    Checks (try to) rely on the CDN provider's API, or on GitHub directly.
    It also stores the results (Sublime.Region + Urllib.ParseResult) for future usages.
    """

    def __init__(self, region, parsed_result):
        self.sublime_region = region
        self.parsed_result = parsed_result

        # This variable will store a status as the ones below :
        # ('up_to_date', 'to_update', 'not_found')
        self.status = None

        # These variables will store the final information of this CDN.
        self.name = None
        self.latest_version = None

        # We load the settings file to retrieve a GitHub API token afterwards.
        self.settings = load_settings('CDNUpdates.sublime-settings')

    def handle_provider(self):  # pylint: disable=too-many-statements, too-many-return-statements, too-many-branches
        """
        This is the most important method of CDNUpdates.
        This is where are comparing the versions in function of the provider...
        ... and their different formatting conventions.
        """

        # CDNJS.com will be handled here.
        if self.parsed_result.netloc == 'cdnjs.cloudflare.com':
            # We temporally store the result of the path split around '/'.
            # The library name will be in `[3]`, and its version in `[4]`.
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[3]

            self.compare_with_latest_cdnjs_version(self.name, tmp[4])

        elif self.parsed_result.netloc == 'maxcdn.bootstrapcdn.com':
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[1]
            if self.name not in MAXCDN_BOOTSTRAP_CORRESPONDENCES.keys():
                log_message("{0} is not known to be delivered by this provider.".format(self.name))
                self.status = 'not_found'
                return

            self.compare_with_latest_github_tag(
                MAXCDN_BOOTSTRAP_CORRESPONDENCES.get(self.name)['owner'],
                MAXCDN_BOOTSTRAP_CORRESPONDENCES.get(self.name)['name'],
                tmp[2]
            )

        # CDN from CODE.JQUERY.COM will be handled here.
        elif self.parsed_result.netloc == 'code.jquery.com':
            tmp = self.parsed_result.path.split('/')

            if tmp[1].startswith('jquery'):
                self.name = 'jquery'
                version = SEMVER_REGEXP_OBJECT.search(tmp[1])
                version = version and version.group(0)
            elif tmp[1] in ['ui', 'mobile', 'color']:
                self.name = 'jquery-' + tmp[1]
                version = tmp[2]
            elif tmp[1] == 'qunit':
                self.name = 'qunit'
                version = SEMVER_REGEXP_OBJECT.search(tmp[2])
                version = version and version.group(0)
            elif tmp[1] == 'pep':
                self.name = 'PEP'
                version = tmp[2]
            else:
                version = None

            if not version:
                self.status = 'not_found'
                return

            self.compare_with_latest_github_tag(
                # Only `QUnit` belongs to another organization.
                ('qunitjs' if self.name == 'qunit' else 'jquery'),
                self.name,
                version
            )

        # CDN from AJAX.GOOGLEAPIS.COM will be handled here.
        elif self.parsed_result.netloc == 'ajax.googleapis.com':
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[3]
            if self.name not in AJAX_GOOGLE_APIS_CORRESPONDENCES.keys():
                self.status = 'not_found'
                return

            self.compare_with_latest_github_tag(
                AJAX_GOOGLE_APIS_CORRESPONDENCES.get(self.name)['owner'],
                AJAX_GOOGLE_APIS_CORRESPONDENCES.get(self.name)['name'],
                tmp[4]
            )

        # CDN from CDN.JSDLIVR.NET will be handled here.
        elif self.parsed_result.netloc == 'cdn.jsdelivr.net':
            # The API from JSDLIVR is powerful.
            # It implies we compute a "fuzzy" version checking.
            # For instance : "jquery@3" is OK for '3.2.1'.
            tmp = self.parsed_result.path.split('/')

            try:
                if tmp[1] == 'npm':
                    self.name, version = tmp[2].split('@')
                    self.compare_with_npmjs_version(self.name, version)

                elif tmp[1] == 'gh':
                    self.name, version = tmp[3].split('@')
                    self.compare_with_latest_github_tag(
                        tmp[2], self.name, version,
                        fuzzy_check=True
                    )

                elif tmp[1] == 'wp':
                    # This how we'll handle the latest version references, as :
                    # <https://cdn.jsdelivr.net/wp/wp-slimstat/trunk/wp-slimstat.js>
                    if len(tmp) < 6:
                        raise IndexError

                    self.name = tmp[2]
                    self.compare_with_latest_wpsvn_tag(self.name, tmp[4])

                else:
                    self.status = 'not_found'

            except (ValueError, IndexError):
                # This statement is here to handle `split()` errors.
                # This page seems using a CDN without specifying a version.
                self.status = 'to_update'

        # CDN from (CDN.)?RAWGIT.COM will be handled here.
        elif self.parsed_result.netloc in 'cdn.rawgit.com':
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[2]

            # If no semantic version is specified in the URL, we assume either:
            # * The developer uses the latest version available (`master`) [OR]
            # * The developer knows what he is doing (commit hash specified)
            if not SEMVER_REGEXP_OBJECT.search(tmp[3]):
                self.status = 'up_to_date'
            else:
                # If not, we compare this version with the latest tag !
                self.compare_with_latest_github_tag(tmp[1], self.name, tmp[3])

        elif self.parsed_result.netloc == 'code.ionicframework.com':
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[1]
            self.compare_with_latest_github_release('ionic-team', self.name, tmp[2])

        elif self.parsed_result.netloc == 'use.fontawesome.com':
            self.name = 'Font Awesome'

            # We assume here that FA's CDN always serves the latest version.
            self.status = 'up_to_date'

        elif self.parsed_result.netloc == 'opensource.keycdn.com':
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[1]
            if self.name not in OPENSOURCE_KEYCDN_CORRESPONDENCES.keys():
                log_message("{0} is currently not handled for this provider.".format(self.name))
                self.status = 'not_found'
                return

            self.compare_with_latest_github_tag(
                OPENSOURCE_KEYCDN_CORRESPONDENCES.get(self.name)['owner'],
                OPENSOURCE_KEYCDN_CORRESPONDENCES.get(self.name)['name'],
                tmp[2]
            )

        elif self.parsed_result.netloc == 'cdn.staticfile.org':
            tmp = self.parsed_result.path.split('/')
            self.name = tmp[1]
            if self.name not in CDN_STATIC_FILE_CORRESPONDENCES.keys():
                log_message("{0} is currently not handled for this provider.".format(self.name))
                self.status = 'not_found'
                return

            self.compare_with_latest_github_tag(
                CDN_STATIC_FILE_CORRESPONDENCES.get(self.name)['owner'],
                CDN_STATIC_FILE_CORRESPONDENCES.get(self.name)['name'],
                tmp[2]
            )

        elif self.parsed_result.netloc in ['ajax.microsoft.com', 'ajax.aspnetcdn.com']:
            tmp = self.parsed_result.path.split('/')

            # Sometimes the version is in the path...
            if len(tmp) == 5:
                version = tmp[3]
            # ... and some other times contained within the name.
            else:
                version = SEMVER_REGEXP_OBJECT.search(tmp[3])
                version = version and version.group(0)

            if tmp[2] not in AJAX_MICROSOFT_CORRESPONDENCES.keys() or not version:
                self.status = 'not_found'
                return

            self.name = tmp[2]
            self.compare_with_latest_github_tag(
                AJAX_MICROSOFT_CORRESPONDENCES.get(tmp[2])['owner'],
                AJAX_MICROSOFT_CORRESPONDENCES.get(tmp[2])['name'],
                version,
                # Microsoft has tagged some libraries very badly...
                # Check `CDNConstants.AJAX_MICROSOFT_CORRESPONDENCES` for this entry.
                AJAX_MICROSOFT_CORRESPONDENCES.get(tmp[2]).get('fuzzy_check', False)
            )

        elif self.parsed_result.netloc == 'cdn.ckeditor.com':
            tmp = self.parsed_result.path.split('/')

            if tmp[1] == 'ckeditor5' and \
               tmp[3] in ['classic', 'inline', 'balloon']:
                self.name = "{0} ({1})".format(tmp[1], tmp[3])
                self.compare_with_latest_github_release('ckeditor', tmp[1], tmp[2])

            else:
                self.status = 'not_found'
                return

        # Additional CDN providers may be handled there.

        else:
            log_message("This statement should not be reached.")

    def compare_with_latest_cdnjs_version(self, name, version):
        """This method handles call and result comparison with the CDNJS' API"""

        # We ask CDNJS API to retrieve information about this library.
        request = urlopen(
            "https://api.cdnjs.com/libraries?search={name}&fields=version".format(
                name=quote(name)
            )
        )

        # If the request was a success...
        if request.getcode() == 200:
            # ... we fetch and decode the data from the payload.
            data = json.loads(request.read().decode())

            # We iterate on the results until we encounter a matching name.
            for result in data['results']:
                if result['name'] == name:
                    # We set here its name and version for future usages.
                    self.latest_version = result['version']

                    # ... let's compare its version with ours !
                    if self.latest_version == version:
                        self.status = 'up_to_date'

                    else:
                        self.status = 'to_update'

                    break

            else:
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            log_message(
                "The HTTP response was not successful for \"{}\" ({}).".format(
                    request.geturl(),
                    request.getcode()
                )
            )

    def compare_with_latest_github_tag(
            self,
            owner, name, version,
            fuzzy_check=False):
        """
        This method fetches tags from the `owner/name` repository on GitHub...
        ... and compares it with `version`.
        `self.status` will be set according to the previous comparison.
        """
        request = urlopen(Request(
            "https://api.github.com/repos/{owner}/{name}/tags".format(
                owner=quote(owner),
                name=quote(name)),
            headers={
                'Authorization': "token {}".format(self.settings.get('github_api_token'))
            } if self.settings.get('github_api_token') else {}
        ))

        if request.getcode() == 200:
            data = json.loads(request.read().decode())
            if len(data) >= 1:
                self.latest_version = data[0]['name'].lstrip('v')
                if (not fuzzy_check and self.latest_version == version) \
                        or self.latest_version.lower().find(version.lower(), 0) == 0:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                # Should not be reached (GitHub issue or repository moved ?).
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            log_message(
                "The HTTP response was not successful for \"{}\" ({}).".format(
                    request.geturl(),
                    request.getcode()
                )
            )

    def compare_with_latest_github_release(
            self,
            owner, name, version,
            fuzzy_check=False):
        """
        This method fetches the latest release from the `owner/name`...
        ... repository on GitHub and compares it with `version`.
        `self.status` will be set according to the previous comparison.
        """
        request = urlopen(Request(
            'https://api.github.com/repos/{owner}/{name}/releases/latest'
            .format(
                owner=quote(owner),
                name=quote(name)
            ),
            headers={
                'Authorization': 'token ' + self.settings.get('github_api_token')
            } if self.settings.get('github_api_token') else {}
        ))

        if request.getcode() == 200:
            data = json.loads(request.read().decode())

            self.latest_version = data['tag_name'].lstrip('v')
            if (not fuzzy_check and self.latest_version == version) \
                    or self.latest_version.lower().find(version.lower(), 0) == 0:
                self.status = 'up_to_date'

            else:
                self.status = 'to_update'

        else:
            self.status = 'not_found'
            log_message(
                "The HTTP response was not successful for \"{}\" ({}).".format(
                    request.geturl(),
                    request.getcode()
                )
            )

    def compare_with_npmjs_version(self, name, version):
        """This method handles call and result comparison with the NPMJS' API"""
        request = urlopen(Request(
            "https://api.npms.io/v2/search?q={name}".format(name=quote(name)),
            headers={  # The API of NPMJS blocks scripts, we need to spoof a real UA.
                'User-Agent': "Mozilla/5.0(X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"
            }
        ))

        if request.getcode() == 200:
            data = json.loads(request.read().decode())
            if data['total'] >= 1 and \
                    data['results'][0]['package']['name'] == name and \
                    data['results'][0]['searchScore'] >= 100000:
                self.latest_version = data['results'][0]['package']['version']

                # "Fuzzy" version checking below !
                if self.latest_version.find(version, 0) == 0:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            log_message(
                "The HTTP response was not successful for \"{}\" ({}).".format(
                    request.geturl(),
                    request.getcode()
                )
            )

    def compare_with_latest_wpsvn_tag(self, name, version):
        """This method parses HTML from WordPress' SVN plugin page to retrieve the latest tag"""
        request = urlopen(
            "https://plugins.svn.wordpress.org/{name}/tags/".format(
                name=quote(name)
            )
        )

        if request.getcode() == 200:
            # A f*cked-up one-liner to retrieve the latest version from SVN...
            data = re.findall(
                r"<li><a href=\".*\">(.*)<\/a><\/li>",
                request.read().decode()
            )
            if len(data) >= 1:
                self.latest_version = data[-1].rstrip('/')

                if self.latest_version == version:
                    self.status = 'up_to_date'

                else:
                    self.status = 'to_update'

            else:
                self.status = 'not_found'

        else:
            self.status = 'not_found'
            log_message(
                "The HTTP response was not successful for \"{}\" ({}).".format(
                    request.geturl(),
                    request.getcode()
                )
            )

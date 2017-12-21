

import json
from urllib.request import urlopen


# This dictionary stores the CDN providers handled as long as their API link.
CDNPROVIDERS = {
    'cdnjs.cloudflare.com':
        'https://api.cdnjs.com/libraries?search={name}&fields=version',
    'maxcdn.bootstrapcdn.com':
        'https://api.github.com/repos/{owner}/{name}/tags'
}


# Simple object to store a CDN element (Sublime.Region + Urllib.ParseResult)
class CDNContent():
    def __init__(self, region, parsedResult):
        self.sublimeRegion = region
        self.parsedResult = parsedResult
        self.status = None

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
            request = urlopen(
                CDNPROVIDERS[self.parsedResult.netloc].format(
                    owner=owner,
                    name=name or tmp[1])
            )

            if request.getcode() == 200:
                data = json.loads(request.read().decode())

                if len(data) >= 1 and data[0]['name'].lstrip('v') == tmp[2]:
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



import json
from urllib.request import urlopen


# This dictionary stores the CDN providers handled as long as their API link.
CDNPROVIDERS = {
    'cdnjs.cloudflare.com':
        'https://api.cdnjs.com/libraries?search={name}&fields=version'
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
                CDNPROVIDERS[self.parsedResult.netloc].format(name=tmp[3]))

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

        elif False:
            # Additional CDN providers will have to be handled there
            pass

        else:
            print('CDNUpdates: This statement should not be reached.')

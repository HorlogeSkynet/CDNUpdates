

from urllib.parse import urlparse

from .CDNContent import CDNContent, CDNPROVIDERS
from .CDNUtils import log_message


class CheckForCDNProviders():
    def __init__(self, view, cdnContentList, regionList):
        self.view = view
        self.cdnContentList = cdnContentList
        self.regionList = regionList

        """
        Simple method to filter out the regions containing a link not handled.
        """
        for region in self.regionList:
            # We parse the URL taken from that region...
            parsedResult = urlparse(
                self.view.substr(region)
            )

            # ... to check if it's a known CDN provider.
            if parsedResult.netloc in CDNPROVIDERS:
                # If this matches, we store it and move on to the next element.
                self.cdnContentList.append(CDNContent(region, parsedResult))

            # If not, we'll just ignore this region in the future.
            else:
                log_message(
                    '\"{0}\" has been detected, but won\'t be handled here.'
                    .format(parsedResult.netloc)
                )

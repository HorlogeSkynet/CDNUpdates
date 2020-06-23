"""CDNUpdates' CDN providers verification"""

from urllib.parse import urlparse

from .CDNContent import CDNContent
from .CDNConstants import CDN_PROVIDERS
from .CDNUtils import log_message


class CheckForCDNProviders:  # pylint: disable=too-few-public-methods
    """
    A simple class to verify that the links found within the view are handled by the plugin.
    """

    def __init__(self, view, cdn_content_list, region_list):
        """Simple method to filter out the regions containing a link not handled"""
        self.view = view
        self.cdn_content_list = cdn_content_list
        self.region_list = region_list

        for region in self.region_list:
            # We parse the URL taken from that region...
            parsed_result = urlparse(self.view.substr(region))

            # ... to check if it's a known CDN provider.
            if parsed_result.netloc in CDN_PROVIDERS:
                # If this matches, we store it and move on to the next element.
                self.cdn_content_list.append(CDNContent(region, parsed_result))

            # If not, we'll just ignore this region in the future.
            else:
                log_message(
                    "\"{0}\" has been detected, but won\'t be handled here.".format(
                        parsed_result.netloc
                    )
                )

"""CDNUpdates' links finder"""

from sublime import IGNORECASE

from .CDNUtils import LINK_REGEX


class CheckForLinks:  # pylint: disable=too-few-public-methods
    """
    A simple class to gather the links present within the view.
    """

    def __init__(self, view, region_list):
        """This method gathers URLs present within the sheet calling this plugin"""
        self.view = view
        self.region_list = region_list

        for region in self.view.find_all(LINK_REGEX, IGNORECASE):
            # We have to fill the list directly (passed by reference)
            self.region_list.append(region)



from sublime import IGNORECASE

from .CDNUtils import LINK_REGEX


class CheckForLinks():
    def __init__(self, view, regionList):
        """
        This method gathers URLs present within the sheet calling this plugin.
        """

        self.view = view
        self.regionList = regionList

        for region in self.view.find_all(LINK_REGEX, IGNORECASE):

            # We have to fill the list directly (passed by reference)
            self.regionList.append(region)

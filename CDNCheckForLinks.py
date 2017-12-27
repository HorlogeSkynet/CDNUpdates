
from sublime import IGNORECASE


class CheckForLinks():
    def __init__(self, view, regionList):
        self.view = view
        self.regionList = regionList

        """
        This method gathers URLs present within the sheet calling this plugin.
        """
        # This is a regex written by @diegoperini, Python ported by @adamrofer.
        # (https://gist.github.com/dperini/729294)
        # It is tweaked to work with network path references and HTML tags.
        for region in self.view.find_all(
                    '(?:(https?:)?//)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S[^\"\s]*)?',
                    IGNORECASE
                ):

            # We have to fill the list directly (passed by reference)
            self.regionList.append(region)


import os
from urllib.parse import urlparse

from CDNUpdates.CDNContent import CDNContent, CDNPROVIDERS

from sublime import DRAW_EMPTY_AS_OVERWRITE, DRAW_NO_FILL, DRAW_NO_OUTLINE, \
    DRAW_SOLID_UNDERLINE
from sublime import IGNORECASE, active_window, message_dialog

from sublime_plugin import EventListener, TextCommand


class CDNUpdatesCommand(TextCommand):
    def run(self, edit):
        """
        Main function, only handling statuses and calling other methods
        """
        self.regionList = []
        self.cdnContentList = []

        if self.view.is_loading():
            message_dialog('This file is not loaded yet.')
            return

        self.view.set_status(
            'checking_link',
            'Checking this sheet for links...'
        )

        self.check_for_links()

        self.view.erase_status('checking_link')
        self.view.set_status(
            'checking_cdn',
            'Checking for known CDN providers...'
        )

        self.check_for_CDN_providers()

        self.view.erase_status('checking_cdn')
        self.view.set_status(
            'checking_updates',
            'Checking for updates now...'
        )

        self.check_for_updates()

        self.view.erase_status('checking_updates')

    def check_for_links(self):
        """
        This method gathers URLs present within the sheet calling this plugin.
        """
        # This is a regex written by @diegoperini, Python ported by @adamrofer.
        # (https://gist.github.com/dperini/729294)
        # It is tweaked to work with network path references and HTML tags.
        self.regionList = self.view.find_all(
            '(?:(https?:)?//)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S[^\"\s]*)?',
            IGNORECASE
        )

    def check_for_CDN_providers(self):
        """
        Simple method to filter out the regions containing a link not handled.
        """
        for region in self.regionList:
            # We parse the URL taken from that region...
            parsedResult = urlparse(
                self.view.substr(region)
            )

            # ... to check if it's a known CDN provider
            if parsedResult.netloc in CDNPROVIDERS:
                # If this matches, we store it and move on to the next element.
                self.cdnContentList.append(CDNContent(region, parsedResult))

    def check_for_updates(self):
        # See `CDNContent.py:handleProvider()` to check what is done.
        for cdnContent in self.cdnContentList:
            try:
                cdnContent.handleProvider()

            except OSError as e:
                # Let's display the console and log an error there.
                if active_window().active_panel() != 'console':
                    active_window().run_command(
                        'show_panel', {'panel': 'console', 'toggle': True}
                    )

                print('CDNUpdates: An error occurred for \"{}\" ({}).'.format(
                    cdnContent.parsedResult.geturl(),
                    e.reason)
                )

                # But we'll display a red icon anyway...
                cdnContent.status = 'not_found'

            # If this CDN represents a problem "that has to be fixed"...
            if cdnContent.status != 'up_to_date':
                # ... let's scroll directly to its location.
                self.view.show(cdnContent.sublimeRegion)

        # Let's add some regions for the user with specific colors.
        # This is done afterwards to reduce the number of regions drawn.
        for status in ['up_to_date', 'to_update', 'not_found']:
            self.view.add_regions(
                status,
                [cdnContent.sublimeRegion for cdnContent in self.cdnContentList
                    if cdnContent.status == status],
                'text',
                'Packages{0}CDNUpdates{0}Icons{0}{1}.png'.format(
                    os.sep, status
                ),
                DRAW_EMPTY_AS_OVERWRITE | DRAW_NO_FILL |
                DRAW_NO_OUTLINE | DRAW_SOLID_UNDERLINE
            )

        # Let's make appear a message dialog with a report for the user.
        message_dialog('CDNUpdates :{0}{0}'
                       '• {1} CDN already up to date.{0}'
                       '• {2} CDN to update.{0}'
                       '• {3} CDN not found.'.format(
                        '\r\n' if os.name == 'nt' else '\n',
                        len([i for i in self.cdnContentList
                            if i.status == 'up_to_date']),
                        len([i for i in self.cdnContentList
                            if i.status == 'to_update']),
                        len([i for i in self.cdnContentList
                            if i.status == 'not_found'])))


class CDNUpdatesListener(EventListener):
    def on_pre_save_async(self, view):
        view.erase_regions('up_to_date')
        view.erase_regions('to_update')
        view.erase_regions('not_found')

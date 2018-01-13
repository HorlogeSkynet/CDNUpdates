

from sublime import error_message

from sublime_plugin import EventListener, TextCommand

from .CDNCheckForCDNProviders import CheckForCDNProviders
from .CDNCheckForLinks import CheckForLinks
from .CDNCheckForUpdates import CheckForUpdates
from .CDNUtils import clear_view


class CDNUpdatesCommand(TextCommand):
    def run(self, edit):
        """
        Main function, only handling statuses and calling other methods
        """
        self.regionList = []
        self.cdnContentList = []

        # First we check if the current sheet is not still being loaded.
        if self.view.is_loading():
            error_message('This file is not fully loaded yet.')
            return

        else:
            # If it's OK, we clear the view from the elements added previously.
            clear_view(self.view)

        self.view.set_status(
            'checking_link',
            'Checking this sheet for links...'
        )

        CheckForLinks(self.view, self.regionList)

        self.view.erase_status('checking_link')
        self.view.set_status(
            'checking_cdn',
            'Checking for known CDN providers...'
        )

        CheckForCDNProviders(self.view, self.cdnContentList, self.regionList)

        self.view.erase_status('checking_cdn')
        self.view.set_status(
            'checking_updates',
            'Checking for updates now...'
        )

        # This operation will run in another Thread to not "freeze" the worker
        CheckForUpdates(self.view, self.cdnContentList).start()

        self.view.erase_status('checking_updates')


class CDNUpdatesListener(EventListener):
    def on_pre_save_async(self, view):
        clear_view(view)



from CDNUpdates.CDNCheckForCDNProviders import CheckForCDNProviders
from CDNUpdates.CDNCheckForLinks import CheckForLinks
from CDNUpdates.CDNCheckForUpdates import CheckForUpdates

from sublime import error_message

from sublime_plugin import EventListener, TextCommand


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


def clear_view(view):
    if view:
        # We just remove each regions containing icons in the gutter...
        view.erase_regions('up_to_date')
        view.erase_regions('to_update')
        view.erase_regions('not_found')

        # ... and our phantoms objects containing the latest versions...
        view.erase_phantoms('latest_versions')
        # ... and "specify version" advices...
        view.erase_phantoms('specify_versions')
        # ... and "specify HTTPS" advices.
        view.erase_phantoms('specify_https')



from CDNUpdates.CDNCheckForCDNProviders import CheckForCDNProviders
from CDNUpdates.CDNCheckForLinks import CheckForLinks
from CDNUpdates.CDNCheckForUpdates import CheckForUpdates

from sublime import message_dialog

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
        # We just remove each regions containing icons in the gutter...
        view.erase_regions('up_to_date')
        view.erase_regions('to_update')
        view.erase_regions('not_found')

        # ... and our phantoms objects containing the latest versions.
        view.erase_phantoms('latest_versions')

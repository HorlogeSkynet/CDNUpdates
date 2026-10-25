"""CDNUpdates main class"""

from sublime import error_message
from sublime_plugin import EventListener, TextCommand

from .check_for_cdn_providers import CheckForCdnProviders
from .check_for_links import CheckForLinks
from .check_for_updates import CheckForUpdates
from .utils import clear_view


class CdnUpdatesCommand(TextCommand):  # pylint: disable=too-few-public-methods
    """
    Entry point of CDNUpdates.
    The `run` method is called when the command is run.
    """
    def __init__(self, view):
        self.view = view

        self.region_list = []
        self.cdn_content_list = []

    def run(self, _):
        """
        Main function, only handling statuses and calling other methods
        """
        # First we check if the current sheet is not still being loaded.
        if self.view.is_loading():
            error_message("This view is not fully loaded yet.")
            return

        # If it's OK, we clear the view from the previously added elements.
        clear_view(self.view)

        self.view.set_status(
            'checking_link',
            "Checking this sheet for links..."
        )
        CheckForLinks(self.view, self.region_list)
        self.view.erase_status('checking_link')

        self.view.set_status(
            'checking_cdn',
            "Checking for known CDN providers..."
        )
        CheckForCdnProviders(self.view, self.cdn_content_list, self.region_list)
        self.view.erase_status('checking_cdn')

        self.view.set_status(
            'checking_updates',
            "Checking for updates now..."
        )
        # This operation will run in another Thread not to "freeze" the worker.
        CheckForUpdates(self.view, self.cdn_content_list).start()
        self.view.erase_status('checking_updates')


class CdnUpdatesListener(EventListener):  # pylint: disable=too-few-public-methods
    """Simple ST's listeners implementations"""

    def on_pre_save_async(self, view):
        """Just before file-saving, removes each CDNUpdates' object from the view"""
        clear_view(view)

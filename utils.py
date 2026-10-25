"""CDNUpdates' utils module"""

from sublime import active_window, load_settings


def clear_view(view):
    """Removes the passed `view` object all traces of our elements (known identifiers)"""
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


def log_message(message):
    """When debug mode is enabled in configuration, logs the passed message in the console"""
    if load_settings('CDNUpdates.sublime-settings').get('debug', False):
        if active_window().active_panel() != 'console':
            active_window().run_command(
                'show_panel',
                {
                    'panel': 'console',
                    'toggle': True
                }
            )

        print("[DEBUG] CDNUpdates : {0}".format(message))

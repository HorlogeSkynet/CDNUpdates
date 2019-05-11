"""CDNUpdates' utils module"""

from sublime import active_window, load_settings


# pylint: disable=line-too-long
# This regex has been written by @sindresorhus for Semver.
# <https://github.com/sindresorhus/semver-regex>
SEMVER_REGEX = r"v?(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-[\da-z-]+(?:\.[\da-z-]+)*)?(?:\+[\da-z-]+(?:\.[\da-z-]+)*)?"

# This is a regex written by @diegoperini, Python ported by @adamrofer.
# <https://gist.github.com/dperini/729294>
# It has been tweaked to work with network path references and HTML tags.
LINK_REGEX = r"(?:(https?:)?//)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S[^\"\s]*)?"
# pylint: enable=line-too-long


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

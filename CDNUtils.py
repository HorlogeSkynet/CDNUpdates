

from sublime import active_window, load_settings


def log_message(message):
    if load_settings('CDNUpdates.sublime-settings').get('debug', False):
        if active_window().active_panel() != 'console':
            active_window().run_command(
                'show_panel',
                {
                    'panel': 'console',
                    'toggle': True
                }
            )

        print('[DEBUG] CDNUpdates : {0}'.format(message))

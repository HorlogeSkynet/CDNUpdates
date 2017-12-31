

import os
from threading import Thread

from CDNUpdates.CDNUtils import log_message

from sublime import DRAW_EMPTY_AS_OVERWRITE, DRAW_NO_FILL, DRAW_NO_OUTLINE, \
    DRAW_SOLID_UNDERLINE
from sublime import LAYOUT_BLOCK, message_dialog


class CheckForUpdates(Thread):
    def __init__(self, view, cdnContentList):
        self.view = view
        self.cdnContentList = cdnContentList

        # Threading initialization
        Thread.__init__(self)

    def run(self):
        # See `CDNContent.py:handleProvider()` to check what is done.
        for cdnContent in self.cdnContentList:
            try:
                cdnContent.handleProvider()

            except OSError as e:
                # Let's display the console and log an error there.
                log_message('An error occurred for \"{}\" ({}).'.format(
                    cdnContent.parsedResult.geturl(),
                    e.reason)
                )

                # But we'll display a red icon anyway...
                cdnContent.status = 'not_found'

            # If this CDN represents a problem "that has to be fixed"...
            if cdnContent.status != 'up_to_date':
                # ... let's scroll directly to its location.
                self.view.show(cdnContent.sublimeRegion)

                # If the plugin is to update, let's set a "Phantom" with...
                # ... an interesting contents 😉
                if cdnContent.latestVersion:
                    self.view.add_phantom(
                        'latest_versions',
                        cdnContent.sublimeRegion,
                        """
                            <body id="CDN-new_version">
                                <style>
                                    div.new_version {{
                                        background-color: var(--bluish);
                                        padding: 10px;
                                    }}
                                </style>
                                <div class="new_version">
                                    New version for {0} found : <b>{1}</b>
                                </div>
                            </body>
                        """.format(cdnContent.name, cdnContent.latestVersion),
                        LAYOUT_BLOCK
                    )

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
                DRAW_EMPTY_AS_OVERWRITE | DRAW_NO_FILL | DRAW_NO_OUTLINE |
                DRAW_SOLID_UNDERLINE
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

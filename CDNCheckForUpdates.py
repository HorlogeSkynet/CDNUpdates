

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
                # Let's log an error there for the user (if `debug` is `true`).
                log_message('An error occurred for \"{0}\" ({1}).'.format(
                    cdnContent.parsedResult.geturl(),
                    e.reason)
                )

                # But we'll display a red icon anyway...
                cdnContent.status = 'not_found'

            # If this CDN represents a problem "that has to be fixed"...
            if cdnContent.status == 'to_update':
                # ... let's scroll directly to its location.
                self.view.show(cdnContent.sublimeRegion)

                # If the CDN is to update and we retrieved a newer version...
                # ...let's set a "Phantom" with an interesting content 😉
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

                # Let's inform the user he should specify version for this CDN.
                else:
                    self.view.add_phantom(
                        'specify_versions',
                        cdnContent.sublimeRegion,
                        """
                            <body id="CDN-no_version_found">
                                <style>
                                    div.no_version_found {{
                                        background-color: var(--orangish);
                                        color: black;
                                        padding: 10px;
                                    }}
                                </style>
                                <div class="no_version_found">
                                    You should specify a version for \"{0}\".
                                </div>
                            </body>
                        """.format(cdnContent.parsedResult.path
                                   .rpartition('/')[2]),
                        LAYOUT_BLOCK
                    )

            # Security measures !
            # If this resource is not loaded over HTTPS, we add a warning !
            if cdnContent.parsedResult.scheme != 'https':
                self.view.add_phantom(
                    'specify_https',
                    cdnContent.sublimeRegion,
                    """
                        <body id="CDN-https_warning">
                            <style>
                                div.https_warning {{
                                    background-color: var(--redish);
                                    color: black;
                                    padding: 10px;
                                }}
                            </style>
                            <div class="https_warning">
                                You should load {0} over HTTPS !
                            </div>
                        </body>
                    """.format(cdnContent.name or
                               '\"' + cdnContent.parsedResult.path
                               .rpartition('/')[2] + '\"'),
                    LAYOUT_BLOCK
                )

        # Let's add some regions for the user with specific icons.
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

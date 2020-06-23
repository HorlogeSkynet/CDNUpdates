"""CDNUpdates' update verification entry point"""

import os
from threading import Thread
from urllib.error import HTTPError

from sublime import (
    DRAW_EMPTY_AS_OVERWRITE,
    DRAW_NO_FILL,
    DRAW_NO_OUTLINE,
    DRAW_SOLID_UNDERLINE,
    LAYOUT_BLOCK,
    message_dialog
)

from .CDNUtils import log_message


class CheckForUpdates(Thread):
    """This class run asynchronously the CDNs version checking upstream."""

    def __init__(self, view, cdn_content_list):
        self.view = view
        self.cdn_content_list = cdn_content_list

        # Threading initialization.
        Thread.__init__(self)

    def run(self):
        # See `CDNContent.py:handle_provider()` to check what is done.
        for cdn_content in self.cdn_content_list:
            try:
                cdn_content.handle_provider()

            except HTTPError as error:
                # Let's log an error there for the user (if `debug` is `true`).
                log_message(
                    "An error occurred for \"{0}\" ({1}).".format(
                        cdn_content.parsed_result.geturl(),
                        error.reason
                    )
                )

                # But we'll display a red icon anyway...
                cdn_content.status = 'not_found'

            # If this CDN represents a problem "that has to be fixed"...
            if cdn_content.status == 'to_update':
                # ... let's scroll directly to its location.
                self.view.show(cdn_content.sublime_region)

                # If the CDN is to update and we retrieved a newer version...
                # ...let's set a "Phantom" with an interesting content 😉
                if cdn_content.latest_version:
                    self.view.add_phantom(
                        'latest_versions',
                        cdn_content.sublime_region,
                        """
                            <body id="CDN-new_version">
                                <style>
                                    div.new_version {{
                                        background-color: var(--bluish);
                                        color: black;
                                        padding: 10px;
                                    }}
                                </style>
                                <div class="new_version">
                                    New version for {0} found : <b>{1}</b>
                                </div>
                            </body>
                        """.format(cdn_content.name, cdn_content.latest_version),
                        LAYOUT_BLOCK
                    )

                # Let's inform the user he should specify version for this CDN.
                else:
                    self.view.add_phantom(
                        'specify_versions',
                        cdn_content.sublime_region,
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
                                    You should specify a version for <b>{}</b>.
                                </div>
                            </body>
                        """.format(
                            cdn_content.parsed_result.path.rpartition('/')[2]
                        ),
                        LAYOUT_BLOCK
                    )

            # Security measures !
            # If this resource is not loaded over HTTPS, we add a warning !
            if cdn_content.parsed_result.scheme != 'https':
                self.view.add_phantom(
                    'specify_https',
                    cdn_content.sublime_region,
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
                                You should explicitly load <b>{0}</b> over HTTPS !
                            </div>
                        </body>
                    """.format(
                        cdn_content.name or
                        cdn_content.parsed_result.path.rpartition('/')[2]
                    ),
                    LAYOUT_BLOCK
                )

        # Let's add some regions for the user with specific icons.
        # This is done afterwards to reduce the number of regions drawn.
        for status in ['up_to_date', 'to_update', 'not_found']:
            self.view.add_regions(
                status,
                [cdn_content.sublime_region for cdn_content in self.cdn_content_list
                 if cdn_content.status == status],
                'text',
                "Packages/CDNUpdates/Icons/{0}.png".format(status),
                DRAW_EMPTY_AS_OVERWRITE | DRAW_NO_FILL | DRAW_NO_OUTLINE |
                DRAW_SOLID_UNDERLINE
            )

        # Let's make appear a message dialog with a report for the user.
        message_dialog(
            "CDNUpdates :{0}{0}"
            "• {1} CDN already up to date.{0}"
            "• {2} CDN to update.{0}"
            "• {3} CDN not found.{0}"
            "• {4} CDN not loaded over HTTPS.".format(
                os.linesep,
                len([i for i in self.cdn_content_list
                     if i.status == 'up_to_date']),
                len([i for i in self.cdn_content_list
                     if i.status == 'to_update']),
                len([i for i in self.cdn_content_list
                     if i.status == 'not_found']),
                len([i for i in self.cdn_content_list
                     if i.parsed_result.scheme != 'https'])
            )
        )

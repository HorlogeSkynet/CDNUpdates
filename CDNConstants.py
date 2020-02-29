"""CDNUpdates' constants module"""

# pylint: disable=line-too-long
# This regex has been written by @sindresorhus for Semver.
# <https://github.com/sindresorhus/semver-regex> (v3.1.1)
SEMVER_REGEX = r"(?<=^v?|\sv?)(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)(?:-(?:0|[1-9]\d*|[\da-z-]*[a-z-][\da-z-]*)(?:\.(?:0|[1-9]\d*|[\da-z-]*[a-z-][\da-z-]*))*)?(?:\+[\da-z-]+(?:\.[\da-z-]+)*)?(?=$|\s)"

# This is a regex written by @diegoperini, ported for Python by @adamrofer.
# <https://gist.github.com/dperini/729294>
# It has been tweaked to work with network path references and HTML tags.
LINK_REGEX = r"(?:(https?:)?//)(?:\S+(?::\S*)?@)?(?:(?!(?:10|127)(?:\.\d{1,3}){3})(?!(?:169\.254|192\.168)(?:\.\d{1,3}){2})(?!172\.(?:1[6-9]|2\d|3[0-1])(?:\.\d{1,3}){2})(?:[1-9]\d?|1\d\d|2[01]\d|22[0-3])(?:\.(?:1?\d{1,2}|2[0-4]\d|25[0-5])){2}(?:\.(?:[1-9]\d?|1\d\d|2[0-4]\d|25[0-4]))|(?:(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)(?:\.(?:[a-z\u00a1-\uffff0-9]-?)*[a-z\u00a1-\uffff0-9]+)*(?:\.(?:[a-z\u00a1-\uffff]{2,})))(?::\d{2,5})?(?:[/?#]\S[^\"\s]*)?"
# pylint: enable=line-too-long

# This list stores the API links of handled CDN providers.
CDN_PROVIDERS = [
    'cdnjs.cloudflare.com',
    'maxcdn.bootstrapcdn.com',
    'code.jquery.com',
    'ajax.googleapis.com',
    'cdn.jsdelivr.net',
    'rawgit.com',
    'cdn.rawgit.com',
    'code.ionicframework.com',
    'use.fontawesome.com',
    'opensource.keycdn.com',
    'cdn.staticfile.org',
    'ajax.microsoft.com',
    'ajax.aspnetcdn.com',
    'cdn.ckeditor.com'
]

# The dictionaries below will store the "correspondences" between project names and...
# ... GitHub repositories identities (owner / name).
# This allows us to fetch latest version from GitHub when a provider does not offer any API.
MAXCDN_BOOTSTRAP_CORRESPONDENCES = {
    'bootstrap': {
        'owner': 'twbs',
        'name': 'bootstrap'
    },
    'font-awesome': {
        'owner': 'FortAwesome',
        'name': 'Font-Awesome'
    },
    'bootlint': {
        'owner': 'twbs',
        'name': 'bootlint'
    },
    'bootswatch': {
        'owner': 'thomaspark',
        'name': 'bootswatch'
    }
}

AJAX_GOOGLE_APIS_CORRESPONDENCES = {
    'dojo': {
        'owner': 'dojo',
        'name': 'dojo'
    },
    'ext-core': {
        'owner': 'ExtCore',
        'name': 'ExtCore'
    },
    'hammerjs': {
        'owner': 'hammerjs',
        'name': 'hammer.js'
    },
    'indefinite-observable': {
        'owner': 'material-motion',
        'name': 'indefinite-observable-js'
    },
    'jquery': {
        'owner': 'jquery',
        'name': 'jquery'
    },
    'jquerymobile': {
        'owner': 'jquery',
        'name': 'jquery-mobile'
    },
    'jqueryui': {
        'owner': 'jquery',
        'name': 'jquery-ui'
    },
    'mootools': {
        'owner': 'mootools',
        'name': 'mootools-core'
    },
    'myanmar-tools': {
        'owner': 'googlei18n',
        'name': 'myanmar-tools'
    },
    'prototype': {
        'owner': 'sstephenson',
        'name': 'prototype'
    },
    'scriptaculous': {
        'owner': 'madrobby',
        'name': 'scriptaculous'
    },
    'shaka-player': {
        'owner': 'google',
        'name': 'shaka-player'
    },
    'spf': {
        'owner': 'youtube',
        'name': 'spfjs'
    },
    'swfobject': {
        'owner': 'swfobject',
        'name': 'swfobject'
    },
    'threejs': {
        'owner': 'mrdoob',
        'name': 'three.js'
    },
    'webfont': {
        'owner': 'typekit',
        'name': 'webfontloader'
    }
}

OPENSOURCE_KEYCDN_CORRESPONDENCES = {
    'fontawesome': {
        'owner': 'FortAwesome',
        'name': 'Font-Awesome'
    },
    'pure': {
        'owner': 'yahoo',
        'name': 'pure'
    }
}

CDN_STATIC_FILE_CORRESPONDENCES = {
    'react': {
        'owner': 'facebook',
        'name': 'react'
    },
    'vue': {
        'owner': 'vuejs',
        'name': 'vue'
    },
    'angular.js': {
        'owner': 'angular',
        'name': 'angular.js'
    },
    'jquery': {
        'owner': 'jquery',
        'name': 'jquery'
    }
}

# Sources : <https://docs.microsoft.com/en-us/aspnet/ajax/cdn/>
AJAX_MICROSOFT_CORRESPONDENCES = {
    'jquery': {
        'owner': 'jquery',
        'name': 'jquery'
    },
    'jquery.migrate': {
        'owner': 'jquery',
        'name': 'jquery-migrate'
    },
    'jquery.ui': {
        'owner': 'jquery',
        'name': 'jquery-ui'
    },
    'jquery.mobile': {
        'owner': 'jquery',
        'name': 'jquery-mobile'
    },
    'jquery.validate': {
        'owner': 'jquery-validation',
        'name': 'jquery-validation'
    },
    'jquery.templates': {
        'owner': 'BorisMoore',
        'name': 'jquery-tmpl',
        'fuzzy_check': True
    },
    'jquery.cycle': {
        'owner': 'malsup',
        'name': 'cycle2'
    },
    'jquery.dataTables': {
        'owner': 'dataTables',
        'name': 'dataTables'
    },
    'jshint': {
        'owner': 'jshint',
        'name': 'jshint'
    },
    'modernizr': {
        'owner': 'Modernizr',
        'name': 'Modernizr'
    },
    'respond': {
        'owner': 'scottjehl',
        'name': 'Respond'
    },
    'globalize': {
        'owner': 'globalizejs',
        'name': 'globalize'
    },
    'knockout': {
        'owner': 'knockout',
        'name': 'knockout'
    },
    'bootstrap': {
        'owner': 'twbs',
        'name': 'bootstrap'
    },
    'bootstrap-touch-carousel': {
        'owner': 'ixisio',
        'name': 'bootstrap-touch-carousel'
    },
    'hammer.js': {
        'owner': 'hammerjs',
        'name': 'hammer.js'
    },
    'signalr': {
        'owner': 'SignalR',
        'name': 'SignalR'
    }
}

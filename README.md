# CDNUpdates

> A Sublime Text 3 plugin to check for CDN updates in your Web pages

Bored of manually check if your CDNs are up to date ? Yeah, so was I...  
This is what this Sublime Text 3 plugin does (well) :

1. Gathers links present in your current sheet
2. Compares them with a list containing known CDN providers
3. Figures out a way to retrieve the latest "version" of each resource, and compares it with the one you are currently using
4. Displays a basic (ugly ?) icon in the gutter, to inform you of the result

Of course, when this plugin does not use the API of the CDN provider, it may informs you of a newer published version, possibly not available from your provider (it would be time to opt out of this privacy mess, by the way...).

## Installation

Coming soon...

## Usage

* Open your command palette and type in : `CDNUpdates`

* Press `CTRL + SHIFT + C`

* Right click on your file : `CDNUpdates > ...`

* `Tools > Packages > CDNUpdates > ...`

## Settings

Most of the CDN providers don't provide any API for their service, so it would be very tricky to retrieve latest version available directly from them.  
Unless for <https://cdnjs.com/>, this plugin is actually based on the GitHub API to fetch from repositories the latest existing Git tag. Its `name` is compared afterwards with the version present in the CDN you got in your sources.  
If you have many many CDNs in your sheets (or if you want to contribute to this project 😜), you'll surely need to set a GitHub API token to avoid reaching the rate limit. You can generate one [here](https://github.com/settings/tokens), and paste in under the plugin preferences (accessible from `CDNUpdates`'s Sublime menu).

## CDN Providers currently handled

* [X] <https://cdnjs.com/>
* [X] <https://bootstrapcdn.com/>
* [X] <https://code.jquery.com/>
* [X] <https://ajax.googleapis.com/>
* [ ] More soon...

## Frequently Asked Questions

### How do I get rid of your horrible icons in the gutter ?

> It'll be done automatically next time you'll save your sheet :wink:

### Can I add another or my own CDN ?

> Of course you can, unless this project wouldn't be Open Source !  
> You basically just have to tweak [CDNContent.py](CDNContent.py) and imitate what is done there for your provider.  
> Don't forget to share your work with the world ! :earth_africa:  
> Or... you can just open an [issue here](https://github.com/HorlogeSkynet/CDNUpdates/issues/new) and I'll do my best to handle your case !

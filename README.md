# CDNUpdates

> A Sublime Text 3 plugin to check for CDN updates in your Web pages

## Installation

Coming soon...

## Usage

* Open your command palette and type in : `CDNUpdates`

* Press `CTRL + SHIFT + C`

* Right click on your file : `CDNUpdates >`

## Settings

Most of the CDN providers don't provide any API for their service, so it would be very tricky to retrieve latest version available directly from them.  
Unless for <https://cdnjs.com/>, this plugin is actually based on the GitHub API to fetch from repositories the latest existing Git tag. Its `name` is compared afterwards with the version present in the CDN you got in your sources.  
If you have many many CDNs in your sheets (or if you want to contribute to this project 😜), you'll surely need to set a GitHub API token to avoid reaching the rate limit. You can generate one [here](https://github.com/settings/tokens), and paste in under the plugin preferences (accessible from `CDNUpdates`'s Sublime menu).

## CDN Providers currently handled

* [X] <https://cdnjs.com/>
* [X] <https://bootstrapcdn.com/>
* [X] <https://code.jquery.com/>
* [ ] More soon...

## Frequently Asked Questions

### How do I get rid of your horrible icons in the gutter ?

> It'll be done automatically next time you'll save your sheet :wink:

### Can I add another or my own CDN ?

> Of course you can, unless this project wouldn't be Open Source !  
> You basically just have to tweak [CDNContent.py](CDNContent.py) and imitate what is done there for your provider.  
> Don't forget to share your work with the world ! :earth_africa:  
> Or... you can just open an [issue here](https://github.com/HorlogeSkynet/CDNUpdates/issues/new) and I'll do my best to handle your case !

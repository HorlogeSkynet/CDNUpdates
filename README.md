# CDNUpdates

> A Sublime Text 3 plugin to check for CDN updates in your Web sources

![Preview](https://i.imgur.com/WrxQApP.png)

## Introduction

Tired of manually checking if your CDN (_Content Delivery Network_) are up to date in your web pages ? Yeah, so was I... :confused:

This is what this Sublime Text 3 plugin does (well) to help you dealing with this :

1. Gathers links present in your current sheet
2. Compares them to a list containing known public CDN providers
3. Figures out a way (with providers' API or with GitHub one) to retrieve the latest "version" of each resource, and compares it with the one you are currently using
4. Displays some icons in the gutter, to inform you of the results
5. Displays a _Phantom_ object with the latest version available you should be using
6. _Bonus_ : Shows up a warning for resources not loaded over HTTPS :+1:

Of course, when this plugin does not use the API of the CDN provider, it may informs you of a newer published version, possibly not available from your provider (maybe it's time to opt out from this privacy mess ? :wink:).

## Installation

### With Package Control

1. Open your command palette and type in : `Package Control: Install Package`
2. Browse the list or search for `CDNUpdates`
3. Press `Enter` and you're done !

Package Control dedicated page [here](https://packagecontrol.io/packages/CDNUpdates).

### Manually

1. Move into Sublime Text packages folder (usually `$HOME/.config/sublime-text-3/Packages/` or `%AppData%\Sublime Text 3\Packages\`)
2. Clone this repository there : `$ git clone https://github.com/HorlogeSkynet/CDNUpdates.git`
3. Restart Sublime Text and... :tada:

## Usage

* Open your command palette and type in : `CDNUpdates`

* Right click on your file : `CDNUpdates > ...`

* `Tools > Packages > CDNUpdates > ...`

## Settings

Most of the CDN providers don't provide any API for their service, so it would be very tricky to retrieve latest version available directly from them.  
Unless for <https://cdnjs.com/>, this plugin is actually based on the GitHub API to fetch from repositories the latest existing Git tag. Its `name` is compared afterwards with the CDN version present in your sources.  
If you have many many CDNs in your sheets (or if you want to contribute to this project 😜), you'll surely need to set a GitHub API token to avoid being blocked by the rate limit.  
You can generate one [here](https://github.com/settings/tokens), and paste in under the plugin preferences (accessible from `CDNUpdates`'s Sublime menu).

## CDN Providers currently handled

* [X] <https://cdnjs.com/>
* [X] <https://bootstrapcdn.com/>
* [X] <https://code.jquery.com/>
* [X] <https://ajax.googleapis.com/>
* [X] <https://jsdelivr.com/>
* [X] <https://rawgit.com/>
* [X] <https://code.ionicframework.com/>
* [X] <https://cdn.fontawesome.com/>
* [X] <https://www.keycdn.com/> (partially)
* [X] <https://www.staticfile.org/>
* [X] <https://ajax.aspnetcdn.com/> (partially)
* [X] <https://cdn.ckeditor.com>

## Frequently Asked Questions

### How do I get rid of your horrible icons in the gutter ?

> It'll be done automatically next time you'll save your sheet :wink:

### I've updated my links, but the _Phantom_ objects don't want to leave...

> Same as above :smile:

### Can I add another (or my own) CDN ?

> Of course you can, unless the Open Source aspect of this project would be useless :fearful:  
> You basically just have to tweak [CDNContent.py](CDNContent.py) and imitate what is done there for your provider.  
> Don't forget to share your work with the world ! :earth_africa:  
> Or... you can just open an [issue here](https://github.com/HorlogeSkynet/CDNUpdates/issues/new) and I'll do my best to handle your case !

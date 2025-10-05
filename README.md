# Objectionodon - Ace Attorney Mastodon Bot

One of my favorite things about the old bird website was the number of shitposting bots that were all over the place. The Fediverse needs more of those. (im-doing-my-part.gif)

So this is my attempt to make a version of the Ace Attorney Bot (https://github.com/LuisMayo/ace-attorney-twitter-bot?tab=readme-ov-file) for Mastodon.

## Dependencies

Most of the heavy lifting is handled by LuisMayo's "Objection_Engine" project: https://github.com/LuisMayo/objection_engine 

Look, I'll write the rest of the Readme later. I promise...

- Python 3.12.x
- 

# Installation

0. (optional) Create a Virtual Environment 

`python3 -m venv venv`

`source .venv/bin/activate`

1. Install build dependencies

### Pillow 

objection_engine needs Pillow, which itself needs many system libraries. 

if on macOS with Homebrew:

`brew install libavif libjpeg libraqm libtiff little-cms2 openjpeg webp`

See https://pillow.readthedocs.io/en/latest/installation/building-from-source.html#building-from-source for more info about setup for other systems

### Ffmpeg

You need this too! 

`brew install ffmpeg`

### Polyglot

If you wanted to support languages beyond English, you should also install polyglot:

`python3 -m pip install pyICU pycld2 morfessor polyglot`

If on macOS, see this important info from the `icu4c` homebrew info:

```
icu4c@77 is keg-only, which means it was not symlinked into /opt/homebrew,
because macOS provides libicucore.dylib (but nothing else).

If you need to have icu4c@77 first in your PATH, run:
  echo 'export PATH="/opt/homebrew/opt/icu4c@77/bin:$PATH"' >> /Users/ben.pettis/.zshrc
  echo 'export PATH="/opt/homebrew/opt/icu4c@77/sbin:$PATH"' >> /Users/ben.pettis/.zshrc

For compilers to find icu4c@77 you may need to set:
  export LDFLAGS="-L/opt/homebrew/opt/icu4c@77/lib"
  export CPPFLAGS="-I/opt/homebrew/opt/icu4c@77/include"

For pkgconf to find icu4c@77 you may need to set:
  export PKG_CONFIG_PATH="/opt/homebrew/opt/icu4c@77/lib/pkgconfig"
```

Do those things before trying to install polyglot

2. Install objection_engine using pip


`pip install objection_engine`


3. Install some other dependencies 

This will probably not work right away. 



# Usage

## Environment Variables

Create a `.env` file to store important secrets (or have them set in your run environment)

## Blacklist

I think it's important to have some control over where the bot will run. People may not want their posts included. You may also want to manually specify some accounts that just shouldn't be included for whatever reason. For example, I follow the Auschwitz Museum in the Fediverse - they regularly post important remembrances from history. I don't think that content would be appropriate for displaying in Ace Attorney format. So I skip it. 

The demo `blacklist.txt` file works as an example of how this file should be set up. I am including my own bot's account in the list as an example - but note that the script is already set up to skip any threads to which it has already responded.



# Known Issues

- Blacklisted accounts - if your mastodon server uses an alias for its domain name, then the blacklist will almost certainly not behave correctly. 
    - For example, my server is at `mastodon.benpettis.ninja` but its alias for any account names is just `benpettis.ninja`. This means that my bot's account username appears to be `@objectionodon@benpettis.ninja`. But the way that the script checks the blacklist, it is going to compare the username to `@objectionodon@mastodon.benpettis.ninja` and not match as expected
    - as a temporary workaround, if listing any local accounts on the blacklist, you must use the _full_ domain name

---

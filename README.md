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


## To 

# Usage

---

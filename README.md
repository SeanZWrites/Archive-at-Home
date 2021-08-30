# Archive At Home
A static website generator for downloaded AO3 fic.

## Overview
This tool can parse all of your downloaded (html) fanfic from
AO3 and build a local, private website where you can read 
all your fic.

It will import tags, authors, series, and more, so you can
easily browse your downloaded files. Simply copy all your
downloaded fic into the `content` directory, run this tool,
and you'll have a local website you can navigate to!

## Installation
This tool requires python3. You'll need to have it installed
before you can proceed. 

  1. Clone this git repo with the command `git clone https://github.com/SeanZWrites/Archive-at-Home`
  2. (Optional, but recommended) Create a virtual env for your work by running `python -m venv ./venv && . ./venv/bin/activate`
  3. Install all dependencies with `pip install -r requirements.txt`

You're now ready to use the tool!

## Running
*Note: If you are using a virtual env, you'll need to activate it before running
these commands. Run `. ./venv/bin/activate` to activate. Windows users should
run `./venv/Scripts/activate` instead.*

  1. Copy your download fic to the `content` folder. 
  2. Run `inv reserve`

That's it! There will be a message that your website is now available on
`localhost:8000`, simply plug that into your web browser and read your fics!

## Acknowledgements
This tool relies on [Pelican](https://blog.getpelican.com/), and would not be possible their work.

The included theme is based on Pelican's 'simple' theme, and the AO3 parser is
based on their HTML parser.
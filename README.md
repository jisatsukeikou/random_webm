## Description

This is a simple script collection to learn new languages on same sample constructions doing the same task.\
The algorithm is simple: get JSON with threads named "WEBM*", collect urls to webm files and play either random link or temporary playlist of all links in your favorite player.

## Usage

`./random_webm.<ext> [-b <board>] [-p]`\
\
`-b`: Specify board to get webms from. /a/ by default.\
`-p`: Playlist mode, start a playlist of all webms found.\
\
You might also want to change your player path/arguments, if you're on Windows; the default player is mpv (Linux).

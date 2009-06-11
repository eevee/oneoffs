#!/usr/bin/zsh
# Minimally-interactive screenshot tool.  All parameters are passed to scrot.

# When launching this script from a compiz command, compiz has a lock on the
# keyboard, and scrot complains it cannot grab the keyboard if there's not a
# delay.  Lame but whatever
sleep 0.25

# Save to a tempfile so we don't have to worry about waiting for the zenity
# window to close
local tempfile; tempfile=$(mktemp).png
scrot $* $tempfile

# Ask where to save locally
local screenshot_root; screenshot_root=/stuff/pictures/screenshots/  # NEED trailing slash
local screenshot_path
screenshot_path=$(zenity --title='Save screenshot' --file-selection --save --filename=$screenshot_root --confirm-overwrite)

local screenshot_filename
screenshot_filename=${screenshot_path/$screenshot_root/}

# Move the tempfile to the right place and copy it to stuff.veekun.com
mv $tempfile $screenshot_path
scp $screenshot_path veekun.com:stuff.veekun.com/screenshots/$screenshot_filename

# Report success
zenity --info --title='Success' --text=http://stuff.veekun.com/screenshots/$screenshot_filename

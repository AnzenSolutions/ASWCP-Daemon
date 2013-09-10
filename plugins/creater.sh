#!/bin/sh

# Simple helper script to create a plugin directory.
# Nothing more, nothing less.

if [ -z "$1" ]; then
	read -p "Plugin class: " CLASS
	read -p "Plugin name: " PLUGIN
elif [ -z "$2" ]; then
	CLASS="$1"
	read -p "Plugin name: " PLUGIN
else
	CLASS="$1"
	PLUGIN="$2"
fi

PDIR="$CLASS/$PLUGIN"
PFILE="$PDIR/$PLUGIN.py"

if [ ! -d "$PDIR" ]; then
	mkdir -p "$PDIR"
	touch "$PFILE"

	echo "Properly installed $PLUGIN to $PDIR; edit $PFILE now."
else
	echo "$PLUGIN already exists in $CLASS"

	if [ ! -f "$PFILE" ]; then
		echo "Plugin is not proper.  $PFILE must exist."
	else
		echo "Plugin is properly installed."
	fi
fi

exit 0

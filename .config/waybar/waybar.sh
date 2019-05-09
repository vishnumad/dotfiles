#!/usr/bin/env sh

# Kill running waybar instances
killall -q waybar

# Kill instances of media player script
ps -ef | awk '/python \/home\/vishnu\/scripts\/player-mpris-tail.py/{print $2}' | xargs kill

while pgrep -x waybar >/dev/null; do sleep 1; done

# Start waybar
waybar

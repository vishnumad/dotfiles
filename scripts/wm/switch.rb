#!/usr/bin/env ruby

# Gets the currently running window manager
def get_current_wm()
  output = `wmctrl -m`
  output.lines.first.sub(/Name: /, "").chomp
end

def start_wm(wm)
  system("#{wm} &")
end

def kill_wm(wm)
  system("pkill #{wm}")
end

wm = get_current_wm

if wm == "i3"
  puts "Running i3. Switch to Openbox"
  kill_wm 'i3'
  start_wm 'openbox'
elsif wm == 'Openbox'
  puts "Running Openbox. Switch to i3"
  kill_wm 'openbox'
  start_wm 'i3'
end


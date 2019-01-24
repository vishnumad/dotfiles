#!/usr/bin/env ruby

def change_brightness(value)
	system("qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl setBrightnessSilent #{value}")
end

max_brightness = `qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightnessMax`.to_i
current_brightness = `qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightness`.to_i
brightness_steps = `qdbus org.kde.Solid.PowerManagement /org/kde/Solid/PowerManagement/Actions/BrightnessControl brightnessSteps`.to_i * 3

case ARGV[0]
when "inc"
	# Increase brightness
	to_brightness = current_brightness + brightness_steps
	change_brightness [to_brightness, max_brightness].min
when "dec"
	# Decrease brightness
	to_brightness = current_brightness - brightness_steps
	change_brightness [to_brightness, 0].max
else
	abort("Invalid argument at 0: #{ARGV[0]}")
end

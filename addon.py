import xbmcaddon
import xbmcgui

from resources.lib.firebase_handler import log_message
 
addon       = xbmcaddon.Addon()
addonname   = addon.getAddonInfo('name')

# Set a string variable to use
line1 = "Making a change without restarting Kodi"

# Launch a dialog box in kodi showing the string variable 'line1' as the contents
xbmcgui.Dialog().ok(addonname, line1)

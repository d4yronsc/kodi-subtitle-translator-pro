"""Force translate - invoke manually to re-trigger subtitle translation.

Usage from Kodi:
  RunScript(service.subtitletranslator.tamabin, force_translate)

Or map to a key/button in keymap XML.
"""
import xbmc

# Send notification to the running service
xbmc.executebuiltin('NotifyAll(force_translate_tamabin, force_translate_tamabin)')
xbmc.log("[service.subtitletranslator.tamabin] Force translate signal sent", xbmc.LOGINFO)

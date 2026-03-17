# -*- coding: utf-8 -*-
"""Entry point for manual subtitle translation trigger.

Appears in Programs > Add-ons. Can be added to Favourites for quick access.
"""
import xbmc
import xbmcgui

# Check if something is playing
player = xbmc.Player()
if not player.isPlaying():
    xbmcgui.Dialog().notification(
        "TaMaBin",
        "Play a video first / Reproduce un video primero",
        xbmcgui.NOTIFICATION_WARNING,
        3000
    )
else:
    # Send force_translate signal to the running service
    xbmc.executebuiltin('NotifyAll(force_translate_tamabin, force_translate_tamabin)')
    xbmcgui.Dialog().notification(
        "TaMaBin",
        "Translating subtitles... / Traduciendo subtitulos...",
        xbmcgui.NOTIFICATION_INFO,
        3000
    )

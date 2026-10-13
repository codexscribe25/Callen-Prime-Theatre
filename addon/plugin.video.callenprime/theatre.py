"""Launch the Callen Prime full-screen theatre without switching Kodi skins."""
import xbmc
import xbmcaddon
import xbmcgui


def main():
    addon = xbmcaddon.Addon()
    try:
        # Lazy import: the light widget routes never load the heavy GUI module.
        from resources.lib.theatre_window import launch
        launch(addon.getAddonInfo('path'))
    except Exception as error:
        xbmc.log('[Callen Prime] theatre unavailable: ' + type(error).__name__, xbmc.LOGERROR)
        xbmcgui.Dialog().ok('Callen Prime Theatre',
                            'Could not open the theatre window. Your original Kodi skin is untouched. Check the Kodi log for Callen Prime.')


if __name__ == '__main__':
    main()

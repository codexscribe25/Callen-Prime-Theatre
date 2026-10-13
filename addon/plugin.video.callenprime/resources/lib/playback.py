"""Explicit, user-directed local playback. Never invoked by a widget listing."""
import os

VIDEO_SUFFIXES = frozenset(('.mp4', '.m4v', '.mkv', '.webm', '.avi', '.mov', '.ts'))


def local_video_path(path):
    """Allow only a filesystem file selected interactively in Kodi.

    This is intentionally narrower than Kodi's supported media URLs. Network
    sources, protocol handlers, directories and arbitrary caller URL parameters
    are not supported in CP04.
    """
    if not isinstance(path, str) or not path or '\x00' in path or len(path) > 2048:
        return None
    if '://' in path or '|' in path or '?' in path or '#' in path or '\n' in path or '\r' in path:
        return None
    if not os.path.isabs(path) or not os.path.isfile(path):
        return None
    if os.path.splitext(path)[1].lower() not in VIDEO_SUFFIXES:
        return None
    return path


def select_local_video(dialog):
    """Return a validated path after user selection + confirmation, else None."""
    selected = dialog.browseSingle(1, 'Select your local video', 'local',
                                   '.mp4|.m4v|.mkv|.webm|.avi|.mov|.ts',
                                   False, False, '')
    path = local_video_path(selected)
    if not path:
        # Cancellation is deliberately silent.
        if selected:
            dialog.ok('Local playback unavailable',
                      'Choose a supported video file stored on this device. Network links and folders are excluded.')
        return None
    if not dialog.yesno('Callen Prime | Local test',
                        'Play the video you selected? Kodi will control pause, seek, stop and resume.'):
        return None
    return path

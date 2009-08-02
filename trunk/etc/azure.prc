# GLOBAL AZURE SETTINGS
# ---------------------
# These settings are read at the start of a game and override Panda3D's
# settings. All except those starting with azure- are reserved by Panda3D.
# For all panda settings, see:
# http://www.panda3d.org/wiki/index.php/List_of_All_Config_Variables


# window
# ------
window-title Azure: Infinite Skies
win-origin 50 50
win-size 800 600
fullscreen true


# paths
# -----
# where to look for all models, textures, fonts etc.
model-path $MAIN_DIR/assets
# OS dependent - will be determined by python. change to force
#model-cache-dir /tmp/pandacache


# graphics
# --------
basic-shaders-only false
use-movietexture true
compressed-textures true
driver-compress-textures true
model-cache-textures true
# default camera clipping
default-far 100000
# scale textures while loading (lower for more performance)
texture-scale 1


# audio
# -----
audio-library-name p3openal_audio
audio-music-active true
audio-sfx-active true
audio-volume 1


# else
# ----
# use DirectX if available (windows) or fall back to opengl (linux, mac)
aux-display pandadx9
aux-display pandadx8
aux-display pandagl
load-display *
# opengl display lists support
display-lists true
# set higher on multicore processors
loader-num-threads 1
# used when panda writes text files (unsure what's best here)
#newline-mode msdos
newline-mode unix


# debugging
# ---------
#window-type none
want-dev false
want-pstats false
# framerate limitation
sync-video false
show-frame-rate-meter true
on-screen-debug-enabled true
notify-output azure-log.txt

# notifier verbosity levels: spam, debug, info, warning, error
notify-level info
default-directnotify-level                  info
notify-level-BufferViewer                   error
notify-level-BulletinBoard                  error
notify-level-ClassicFSM 			        error
notify-level-DirectScrolledList             error
notify-level-DirectScrolledListItem         error
notify-level-EventManager                   error
notify-level-ExceptionVarDump               error
notify-level-FunctionInterval               error
notify-level-GarbageReport                  error
notify-level-InputState                     error
notify-level-JobManager                     error
notify-level-LerpFunctionInterval           error
notify-level-LerpFunctionNoStateInterval    error
notify-level-Loader                         error
notify-level-Messenger                      error
notify-level-MetaInterval                   error
notify-level-ShowBase                       error
notify-level-State                          error
notify-level-TaskManager                    error

# vim:set sw=4 ts=4 sts=4 et sta:

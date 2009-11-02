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
fullscreen false


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
# antialiasing
framebuffer-multisample true
multisamples 2
#multisamples 4
#multisamples 8
# default camera clipping
default-far 100000
# scale textures while loading (lower for more performance)
texture-scale 1
azure-bloom-filter false
azure-cartoon-ink false


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
#notify-output azure-log.txt

# notifier verbosity levels: (spam), debug, info, warning, error, (fatal)
# the ones in brackets are only available for C++ modules (not direct)
default-directnotify-level                  warning
notify-level                                warning
#notify-level-util                           fatal
#notify-level-ShowBase                       debug
#notify-level-BufferViewer                   debug
#notify-level-BulletinBoard                  debug
#notify-level-FSM                            debug
#notify-level-DirectScrolledList             debug
#notify-level-DirectScrolledListItem         debug
#notify-level-EventManager                   debug
#notify-level-ExceptionVarDump               debug
#notify-level-FunctionInterval               debug
#notify-level-GarbageReport                  debug
#notify-level-InputState                     debug
#notify-level-JobManager                     debug
#notify-level-LerpFunctionInterval           debug
#notify-level-LerpFunctionNoStateInterval    debug
#notify-level-Loader                         debug
#notify-level-Messenger                      debug
#notify-level-MetaInterval                   debug
#notify-level-State                          debug
#notify-level-TaskManager                    debug
#notify-level-azure-camera                   debug
#notify-level-azure-controls                 debug

# ignore the next line. it's only for my editor ;)
# vim:set sw=4 ts=4 sts=4 et sta:

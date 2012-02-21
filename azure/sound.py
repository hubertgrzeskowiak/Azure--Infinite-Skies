"""Audio Management.
This module is unused.
"""

# builtins like base, loader and camera are all defined in
# direct.showbase.ShowBase.py

from direct.showbase.Audio3DManager import Audio3DManager
from direct.task import Task

audio3d = Audio3DManager(base.sfxManagerList[0], camera)
audio3d.setDropOffFactor(0.2)

def play3DSound(filename, emitter, loop=True):
    """Play sounds with 3D orientation. Arguments:
    filename -- path to the audio file (string)
    emitter -- nodepath, or at least something with a getPos() method
    loop -- how many times should the sound be played. default: infinite loop
    """
    sound = audio3d.loadSfx(filename)
    sound.setLoop(loop)
    sound.play()
    audio3d.attachSoundToObject(sound, emitter)
    return sound


class Jukebox(object):
    """Background music manager. Mount playlists in it and it plays all sound
    files in a row. There's only one playlist within one Jukebox."""

    def __init__(self, playlist=None):
        """Takes a playlist (list object) as optional argument."""
        self.__playlist = None
        if playlist:
            self.mountPlaylist(playlist)

        # 0 = playing, 1 = paused, 2 = stopped
        # also see method status()
        self.__status = 2
        # current/cursor
        self.__cur = 0
        self.__time = 0.0
        self.setCrossfade(3)
        taskMgr.add(self.__manager, "jukebox manager")

    def mountPlaylist(self, playlist, replace=True):
        """Arguments:
        playlist -- list of strings where the strings are paths to music files
        replace -- set to False to prevent eventual overwriting
        """
        if self.__playlist is None:
            self.__playlist = playlist
        elif replace is True:
            self.reset()
            self.__playlist = playlist
        else:
            pass
            #raise Error("cannot replace current playlist")

    def setCrossfade(self, fadetime):
        """The next song is already played when the current is n seconds
        from end."""
        self.crossfade = fadetime

    def query(self, song):
        """Add a song at the end of the current playlist.
        Arguments:
        song -- path to music file (string)
        """
        if self.__playlist:
            self.__playlist.append(song)

    def play(self, nr=None, time=None):
        """Arguments:
        nr -- song number to play (integer, starting from 0)
        time -- ...where playback should start (float)"""

        if time is None:
            time = self.__time

        if nr is not None:
            if nr not in range(0, len(self.__playlist)):
                raise OutOfRange("given track number is not in playlist")
                nr = 0
            if nr != self.__cur:
                time = 0.0
        else:
            nr = self.__cur

        if self.__status > 0:
            self.__song = loader.loadMusic(
                soundPath=self.__playlist[nr],
                )
                #cural=False, callback=True)
            self.__song.setTime(time)
            self.__time = 0.0
            self.__song.play()
            self.__status = 0

    def stop(self):
        self.__song.stop()
        self.__time = 0.0
        self.__status = 2

    def reset(self):
        """Stops playback and sets cursor to the first song in list."""
        self.stop()
        self.__cursor = 0

    def pause(self):
        # There's nothing like pause from panda, so we need to do it manually.
        self.__time = self.__song.getTime()
        self.__song.stop()
        self.__status = 1

    def next(self):
        self.stop()
        self.__cur += 1
        if self.__cur not in range(len(self.__playlist)):
            self.__cur = 0
        self.play()

    def check(self, playlist=None):
        """Check a playlist for being valid.

        Argument:
        playlist - list of filenames. the mounted one by default."""
        if playlist is None:
            playlist = self.__playlist
        # TODO
        pass

    def status(self, i=False):
        """Return status. Possible statuses are 'playing', 'paused' amd
        'stopped'.

        Arguments:
        i -- return an integer as status indicator
        """
        if i is True:
            return self.__status
        else:
            stat = ["playing", "paused", "stopped"]
            return stat[self.__status]

    def playlist(self):
        return self.__playlist

    def __manager(self, task):
        if self.__status < 2:
            if self.__song.length() - self.__song.getTime() <= self.crossfade:
                # TODO: fading/crossfade effect
                self.next()

        return Task.cont

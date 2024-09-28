""" Experimental module for subtitles support. """
import re
import numpy as np
from moviepy.tools import cvsecs
from moviepy.video.VideoClip import TextClip, VideoClip

class SubtitlesClip(VideoClip):
    """ A Clip that serves as "subtitle track" in videos.
    
    One particularity of this class is that the images of the
    subtitle texts are not generated beforehand, but only if
    needed.

    Parameters
    ==========

    subtitles
      Either the name of a file, or a list

    Examples
    =========
    
    >>> from moviepy.video.tools.subtitles import SubtitlesClip
    >>> from moviepy.video.io.VideoFileClip import VideoFileClip
    >>> generator = lambda txt: TextClip(txt, font='Georgia-Regular', fontsize=24, color='white')
    >>> sub = SubtitlesClip("subtitles.srt", generator)
    >>> myvideo = VideoFileClip("myvideo.avi")
    >>> final = CompositeVideoClip([clip, subtitles])
    >>> final.write_videofile("final.mp4", fps=myvideo.fps)
    
    """

    def __init__(self, subtitles, make_textclip=None):
        VideoClip.__init__(self, has_constant_size=False)
        if isinstance(subtitles, str):
            subtitles = file_to_subtitles(subtitles)
        self.subtitles = subtitles
        self.textclips = dict()
        if make_textclip is None:
            make_textclip = lambda txt: TextClip(txt, font='Georgia-Bold', fontsize=24, color='white', stroke_color='black', stroke_width=0.5)
        self.make_textclip = make_textclip
        self.start = 0
        self.duration = max([tb for (ta, tb), txt in self.subtitles])
        self.end = self.duration

        def add_textclip_if_none(t):
            """ Will generate a textclip if it hasn't been generated asked
            to generate it yet. If there is no subtitle to show at t, return
            false. """
            sub = [((ta, tb), txt) for (ta, tb), txt in self.textclips.keys() if ta <= t < tb]
            if not sub:
                sub = [((ta, tb), txt) for (ta, tb), txt in self.subtitles if ta <= t < tb]
                if not sub:
                    return False
            sub = sub[0]
            if sub not in self.textclips.keys():
                self.textclips[sub] = self.make_textclip(sub[1])
            return sub

        def make_frame(t):
            sub = add_textclip_if_none(t)
            return self.textclips[sub].get_frame(t) if sub else np.array([[[0, 0, 0]]])

        def make_mask_frame(t):
            sub = add_textclip_if_none(t)
            return self.textclips[sub].mask.get_frame(t) if sub else np.array([[0]])
        self.make_frame = make_frame
        hasmask = bool(self.make_textclip('T').mask)
        self.mask = VideoClip(make_mask_frame, ismask=True) if hasmask else None

    def in_subclip(self, t_start=None, t_end=None):
        """ Returns a sequence of [(t1,t2), txt] covering all the given subclip
        from t_start to t_end. The first and last times will be cropped so as
        to be exactly t_start and t_end if possible. """
        pass

    def __iter__(self):
        return iter(self.subtitles)

    def __getitem__(self, k):
        return self.subtitles[k]

    def __str__(self):

        def to_srt(sub_element):
            (ta, tb), txt = sub_element
            fta = cvsecs(ta)
            ftb = cvsecs(tb)
            return '%s - %s\n%s' % (fta, ftb, txt)
        return '\n\n'.join((to_srt(s) for s in self.subtitles))

def file_to_subtitles(filename):
    """ Converts a srt file into subtitles.

    The returned list is of the form ``[((ta,tb),'some text'),...]``
    and can be fed to SubtitlesClip.

    Only works for '.srt' format for the moment.
    """
    pass
multisplice
===========

A stupid little helper utility for automatically and losslessly splitting and splicing together portions of audio from multiple sources. Designed primarily for syncing audio to different versions of video.

Requires Python 2.7, [click](http://click.pocoo.org/), and mkvmerge from [MKVToolNix](https://www.bunkus.org/videotools/mkvtoolnix/). Also probably requires familiarity with AviSynth and AvsPmod if you actually want to sync anything.

Prerequisites
-----

Your audio tracks should use the same codec, sampling rate, and channel configuration. For some codecs (such as AC-3), the bitrate should be the same as well (or you'll get decode errors in players such as VLC). If your files have different format parameters, you may need to transcode them to match.

Your videos must have the same constant frame rate when syncing with AviSynth. If they are different, or one of them is variable, you must use `ChangeFPS` for CFR or your source filter's frame rate arguments (e.g. `fpsnum`/`fpsden` in `FFVideoSource`) for VFR.

Example
-------

Let's say we have two different versions of a video: a Japanese one and an English one. We want to sync the audio from the English version to the Japanese video. However, the English version is missing a few parts. To solve this, we'll create a new audio track that borrows audio from the Japanese version.

To find out which parts we need and from where, we write an AviSynth script that effectively syncs the English video to the Japanese video, taking parts from the Japanese video if needed.

    eng = FFVideoSource("foo_eng.mkv").FFInfo()
    jpn = FFVideoSource("foo_jpn.mkv").FFInfo()
    cuts = eng.Trim(3, 1200)      \
         + jpn.Trim(1198, 3378)   \
         + eng.Trim(1898, 30761)  \ 
         + jpn.Trim(32243, 34401) \
         + eng.Trim(32370, 32728)
    StackHorizontal(cuts, jpn)
  
After that's done, we demux the audio tracks and convert the trims to a *manifest file*.

	foo_{}.mka
	eng 3 1200
	jpn 1198 3378
	eng 1898 30761
	jpn 32243 34401
	eng 32370 32728
    
The first line is a "template" filename. For each line, multisplice will take the template and replace the `{}` with the first part of the line (e.g. `eng` to `foo_eng.mka`). The second part of each line is the trim points, measured in video frames (inclusive).

Then we let multisplice (actually mostly mkvmerge) do its magic:

	# ./multisplice.py -f 24000/1001 manifest.txt
    
The `-f` parameter specifies the frame rate at which to convert the trim points into timestamps. Since our videos are NTSC film (approximately 23.976 frames per second), we use `24000/1001`.

By default, the output is saved to a filename based on the template, with the asterisk replaced with "spliced" (in this case, the output filename is `foo_spliced.mka`). You can also use the `-o` parameter to specify a filename.

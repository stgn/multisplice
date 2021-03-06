#!/usr/bin/env python

import os, re
import click
from subprocess import call
from collections import defaultdict
from datetime import timedelta
from fractions import Fraction

@click.command()
@click.option('--fps', '-f', default='30000/1001', metavar='FRAMERATE', 
              help='Frame rate to convert frame numbers to timestamps at '
                   'as a float or fraction. Defaults to 30000/1001.')
@click.option('--dirty', '-d', is_flag=True, 
              help='Don\'t delete intermediate split files.')
@click.option('--output', '-o', metavar='FILENAME', 
              help='Output filename of spliced result.')
@click.argument('manifest', type=click.File())

def multisplice(manifest, fps, output, dirty):
    """Splices together portions of audio from multiple source files, as specified by a MANIFEST file."""
    
    tmpl = manifest.readline().rstrip('\r\n')
    out = output or os.path.splitext(tmpl.format('spliced'))[0] + '.mka'
    
    parts = []
    for line in manifest:
        m = re.search(r'(\S+) (\d+) (\d+)', line)
        if m:
            p = m.groups()
            parts.append((tmpl.format(p[0]), (int(p[1]), int(p[2]) + 1)))
        else:
            raise Exception('Unable to parse manifest')
            
    agg = defaultdict(list)
    for f, r in parts:
        agg[f].append(r)
    
    files = [('_{}' + '-{:03d}' * (len(agg[f]) > 1) + '.mka').format(f, agg[f].index(r) + 1) for f, r in parts]
                
    try:
        ft = 1 / Fraction(fps)
        for f, fr in agg.iteritems():
            arg = ','.join('-'.join(str(timedelta(seconds=float(ft * t))) for t in r) for r in fr)
            if call(['mkvmerge', '-q', f, '-o', '_{}.mka'.format(f), '--split', 'parts:' + arg]) > 1:
                raise Exception('{}: Split failed'.format(f))
            
        join_files = ['+' * (i > 0) + f for i, f in enumerate(files)]
        if call(['mkvmerge', '-q', '-o', out] + join_files) > 1:
            raise Exception('Splice failed')
    finally:
        if not dirty:
            for f in filter(os.path.isfile, files):
                os.remove(f)
        
if __name__ == '__main__':
    multisplice()
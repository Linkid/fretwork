#!/usr/bin/env python
#####################################################################
#                                                                   #
# Fretwork                                                          #
# Copyright (C) 2009-2015 FoFiX Team                                #
#                                                                   #
# This program is free software; you can redistribute it and/or     #
# modify it under the terms of the GNU General Public License       #
# as published by the Free Software Foundation; either version 2    #
# of the License, or (at your option) any later version.            #
#                                                                   #
# This program is distributed in the hope that it will be useful,   #
# but WITHOUT ANY WARRANTY; without even the implied warranty of    #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the     #
# GNU General Public License for more details.                      #
#                                                                   #
# You should have received a copy of the GNU General Public License #
# along with this program; if not, write to the Free Software       #
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,        #
# MA  02110-1301, USA.                                              #
#####################################################################

from setuptools import setup, Extension
from Cython.Build import cythonize
import sys, os, glob
import subprocess
import shlex


def find_command(cmd):
    '''Find a program on the PATH, or, on win32, in the dependency pack.'''

    sys.stdout.write('checking for program %s... ' % cmd)

    if os.name == 'nt':
        # Only accept something from the dependency pack.
        path = os.path.join('.', 'win32', 'deps', 'bin', cmd+'.exe')
    else:
        # Search the PATH.
        path = None
        for dir in os.environ['PATH'].split(os.pathsep):
            if os.access(os.path.join(dir, cmd), os.X_OK):
                path = os.path.join(dir, cmd)
                break

    if path is None or not os.path.isfile(path):
        print('not found')
        sys.stderr.write('Could not find required program "%s".\n' % cmd)
        if os.name == 'nt':
            sys.stderr.write('(Check that you have the latest version of the dependency pack installed.)\n')
        sys.exit(1)

    print(path)
    return path


# Find pkg-config so we can find the libraries we need.
pkg_config = find_command('pkg-config')


def pc_exists(pkg):
    '''Check whether pkg-config thinks a library exists.'''
    if os.spawnl(os.P_WAIT, pkg_config, 'pkg-config', '--exists', pkg) == 0:
        return True
    else:
        return False

# Blacklist MinGW-specific dependency libraries on Windows.
if os.name == 'nt':
    lib_blacklist = ['m', 'mingw32']
else:
    lib_blacklist = []


def pc_info(pkg, altnames=[]):
    '''Obtain build options for a library from pkg-config and
    return a dict that can be expanded into the argument list for
    L{distutils.core.Extension}.'''

    sys.stdout.write('checking for library %s... ' % pkg)
    if not pc_exists(pkg):
        for name in altnames:
            if pc_exists(name):
                pkg = name
                sys.stdout.write('(using alternative name %s) ' % pkg)
                break
        else:
            print('not found')
            sys.stderr.write('Could not find required library "%s".\n' % pkg)
            sys.stderr.write('(Also tried the following alternative names: %s)\n' % ', '.join(altnames))
            if os.name == 'nt':
                sys.stderr.write('(Check that you have the latest version of the dependency pack installed.)\n')
            else:
                sys.stderr.write('(Check that you have the appropriate development package installed.)\n')
            sys.exit(1)

    cflags = shlex.split(subprocess.check_output([pkg_config, '--cflags', pkg]))
    libs = shlex.split(subprocess.check_output([pkg_config, '--libs', pkg]))


    # Pick out anything interesting in the cflags and libs, and
    # silently drop the rest.
    def def_split(x):
        pair = list(x.split('=', 1))
        if len(pair) == 1:
            pair.append(None)
        return tuple(pair)
    info = {
      'define_macros': [def_split(x[2:]) for x in cflags if x[:2] == '-D'],
      'include_dirs': [x[2:] for x in cflags if x[:2] == '-I'],
      'libraries': [x[2:] for x in libs if x[:2] == '-l' and x[2:] not in lib_blacklist],
      'library_dirs': [x[2:] for x in libs if x[:2] == '-L'],
    }

    print('ok')
    return info


def combine_info(*args):
    '''Combine multiple result dicts from L{pc_info} into one.'''

    info = {
      'define_macros': [],
      'include_dirs': [],
      'libraries': [],
      'library_dirs': [],
    }

    for a in args:
        info['define_macros'].extend(a.get('define_macros', []))
        info['include_dirs'].extend(a.get('include_dirs', []))
        info['libraries'].extend(a.get('libraries', []))
        info['library_dirs'].extend(a.get('library_dirs', []))

    return info


vorbisfile_info = pc_info('vorbisfile')
sdl_info = pc_info('sdl')
sdl_mixer_info = pc_info('SDL_mixer')
glib_info = pc_info('glib-2.0')
gthread_info = pc_info('gthread-2.0')
soundtouch_info = pc_info('soundtouch', ['soundtouch-1.4', 'soundtouch-1.0'])
if os.name == 'nt':
    # And glib needs a slight hack to work correctly.
    glib_info['define_macros'].append(('inline', '__inline'))
    # And we use the prebuilt soundtouch-c.
    soundtouch_info['libraries'].append('soundtouch-c')
    extra_soundtouch_src = []
else:
    # And build our own soundtouch-c.
    extra_soundtouch_src = ['fretwork/mixstream/soundtouch-c.cpp']


mixstreamSource = [
    'fretwork/mixstream/_MixStream.pyx',
    'fretwork/mixstream/MixStream.c',
    'fretwork/mixstream/vorbis.c']

mixstreamSource.extend(extra_soundtouch_src)

mixstreamExt = Extension('fretwork.mixstream._MixStream', mixstreamSource,
    **combine_info(vorbisfile_info, soundtouch_info, glib_info, gthread_info, sdl_info, sdl_mixer_info))

setup(name='fretwork',
        version='0.0.1',
        description='Game library used by FoFiX, and FoF:R.',
        author='Matthew Sitton',
        author_email='matthewsitton@gmail.com',
        license='GPLv2+',
        url='https://github.com/fofix',
        packages=['fretwork', 'fretwork.mixstream'],
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: Developers',
            'Topic :: Multimedia :: Graphics',
            'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',

            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
        ],
        keywords='music engine fofix frets game',
        install_requires=['Pillow', 'cython', 'pygame', 'OpenGL', 'numpy'],
        ext_modules=cythonize(mixstreamExt)
     )
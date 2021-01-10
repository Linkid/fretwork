#!/bin/bash

echo $1
operating_system=$(echo "$1" | tr '[:upper:]' '[:lower:]')

case ${operating_system} in
    "linux")
        echo "Linux…"
        if [[ `arch` == 'i686' ]]
        then
            basearch=i386
        else
            basearch=x86_64
        fi
        if [[ $( grep "release 6" /etc/redhat-release ) ]]
        then
            rpm -Uvh https://archives.fedoraproject.org/pub/archive/epel/6/$basearch/epel-release-6-8.noarch.rpm
        fi

        yum -y install \
            portmidi-devel \
            SDL_image-devel \
            SDL_mixer-devel \
            SDL_ttf-devel \
            SDL-devel \
            soundtouch-devel \
            libvorbis-devel
    ;;
    "macos")
        echo "MacOS…"
        brew update --quiet > /dev/null
        brew reinstall pkg-config
        brew install --quiet \
            libvorbis \
            portmidi \
            sdl \
            sdl_image \
            sdl_mixer \
            sdl_ttf \
            wget;
        wget https://www.surina.net/soundtouch/soundtouch-2.0.0.zip;
        unzip soundtouch-2.0.0.zip;
        cd soundtouch;
        ./bootstrap;
        ./configure;
        make;
        make install;
        cd ..;

        brew ls libvorbis
        which pkg-config
        ls -l $(which pkg-config)
        brew unlink pkg-config && brew link pkg-config
        echo $PKG_CONFIG_PATH
        export PKG_CONFIG_PATH=/usr/local/Cellar/libvorbis/1.3.7/lib/pkgconfig:${PKG_CONFIG_PATH}
        echo $PKG_CONFIG_PATH
    ;;
    *)
        echo "[*] no OS: " ${operating_system}
    ;;
esac

pip install cython

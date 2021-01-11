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
        brew install --quiet \
            libvorbis \
            portmidi \
            sdl \
            sdl_image \
            sdl_mixer \
            sdl_ttf \
            wget;
        #wget https://www.surina.net/soundtouch/soundtouch-2.0.0.zip;
        #unzip soundtouch-2.0.0.zip;
        #cd soundtouch;
        #./bootstrap;
        #./configure;
        #make;
        #make install;
        #cd ..;

        brew ls libvorbis
        brew ls libogg
        brew ls sdl
        brew ls sdl_image
        brew ls sdl_mixer
        brew ls glib
        echo "which pkg-config:" `which pkg-config`
        echo "copy"
        cp -rp /usr/local/Cellar/libvorbis/1.3.7/lib/pkgconfig/* /Users/appveyor/.gvm/pkgsets/go1.15.6/global/overlay/lib/pkgconfig/
        cp -rp /usr/local/Cellar/libogg/1.3.4/lib/pkgconfig/* /Users/appveyor/.gvm/pkgsets/go1.15.6/global/overlay/lib/pkgconfig/
        cp -rp /usr/local/Cellar/sdl/1.2.15_3/lib/pkgconfig/* /Users/appveyor/.gvm/pkgsets/go1.15.6/global/overlay/lib/pkgconfig/
        cp -rp /usr/local/Cellar/sdl_image/1.2.12_7/lib/pkgconfig/* /Users/appveyor/.gvm/pkgsets/go1.15.6/global/overlay/lib/pkgconfig/
        cp -rp /usr/local/Cellar/sdl_mixer/1.2.12_4/lib/pkgconfig/* /Users/appveyor/.gvm/pkgsets/go1.15.6/global/overlay/lib/pkgconfig/
        echo $PKG_CONFIG_PATH
        echo "list pkgconfig files"
        ls -l /Users/appveyor/.gvm/pkgsets/go1.15.6/global/overlay/lib/pkgconfig
        echo "list pkgconfig files in path"
        ls -l /Library/Frameworks/Mono.framework/Home/bin/pkg-config
        echo "ok"
    ;;
    *)
        echo "[*] no OS: " ${operating_system}
    ;;
esac

pip install cython

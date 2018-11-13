import os
import requests


def downloadFile(music):
    """下载文件"""
    music_url = music.musicInfo.music_url
    musicImg_url = music.musicInfo.albumImg_url
    musicFile_base_url = os.path.join('~', 'Music')
    musicImgFile_base_url = os.path.join('~', 'Pictures')

    musicFile_url = os.path.join(musicFile_base_url, (
        '%s - %s.mp3' % (music.singerName, music.songName)))
    musicFile_url = os.path.expanduser(musicFile_url)
    musicImgFile_url = os.path.join(musicImgFile_base_url, (
        '%s - %s.jpg' % (music.singerName, music.albumName)))
    musicImgFile_url = os.path.expanduser(musicImgFile_url)

    _file = requests.get(music_url)
    if _file.status_code is not 200:
        return False
    with open(musicFile_url, 'wb') as code:
        code.write(_file.content)
    _file = requests.get(musicImg_url)
    with open(musicImgFile_url, 'wb') as code:
        code.write(_file.content)
    return True
import requests
import json


class Music:
    """音乐类型"""
    def __init__(self, singerName, albumName, songName, songMid, mediaMid, albumMid):
        self.singerName = singerName
        self.albumName = albumName
        self.songName = songName
        self.songMid = songMid
        self.mediaMid = mediaMid
        self.albumMid = albumMid
        self.musicInfo = None

    def getMusicInfo(self, fileType=None):
        """获取歌曲信息"""
        typeList = [
            'M800',
            'M500',
        ]
        if fileType is None:
            fileType = typeList[0]
        elif int(fileType) <= len(typeList):
            fileType = typeList[int(fileType)]
        else:
            fileType = typeList[1]
        music_url = 'http://dl.stream.qqmusic.qq.com/%s%s.mp3?vkey=%s&guid=9391879250&fromtag=27'
        albumImg_url = 'https://y.gtimg.cn/music/photo_new/T002R500x500M000%s.jpg?max_age=2592000'
        songMid = self.songMid
        albumMid = self.albumMid
        mediaMid = self.mediaMid
        vkey = _getVkey(songMid, mediaMid)
        if len(vkey) == 0:
            vkey = _getVkey('003OUlho2HcRHC')
        music_url = music_url % (fileType, mediaMid, vkey)
        albumImg_url = albumImg_url % albumMid
        return MusicInfo(music_url, albumImg_url)


class MusicInfo:
    """歌曲文件的url和专辑图片url"""
    def __init__(self, music_url, albumImg_url):
        self.music_url = music_url
        self.albumImg_url = albumImg_url


def getMusicList(keyword, p):
    """获取搜索列表"""
    get_url = 'https://c.y.qq.com/soso/fcgi-bin/client_search_cp?new_json=1&aggr=1&cr=1&catZhida=1&p=%d&n=20&w=%s&format=jsonp&inCharset=utf8&outCharset=utf-8'
    get_url = get_url % (p, keyword)
    result = requests.get(get_url, timeout=1.5).text
    result = json.loads(result[9:-1])
    musicList = result['data']['song']['list']
    musics = []
    for item in musicList:
        albumName = item['album']['title']
        singerName = ''
        for singer in item['singer']:
            singerName += '/' + singer['title']
        singerName = singerName[1:]
        songName = item['title']
        songMid = item['mid']
        mediaMid = item['file']['media_mid']
        albumMid = item['album']['mid']
        musics.append(Music(
            singerName, albumName, songName, songMid, mediaMid, albumMid))
    return musics


def _getVkey(songMid, mediaMid=None):
    """获取Vkey"""
    if mediaMid is None:
        mediaMid = songMid
    get_url = 'https://c.y.qq.com/base/fcgi-bin/fcg_music_express_mobile3.fcg?g_tk=5381&loginUin=0&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq&needNewCode=0&cid=205361747&uin=0&songmid=%s&filename=M500%s.mp3&guid=9391879250'
    get_url = get_url % (songMid, mediaMid)
    result = requests.get(get_url, timeout=1.5).text
    result = json.loads(result)
    return result['data']['items'][0]['vkey']

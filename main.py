from argparse import ArgumentParser
from os import getcwd
from os import remove as _remove
from os import system as _system
from os.path import exists as _exists
from textwrap import dedent
from typing import Dict, Optional, Tuple
from urllib.parse import quote_plus

from mutagen.easyid3 import ID3, EasyID3
from mutagen.id3 import APIC as AlbumCover
from pytube import YouTube
from youtube_search import YoutubeSearch

from classes import AuthCreds, ClearScreen, Colors, SpotifyAPI


class Runner(SpotifyAPI, Colors):
    YOUTUBE_URL = 'https://youtube.com'

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        bitrate: int=320
        ):

        super().__init__(client_id, client_secret)
        self.bitrate = bitrate

    def process_query(
        self,
        query: str
        ):

        track_id = self.get_track_id(query)
        if track_id is not None:
            self.process_spotify_track(track_id)
        else:
            self.process_youtube_track(query)

    def process_youtube_track(
        self,
        query: str
        ):

        print(f'{self.RED}✖{self.END} Song is not found in Spotify Database! Searching in YouTube...\n')
        youtube_song_url, results = self.search_youtube(query)
        audio_name, converted_name = self.convert_file_path(results[0]['title'])

        print(f'\n{self.WHITE}Title{self.END} : {self.LBLUE}{audio_name}{self.END}\n')

        if _exists(converted_name):
            print(f'{self.GREEN}📍Song Downloaded Already!{self.END}\n')
        else:
            if self.confirm_download():
                downloaded_audio = self.download_youtube(youtube_song_url, audio_name)
                self.convert_320(downloaded_audio, converted_name)
                self.youtube_track_info(audio_name, converted_name, downloaded_audio)

    def process_spotify_track(
        self,
        track_id: str
        ):

        data = self.track_id_data(track_id)
        audio_name, converted_name = self.convert_file_path(f'{self.get_artists(data)} - {self.get_title(data)}')

        print(dedent(f'''
            {self.WHITE}Title{self.END}         : {self.LBLUE}{self.get_title(data)}
            {self.WHITE}Artist{self.END}        : {self.LBLUE}{self.get_artists(data)}
            {self.WHITE}Album{self.END}         : {self.LBLUE}{self.get_album_name(data)}
            {self.WHITE}Album Artist{self.END}  : {self.LBLUE}{self.get_album_artists(data)}
            {self.WHITE}Genres{self.END}        : {self.LBLUE}{self.get_genres(data)}
            {self.WHITE}Release Date{self.END}  : {self.LBLUE}{self.get_release_year(data)}
            {self.WHITE}Disc Number{self.END}   : {self.LBLUE}{self.get_disc_number(data)}
            {self.WHITE}Track Number{self.END}  : {self.LBLUE}{self.get_track_number(data)}
        '''))

        if _exists(converted_name):
            print(f'{self.GREEN}📍Song Downloaded Already!{self.END}\n')
        else:
            if self.confirm_download():
                youtube_song_url = self.search_youtube(audio_name)[0]
                downloaded_audio = self.download_youtube(youtube_song_url, audio_name)
                self.convert_320(downloaded_audio, converted_name)
                self.spotify_track_info(downloaded_audio, converted_name, data)

    def convert_file_path(
        self,
        audio_name: str
        ) -> Tuple[str, str]:

        converted_name = f'./{audio_name}.mp3'
        return audio_name, converted_name

    def search_youtube(
        self,
        query: str
        ) -> Tuple[str, list | str]:

        with self.SPINNER as status:
            status.start('Please wait! Searching Song in YouTube..')
            results = YoutubeSearch(query).to_dict()
            youtube_song_url = f'{self.YOUTUBE_URL}/{str(results[0]["url_suffix"])}'
            status.succeed('Succeed! Song Founded!')
        return youtube_song_url, results

    def download_youtube(
        self,
        youtube_song_url: str,
        audio_name: str
        ) -> str:

        with self.SPINNER as status:
            status.start('Please wait! Downloading Song..')
            yt = YouTube(youtube_song_url)
            downloaded_audio = yt.streams.get_audio_only().download(filename=audio_name, skip_existing=False)
            status.succeed('Succeed! Song Downloaded!')
        return downloaded_audio

    def convert_320(
        self,
        downloaded_audio: str,
        converted_name: str
        ):

        with self.SPINNER as status:
            status.start(f'Converting to mp3 with {self.bitrate}kpbs bitrate ..')
            command = f'ffmpeg -v quiet -y -i "{downloaded_audio}" -acodec libmp3lame -abr true -af "apad=pad_dur=2" -vn -sn -dn -b:a {self.bitrate}k "{converted_name}"'
            _system(command)
            status.succeed('Succeed! MP3 320bitrate Converted!')

    def save_track_info(
        self,
        audio_file: EasyID3,
        downloaded_audio: str,
        metadata_dict: Dict[str, str]
        ):

        with self.SPINNER as status:
            status.start('Please wait! Saving Track Info ..')
            audio_file.delete()
            audio_file.update(metadata_dict)
            audio_file.save(v2_version=3)
            status.succeed('Succeed! Track Info Saved!')
            _remove(downloaded_audio)

    def youtube_track_info(
        self,
        audio_name: str,
        converted_name: str,
        downloaded_audio: str
        ):

        metadata_dict = {
            'title': audio_name
        }
        audio_file = EasyID3(converted_name)
        self.save_track_info(audio_file, downloaded_audio, metadata_dict)

        print(f'\n📍Saved in {self.BGREEN}{getcwd()}\{self.BYELLOW}{converted_name[2:]}{self.END} 🎶\n')


    def spotify_track_info(
        self,
        downloaded_audio: str,
        converted_name: str,
        data: Dict[str, str]):

        metadata_dict = {
            'title': self.get_title(data),
            'tracknumber': self.get_track_number(data),
            'artist': self.get_artists(data),
            'album': self.get_album_name(data),
            'genre': self.get_genres(data),
            'albumartist': self.get_album_artists(data),
            'originaldate': self.get_release_year(data)
        }
        audio_file = EasyID3(converted_name)
        self.save_track_info(audio_file, downloaded_audio, metadata_dict)

        audio_file = ID3(converted_name)
        audio_file['APIC'] = AlbumCover(encoding=3, mime='image/jpeg', type=3, desc='Album Art', data=self.get_album_image(data))
        audio_file.save(v2_version=3)

        print(f'\n📍Saved in {self.BGREEN}{getcwd()}\{self.BYELLOW}{converted_name[2:]}{self.END} 🎶\n')


    def confirm(
        self,
        prompt: str
        ) -> bool:

        while True:
            answer = input(prompt).lower()
            if answer == 'y':
                return True
            elif answer == 'n':
                return False
            else:
                print(f"\n{self.RED}Invalid input!{self.END} Please enter '{self.GREEN}y{self.END}' or '{self.RED}n{self.END}'.\n")

    def search_again(
        self
        ) -> bool:

        search_again = self.confirm('Do you want to search again? (y/n): ')
        print()
        return search_again

    def confirm_download(
        self
        ) -> bool:

        confirm_download = self.confirm('Do you want to download this song? (y/n): ')
        print()
        return confirm_download

    def get_query(
        self,
        user_query: Optional[str]
        ) -> str:

        if user_query is not None:
            query = user_query
        else:
            query = input(
                f'\n{self.GREEN}[{self.WHITE}INFO{self.GREEN}]{self.END} Type \'stop\' to exit the program..\nThe track title and artist / Spotify URL: '
            )
            print()
        return quote_plus(query)

    def program(
        self,
        user_query: Optional[str]
        ):

        while True:
            query = self.get_query(user_query)
            if query.lower() == 'stop':
                break
            self.process_query(query)
            user_query = None
            if not self.search_again():
                break
            ClearScreen()


def run_app():
    parser = ArgumentParser()
    parser.add_argument('query', nargs='?', help='The track title and artist / Spotify URL')
    args = parser.parse_args()

    ClearScreen()
    user_query = args.query
    config = AuthCreds.get_configuration()

    if config.get('CLIENT_ID') and config.get('CLIENT_SECRET'):
        run = Runner(client_id=config['CLIENT_ID'], client_secret=config['CLIENT_SECRET'])
        run.program(user_query)

if __name__ == "__main__":
    run_app()

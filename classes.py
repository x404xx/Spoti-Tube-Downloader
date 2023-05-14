from base64 import b64encode
from json import JSONDecodeError, dump, load
from os import getenv
from os import name as _name
from os import system as _system
from textwrap import dedent
from typing import Dict, Literal, LiteralString
from urllib.parse import unquote

from dotenv import load_dotenv
from halo import Halo
from requests import Session
from spinners import Spinners


class ClearScreen:
    def __init__(self):
        _system('cls' if _name == 'nt' else 'clear')


class Colors:
    BLUE = '\033[38;5;45m'
    LBLUE = '\033[38;2;134;162;255m'
    GREEN = '\033[38;2;171;255;168m'
    BGREEN = '\033[38;5;46m'
    RED = '\033[38;5;196m'
    WHITE = '\033[38;5;255m'
    YELLOW = '\033[38;5;193m'
    BYELLOW = '\033[38;5;226m'
    END = '\033[0m'


class MusicInfo:
    def get_image_url(
        self,
        data: Dict[str, str]
        ) -> str:

        return data['album']['images'][0]['url']

    def get_title(
        self,
        data: Dict[str, str]
        ) -> str:

        return data['name']

    def get_album_artists(
        self,
        data: Dict[str, str]
        ) -> LiteralString:

        return ', '.join(item['name'] for item in data['album']['artists'])

    def get_artists(
        self,
        data: Dict[str, str]
        ) -> LiteralString:

        return ', '.join(item['name'] for item in data['artists'])

    def get_album_name(
        self,
        data: Dict[str, str]
        ) -> str:

        return data['album']['name']

    def get_track_number(
        self,
        data: Dict[str, str]
        ) -> str:

        return str(data['track_number'])

    def get_disc_number(
        self,
        data: Dict[str, str]
        ) -> str:

        return str(data['disc_number'])

    def get_release_year(
        self,
        data: Dict[str, str]
        ) -> str:

        return str(data['album']['release_date'].split('-')[0])

    def get_genres(
        self,
        data: Dict[str, str]
        ) -> (LiteralString | Literal['unknown']):

        genres = [genre for artist in data.get('artists', []) for genre in artist.get('genres', [])]
        genres += data.get('album', {}).get('genres', [])
        return ', '.join(genres) if genres else 'Unknown'


class SpotifyAPI(MusicInfo):
    BASE_URL = 'https://api.spotify.com/v1'
    TOKEN_URL = 'https://accounts.spotify.com/api/token'
    SPINNER = Halo(text_color='green', spinner=Spinners['point'].value, color='magenta')

    def __init__(
        self,
        client_id: str,
        client_secret: str
        ):

        self.client = Session()
        self.headers = {'Authorization': f'Bearer {self.get_token(client_id, client_secret)}'}

    def __del__(self):
        self.client.close()

    def get_token(
        self,
        client_id: str,
        client_secret: str
        ) -> str:

        client_creds = f'{client_id}:{client_secret}'
        creds_bytes = client_creds.encode('ascii')
        encoded_creds_bytes = b64encode(creds_bytes)
        encoded_creds_str = encoded_creds_bytes.decode('ascii')
        with self.SPINNER as status:
            status.start('Please wait! Getting Token ..')
            response = self.client.post(
                self.TOKEN_URL,
                headers={'Authorization': f'Basic {encoded_creds_str}'},
                data={'grant_type': 'client_credentials'},
            )
            response.raise_for_status()
            status.succeed('Succeed! Token Founded!')
        return response.json()['access_token']

    def search_track_id(
        self,
        track_name: str
        ) -> (str | None):

        search_url = f'{self.BASE_URL}/search'
        params = {'q': track_name, 'type': 'track'}
        with self.SPINNER as status:
            status.start('Please wait! Searching Track ID ..')
            response = self.client.get(search_url, headers=self.headers, params=params)
            response.raise_for_status()
            tracks = response.json()['tracks']['items']
            if not tracks:
                return None
            status.succeed('Succeed! Track ID Founded!')
        return tracks[0]['id']

    def get_track_id(
        self,
        track_uri: str
        ) -> (str | None):

        if 'spotify.com' in track_uri:
            return unquote(track_uri).split('/')[-1]
        return self.search_track_id(track_uri)

    def get_album_image(
        self,
        data: Dict[str, str]
        ) -> bytes:

        image_url = self.get_image_url(data)
        with self.SPINNER as status:
            status.start('Please wait! Getting Album Image ..')
            response = self.client.get(image_url)
            response.raise_for_status()
            status.succeed('Succeed! Album Image Saved!')
        return response.content

    def track_id_data(
        self,
        track_id: str
        ) -> Dict[str, str]:

        track_url = f'{self.BASE_URL}/tracks/{track_id}'
        with self.SPINNER as status:
            status.start('Please wait! Searching Track in Spotify database..')
            response = self.client.get(url=track_url, headers=self.headers)
            response.raise_for_status()
            status.succeed('Succeed! Track Founded!')
        return response.json()


class AuthCreds:
    MISSING_CONFIG = dedent("""
    ⚠️  Could not find CLIENT_ID and CLIENT_SECRET in environment variables or configuration.
    ⚠️  Please choose one of the following options:
        [1] Manually enter CLIENT_ID and CLIENT_SECRET
        [2] Exit
    """)

    @staticmethod
    def user_choice(config: Dict[str, str]):
        while True:
            user_choice = input('Enter your choice: ')
            print()
            if user_choice == '2':
                exit()
            elif user_choice == '1':
                config.update({
                    'CLIENT_ID': input('Enter CLIENT_ID: '),
                    'CLIENT_SECRET': input('Enter CLIENT_SECRET: '),
                })
                break
            else:
                print('Wrong input! Please check your value!')

    @staticmethod
    def get_configuration() -> Dict[str, str]:
        try:
            with open('spot_auth.json', 'r') as file:
                return load(file)
        except (FileNotFoundError, JSONDecodeError):
            config = {}

        load_dotenv()
        config['CLIENT_ID'] = getenv('CLIENT_ID')
        config['CLIENT_SECRET'] = getenv('CLIENT_SECRET')

        if not config.get('CLIENT_ID') or not config.get('CLIENT_SECRET'):
            print(AuthCreds.MISSING_CONFIG)
            AuthCreds.user_choice(config)
            with open('spot_auth.json', 'w') as file:
                dump(config, file, indent=4)
                print('\n"spot_auth.json" file has been created successfully.\n')

        return config

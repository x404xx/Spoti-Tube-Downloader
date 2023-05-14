<div align="center">

# Spoti-Tube

**Spoti-Tube** finds songs from Spotify using track title - artist, or URL and downloads them from YouTube, along with album art, and metadata.

<img src="https://github.com/x404xx/Spoti-Tube-Downloader/assets/114883816/eb9ca36a-4140-4cc0-8c51-7d3ea8cb268e" width="400" height="280">

</div>

## **Installing FFmpeg**

FFmpeg is required for _Spoti-Tube_.

-   [Windows Tutorial](https://windowsloop.com/install-ffmpeg-windows-10/)

## **Spotify Credentials**

Spotifys Credential is required for _Spoti-Tube_.

-   You can get it from the [Spotify Website](https://developer.spotify.com/documentation/web-api/concepts/apps)

> **Note**
> After obtaining a Client-ID and Client-Secret, you can save them somewhere and then run the program. By default, the program will ask you for a Client-ID and Client-Secret and make the JSON file automatically for you. Alternatively, you can create the .env or JSON file (**_spot_auth.json_**) manually.

## **Usage**

To use _Spoti-Tube_, open your terminal and navigate to the folder that contains _Spoti-Tube_ content ::

```sh
pip install -r requirements.txt
```

Using _Spoti-Tube_ with command-line ::

```sh
python main.py 'instant crush daftpunk'
```

-   or you can use the URL directly.

```sh
python main.py 'https://open.spotify.com/track/0f8GgsD1lDtRBAS5GEDKgg'
```

Alternatively, you can run _Spoti-Tube_ without command-line, and it will prompt you for the input track title - artist ::

```sh
python main.py
```

## **Music Sourcing and Audio Quality**

_Spoti-Tube_ uses YouTube as a source for music downloads. This method is used to avoid any issues related to downloading music from Spotify.

> **Note**
> This was made for educational purposes only, nobody who is directly involved in this project is responsible for any damages caused. **_You are responsible for your actions._**

### **Audio Quality**

_Spoti-Tube_ downloads music from YouTube and is designed to always download the highest bitrate; which is 320 kbps using FFmpeg conversion.

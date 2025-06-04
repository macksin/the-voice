# The Voice

A lightweight Flask application that converts text to speech using the [edge-tts](https://github.com/rany2/edge-tts) library. It offers text cleanup tools and lets you download the resulting audio.

![Application Interface](docs/app-interface.png)

## Features

- Select from Microsoft Edge voices ("Ava" is the default).
- Fix line breaks, hyphenation and extra spaces in your text.
- Preview and download each generated MP3 with subtitles.
- History panel stores recent conversions and files are cleaned after an hour.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start the app:

```bash
python app.py
```

Open <http://localhost:5000> in your browser.

## License

This project is licensed under the Apache 2.0 License. See the [LICENSE](LICENSE) file for details.

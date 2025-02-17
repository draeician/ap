# AtomicParsley Wrapper (ap)

A Python-based command-line wrapper for AtomicParsley that simplifies metadata manipulation for media files.

## Features

- View and modify metadata in media files (MP4, M4V)
- Set various metadata fields including title, year, TV show information, and more
- Set IMDb and TheTVDB IDs
- Perform deep scans for metadata
- Remove encoding tool metadata
- Wipe all metadata
- Simple command-line interface

## Prerequisites

- Python 3.6 or higher
- AtomicParsley (must be installed and available in PATH)
- pipx (recommended for installation)

## Installation

### Using pipx (Recommended)

```bash
pipx install ap-wrapper
```

### Manual Installation

```bash
git clone https://github.com/Draeician/ap.git
cd ap
pip install .
```

## Usage

```bash
ap [options] [files]
```

### Options

| Option | Description |
|--------|-------------|
| `-t` | View existing metadata |
| `--title TEXT` | Set the Title metadata |
| `--year TEXT` | Set the Year metadata |
| `--episode TEXT` | Set the TV Episode Number metadata |
| `--season TEXT` | Set the TV Season Number metadata |
| `--show TEXT` | Set the TV Show Name metadata |
| `--genre TEXT` | Set the genre metadata |
| `--desc TEXT` | Set the description metadata |
| `--longdesc TEXT` | Set the long description metadata |
| `--advisory {clean,explicit}` | Set the advisory metadata |
| `--imdb TEXT` | Set the IMDb ID (e.g., tt11548850) |
| `--thetvdb TEXT` | Set the TheTVDB ID |
| `--DeepScan` | Perform a deep scan for metadata |
| `--notools` | Remove Encoding Tools metadata |
| `--wipe` | Wipe all metadata (ignores other metadata switches) |

### Examples

1. View metadata of a file:
```bash
ap -t video.mp4
```

2. Set title and year:
```bash
ap --title "My Movie" --year "2024" video.mp4
```

3. Set TV show information:
```bash
ap --show "My Show" --season "1" --episode "5" episode.mp4
```

4. Set IMDb ID:
```bash
ap --imdb "tt11548850" movie.mp4
```

5. Remove all metadata:
```bash
ap --wipe video.mp4
```

6. Process multiple files:
```bash
ap --title "Common Title" file1.mp4 file2.mp4
```

## Supported File Types

- MP4 (.mp4)
- M4V (.m4v)

## Notes

- The wrapper requires AtomicParsley to be installed and available in your system's PATH
- When using the `--wipe` option, all other metadata switches are ignored
- The tool will automatically ignore files with unsupported extensions
- Changes are always made with the `--overWrite` flag to modify files in place
- IMDb IDs should be in the format "tt" followed by numbers (e.g., tt11548850)

## License

MIT License

## Author

Draeician

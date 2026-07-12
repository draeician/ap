# AtomicParsley Wrapper - Development Notes

## Metadata Mapping Reference

This document provides a comprehensive mapping between the ap wrapper command line switches, AtomicParsley command switches, and the resulting metadata atoms.

### Command Line Switch Mappings

| ap Wrapper Switch | AtomicParsley Switch | Target Atom | Description |
|-------------------|---------------------|-------------|-------------|
| `--title` | `--title` | `"©nam"` | Video title |
| `--year` | `--year` | `"©day"` | Release year |
| `--episode` | `--TVEpisodeNum` | `"tves"` | TV episode number |
| `--season` | `--TVSeasonNum` | `"tvsn"` | TV season number |
| `--show` | `--TVShowName` | `"tvsh"` | TV show name |
| `--genre` | `--genre` | `"©gen"` | Genre(s) |
| `--desc` | `--longdesc` | `"ldes"` | Long description text |
| `--longdesc` | `--longdesc` | `"ldes"` | Long description text (alias) |
| `--url` | `--description` | `"desc"` | URL/description |
| `--advisory` | `--advisory` | `"rtng"` | Content advisory rating |
| `--imdb` | `--xID` | `"xid "` | IMDb ID |
| `--thetvdb` | `--xID` | `"xid "` | TheTVDB ID |
| `--notools` | `--encodingTool ""` | `"©too"` | Remove encoding tool info |

### AtomicParsley Raw Output Format

When using `AtomicParsley file.mp4 -t`, the output shows atoms in this format:
```
Atom "ATOM_NAME" contains: VALUE
```

### Metadata Atom Reference

| Atom Name | Description | Example Value | ap Field |
|-----------|-------------|---------------|----------|
| `"©nam"` | Title | `"Brynhildr In the Darkness s01e01"` | `title` |
| `"©day"` | Year | `"2014"` | `year` |
| `"tves"` | TV Episode | `"1"` | `episode` |
| `"tvsn"` | TV Season | `"1"` | `season` |
| `"tvsh"` | TV Show | `"Brynhildr In the Darkness"` | `show` |
| `"©gen"` | Genre | `"Mystery, Drama, Sci-Fi, Seinen"` | `genre` |
| `"ldes"` | Long Description | `"Venturing into the wilderness..."` | `desc` |
| `"desc"` | Description/URL | `"https://hianime.to/..."` | `url` |
| `"rtng"` | Content Rating | `"explicit"` | `advisory` |
| `"xid "` | External ID | `"IMDbID=tt1234567"` | `imdb`/`thetvdb` |
| `"©too"` | Encoding Tool | `"HandBrake 1.6.1"` | `encodingTool` |

### Special Cases

#### Multiple xID Values
The `--xID` switch can set multiple external IDs:
- `--xID "IMDbID=tt1234567"` → `"xid "` atom
- `--xID "TheTVDB=123456"` → `"xid "` atom

#### Content Advisory Values
The `--advisory` switch accepts:
- `"clean"` → `"rtng"` atom
- `"explicit"` → `"rtng"` atom

#### Genre Format
The `--genre` switch accepts comma-separated values:
- `"Mystery, Drama, Sci-Fi, Seinen"` → `"©gen"` atom

### Migration Logic

The wrapper includes migration logic to handle old metadata formats:

#### Old Format (Pre-commit ad07aa3c18dbbafba4efbee56642198cd62507f7)
- `"desc"` atom contained URL
- `"ldes"` atom contained description text

#### New Format (Post-commit ad07aa3c18dbbafba4efbee56642198cd62507f7)
- `"desc"` atom contains URL
- `"ldes"` atom contains description text

#### Migration Detection
The wrapper detects old format by checking if:
1. `"desc"` atom contains a URL pattern and no separate `"url"` field exists
2. `"longdesc"` field exists but no `"desc"` field exists

#### Migration Process
When old format is detected:
1. Move URL from `"desc"` atom to `"url"` field
2. Move description from `"longdesc"` field to `"desc"` field

### Mirror Mode (`-m` switch)

When using the mirror mode:
1. Read metadata from source file
2. Detect if migration is needed
3. Apply migration if necessary
4. Copy migrated metadata to target file(s)

### View Mode

View mode displays metadata in a user-friendly format:
- Shows all available metadata fields
- Does not apply migration (shows raw metadata as stored)
- Handles missing fields gracefully

### Common Issues

#### Description Not Showing
- **Cause**: Incorrect atom mapping in metadata parsing
- **Fix**: Ensure `"ldes"` atom maps to `desc` field, `"desc"` atom maps to `url` field

#### URL Not Showing
- **Cause**: Incorrect atom mapping in metadata parsing
- **Fix**: Ensure `"desc"` atom maps to `url` field

#### Migration Interference
- **Cause**: Migration logic applied in view mode
- **Fix**: Only apply migration in mirror mode (`-m` switch)

### Testing Commands

#### View Raw Metadata
```bash
AtomicParsley file.mp4 -t
```

#### View Processed Metadata
```bash
ap file.mp4
```

#### Set Description
```bash
ap --desc "Description text" file.mp4
```

#### Set URL
```bash
ap --url "https://example.com" file.mp4
```

#### Mirror Metadata
```bash
ap -m source.mp4 target.mp4
```

### Development Notes

- Always test changes with both raw AtomicParsley output and wrapper output
- Verify atom mappings match expected behavior
- Test migration logic with both old and new format files
- Ensure backward compatibility with existing metadata

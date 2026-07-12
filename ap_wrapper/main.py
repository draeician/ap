#!/usr/bin/env python3

import os
import argparse
import subprocess
import shlex
import sys
import re
from typing import List, Optional, Tuple

def is_valid_extension(file_name: str) -> bool:
    """Check if the file has a valid extension for AtomicParsley processing.

    Args:
        file_name: Name of the file to check

    Returns:
        bool: True if the file has a valid extension, False otherwise
    """
    extension = file_name.split('.')[-1] if '.' in file_name else ''
    return extension.lower() in ['mp4', 'm4v']


def upper_first(text: str) -> str:
    """Title-case the first letter of each word (meta_update.pl upper_first).

    Args:
        text: Input string

    Returns:
        str: String with each word's first character uppercased
    """
    # Perl: $tt =~ s/^/ /; $tt =~ s/\s(\w+)/ \u$1/g; $tt =~ s/^ //;
    padded = " " + text
    result = re.sub(r"\s(\w)", lambda m: " " + m.group(1).upper(), padded)
    return result[1:] if result.startswith(" ") else result


def parse_meta_filename(file_name: str) -> Optional[Tuple[str, str, str, str]]:
    """Parse show name, season, episode, and title from a filename.

    Matches meta_update.pl conventions, e.g.
    ``mobile_suit_gundam-the_origin-s01e01.mp4``.

    Args:
        file_name: Path or basename of a media file

    Returns:
        Optional tuple of (show_name, season, episode, title), or None if
        the trailing ``sNNeNN`` token is missing.
    """
    base = os.path.basename(file_name)
    # Strip extension (first '.' split, same as Perl split /\./)
    temp = base.split(".", 1)[0]
    temp_split = temp.split("-")

    if len(temp_split) > 2:
        name = "-".join(temp_split[0:-1])
    elif len(temp_split) >= 1:
        name = temp_split[0]
    else:
        return None

    name = name.replace("_", " ")

    se_match = re.search(r"s(\d+)e(\d+)", temp_split[-1], re.IGNORECASE)
    if not se_match:
        return None

    season = se_match.group(1)
    episode = se_match.group(2)

    name = upper_first(name)
    name = name.replace(" The", " the")
    title = f"{name} s{int(season):02d}e{int(episode):02d}"
    return name, season, episode, title


def build_meta_command(
    cmd: str,
    file: str,
    show: str,
    season: str,
    episode: str,
    title: str,
) -> List[str]:
    """Build AtomicParsley argv for meta_update.pl-equivalent tagging.

    Args:
        cmd: AtomicParsley binary name/path
        file: Target media file
        show: TV show name
        season: Season number string
        episode: Episode number string
        title: Episode title string

    Returns:
        List[str]: Command argument list
    """
    return [
        cmd,
        file,
        "--title",
        title,
        "--TVShowName",
        show,
        "--TVSeasonNum",
        season,
        "--TVEpisodeNum",
        episode,
        "--overWrite",
        "--encodingTool",
        "",
    ]


def is_url(text: str) -> bool:
    """Check if text looks like a URL.
    
    Args:
        text: Text to check
        
    Returns:
        bool: True if text appears to be a URL
    """
    if not text:
        return False
    
    # Simple URL detection - check for common URL patterns
    url_patterns = [
        r'^https?://',  # http:// or https://
        r'^www\.',      # www.
        r'^ftp://',     # ftp://
        r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',  # domain.com pattern
    ]
    
    for pattern in url_patterns:
        if re.match(pattern, text.strip()):
            return True
    
    return False

def needs_metadata_migration(metadata: dict) -> bool:
    """Determine if metadata migration is needed based on content analysis.
    
    The migration is needed if the metadata appears to be in the old format:
    - Old format: desc field contains URL, longdesc field contains description
    - New format: desc field contains description, url field contains URL
    
    Args:
        metadata: Metadata dictionary to analyze
        
    Returns:
        bool: True if migration is needed, False otherwise
    """
    # Check if we have old-style data that needs migration
    desc_value = metadata.get('desc', '')
    url_value = metadata.get('url', '')
    longdesc_value = metadata.get('longdesc', '')
    
    # If desc contains a URL and we don't have a separate url field, it's old format
    if desc_value and is_url(desc_value) and not url_value:
        return True
    
    # If we have longdesc but no desc, it's old format
    if longdesc_value and not desc_value:
        return True
    
    return False

def migrate_metadata(metadata: dict) -> dict:
    """Migrate metadata fields from old format to new format.
    
    Old format: desc=URL, longdesc=description
    New format: desc=description, url=URL
    
    Args:
        metadata: Original metadata dictionary
        
    Returns:
        dict: Migrated metadata dictionary
    """
    migrated = metadata.copy()
    
    # Check if we have old-style data that needs migration
    desc_value = migrated.get('desc', '')
    url_value = migrated.get('url', '')
    longdesc_value = migrated.get('longdesc', '')
    
    # If desc contains a URL and we don't have a separate url field, migrate it
    if desc_value and is_url(desc_value) and not url_value:
        # Move URL from desc to url field
        migrated['url'] = desc_value
        del migrated['desc']
    
    # If we have longdesc but no desc, move longdesc to desc
    if longdesc_value and not migrated.get('desc'):
        migrated['desc'] = longdesc_value
        del migrated['longdesc']
    
    return migrated

def get_metadata(cmd: str, file: str) -> dict:
    """Get metadata from a file using AtomicParsley.

    Args:
        cmd: Base command (AtomicParsley)
        file: File to get metadata from

    Returns:
        dict: Dictionary of metadata values
    """
    result = subprocess.run([cmd, file, "-t"], capture_output=True, text=True)
    metadata = {}
    
    if result.returncode == 0:
        output = result.stdout
        # Parse metadata from output
        for line in output.splitlines():
            # Handle atom-style output (when using just AtomicParsley file -t)
            if '"©gen"' in line and "contains:" in line:
                metadata["genre"] = line.split("contains:")[1].strip()
            elif '"desc"' in line and "contains:" in line:
                # The desc atom contains the URL
                metadata["url"] = line.split("contains:")[1].strip()
            elif '"ldes"' in line and "contains:" in line:
                # The ldes atom contains the description
                metadata["desc"] = line.split("contains:")[1].strip()
            elif '"©day"' in line and "contains:" in line:
                metadata["year"] = line.split("contains:")[1].strip()
            elif '"©nam"' in line and "contains:" in line:
                metadata["title"] = line.split("contains:")[1].strip()
            elif '"tvnn"' in line and "contains:" in line:
                metadata["show"] = line.split("contains:")[1].strip()
            elif '"tves"' in line and "contains:" in line:
                metadata["episode"] = line.split("contains:")[1].strip()
            elif '"tvsn"' in line and "contains:" in line:
                metadata["season"] = line.split("contains:")[1].strip()
            elif '"©too"' in line and "contains:" in line:
                metadata["encodingTool"] = line.split("contains:")[1].strip()
            # Handle --textdata style output (with =>)
            elif "TVEpisodeNum" in line and "=>" in line:
                metadata["episode"] = line.split("=>")[1].strip()
            elif "TVSeasonNum" in line and "=>" in line:
                metadata["season"] = line.split("=>")[1].strip()
            elif "TVShowName" in line and "=>" in line:
                metadata["show"] = line.split("=>")[1].strip()
            elif "Genre" in line and "=>" in line:
                metadata["genre"] = line.split("=>")[1].strip()
            elif "Description" in line and "=>" in line:
                metadata["desc"] = line.split("=>")[1].strip()
            elif "Long Description" in line and "=>" in line:
                metadata["longdesc"] = line.split("=>")[1].strip()
            elif "Rating Tool" in line and "=>" in line:
                metadata["advisory"] = line.split("=>")[1].strip()
            elif "Title" in line and "=>" in line:
                metadata["title"] = line.split("=>")[1].strip()
            elif "Year" in line and "=>" in line:
                metadata["year"] = line.split("=>")[1].strip()
            elif "IMDbID" in line and "=>" in line:
                metadata["imdb"] = line.split("=>")[1].strip()
            elif "TheTVDB" in line and "=>" in line:
                metadata["thetvdb"] = line.split("=>")[1].strip()
            elif "Encoding Tool" in line and "=>" in line:
                metadata["encodingTool"] = line.split("=>")[1].strip()
    
    return metadata

def build_command(cmd: str, file: str, args: argparse.Namespace, mode: str) -> List[str]:
    """Build the AtomicParsley command based on the provided arguments.

    Args:
        cmd: Base command (AtomicParsley)
        file: Target file to process
        args: Parsed command line arguments
        mode: Operating mode (View/Modify)

    Returns:
        List[str]: Command arguments list
    """
    command = []
    if args.wipe:
        command = [cmd, file, "--metaEnema", "--overWrite"]
    elif mode == "View":
        command = [cmd, file, "-t"]
    elif mode == "Modify":
        command = [cmd, file]
        
        # If mirror option is used, get metadata from source file
        if args.mirror and is_valid_extension(args.mirror):
            source_metadata = get_metadata(cmd, args.mirror)
            
            # Check if migration is needed and apply it
            if needs_metadata_migration(source_metadata):
                print(f"Detected old metadata format in {args.mirror}, migrating...")
                migrated_metadata = migrate_metadata(source_metadata)
            else:
                migrated_metadata = source_metadata
            
            if migrated_metadata.get("episode"):
                command.extend(["--TVEpisodeNum", migrated_metadata["episode"]])
            if migrated_metadata.get("season"):
                command.extend(["--TVSeasonNum", migrated_metadata["season"]])
            if migrated_metadata.get("show"):
                command.extend(["--TVShowName", migrated_metadata["show"]])
            if migrated_metadata.get("genre"):
                command.extend(["--genre", migrated_metadata["genre"]])
            if migrated_metadata.get("desc"):
                command.extend(["--longdesc", migrated_metadata["desc"]])
            if migrated_metadata.get("url"):
                command.extend(["--description", migrated_metadata["url"]])
            if migrated_metadata.get("advisory"):
                command.extend(["--advisory", migrated_metadata["advisory"]])
            if migrated_metadata.get("title"):
                command.extend(["--title", migrated_metadata["title"]])
            if migrated_metadata.get("year"):
                command.extend(["--year", migrated_metadata["year"]])
            if migrated_metadata.get("imdb"):
                command.extend(["--xID", f"IMDbID={migrated_metadata['imdb']}"])
            if migrated_metadata.get("thetvdb"):
                command.extend(["--xID", f"TheTVDB={migrated_metadata['thetvdb']}"])
            
            # Always set encoding tool when mirroring, either to source value,
            # empty string if notools is set, or empty string if no encoding tool exists
            if args.notools:
                command.extend(["--encodingTool", ""])
            elif migrated_metadata.get("encodingTool"):
                command.extend(["--encodingTool", migrated_metadata["encodingTool"]])
            else:
                command.extend(["--encodingTool", ""])
                
        else:
            # Handle regular metadata arguments
            if args.episode:
                command.extend(["--TVEpisodeNum", args.episode])
            if args.season:
                command.extend(["--TVSeasonNum", args.season])
            if args.show:
                command.extend(["--TVShowName", args.show])
            if args.genre:
                command.extend(["--genre", args.genre])
            if args.desc:
                command.extend(["--longdesc", args.desc])
            if args.longdesc:
                command.extend(["--longdesc", args.longdesc])
            if args.url:
                command.extend(["--description", args.url])
            if args.advisory:
                command.extend(["--advisory", args.advisory])
            if args.title:
                command.extend(["--title", args.title])
            if args.year:
                command.extend(["--year", args.year])
            if args.imdb:
                command.extend(["--xID", f"IMDbID={args.imdb}"])
            if args.thetvdb:
                command.extend(["--xID", f"TheTVDB={args.thetvdb}"])
            
            # Only add encoding tool if notools flag is set
            if args.notools:
                command.extend(["--encodingTool", ""])
        
        command.append("--overWrite")
        if args.DeepScan:
            command.append("--DeepScan")
    return command

def main() -> None:
    """Main entry point for the AtomicParsley wrapper."""
    # Define default values
    default_cmd = "AtomicParsley"
    mode = "View"

    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="AtomicParsley Wrapper - A user-friendly interface for manipulating media file metadata",
        epilog="Examples:\n"
               "  ap video.mp4                     View metadata in user-friendly format\n"
               "  ap -t video.mp4                  View metadata in raw format\n"
               "  ap -m source.mp4 target.mp4      Copy all metadata from source to target\n"
               "  ap --title 'My Video' video.mp4  Set title for video\n"
               "  ap --notools video.mp4           Remove encoding tool metadata\n"
               "  ap --meta                        Tag all .mp4/.m4v in cwd from filenames\n"
               "  ap --meta ep.mp4                 Tag episode file from its filename",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-t", action="store_true", default=False, help="View metadata in raw AtomicParsley format")
    parser.add_argument("-m", "--mirror", type=str, help="Mirror all metadata from specified file")
    parser.add_argument("--notools", action="store_true", default=False, help="Remove encoding tool metadata")
    parser.add_argument(
        "--meta",
        action="store_true",
        default=False,
        help="Derive title/show/season/episode from filename (meta_update.pl behavior) and clear encoding tool",
    )
    parser.add_argument("--title", type=str, help="Set the title metadata")
    parser.add_argument("--episode", type=str, help="Set the TV episode number metadata")
    parser.add_argument("--season", type=str, help="Set the TV season number metadata")
    parser.add_argument("--show", type=str, help="Set the TV show name metadata")
    parser.add_argument("--genre", type=str, help="Set the genre metadata (comma separated values)")
    parser.add_argument("--desc", type=str, help="Set the description metadata")
    parser.add_argument("--longdesc", type=str, help="Set the long description metadata")
    parser.add_argument("--url", type=str, help="Set the URL metadata")
    parser.add_argument("--advisory", type=str, help="Set the advisory metadata to 'clean' or 'explicit'")
    parser.add_argument("--year", type=str, help="Set the year metadata")
    parser.add_argument("--imdb", type=str, help="Set the IMDb ID (e.g., tt11548850)")
    parser.add_argument("--thetvdb", type=str, help="Set the TheTVDB ID")
    parser.add_argument("--DeepScan", action="store_true", default=False, help="Perform a deep scan of metadata")
    parser.add_argument("--wipe", action="store_true", default=False, help="Wipe all metadata (ignores other metadata switches)")
    parser.add_argument("files", nargs="*", help="Media files to process (.mp4, .m4v)")

    args = parser.parse_args()

    # Check if AtomicParsley is available
    try:
        subprocess.run([default_cmd, "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: AtomicParsley is not installed or not in PATH")
        sys.exit(1)

    # --meta with no files: process all .mp4/.m4v in CWD (meta_update.pl parity)
    input_files = list(args.files)
    if args.meta and not input_files:
        input_files = sorted(
            f for f in os.listdir(".")
            if is_valid_extension(f) and os.path.isfile(f)
        )

    # Separate valid and invalid files
    valid_files = [f for f in input_files if is_valid_extension(f)]
    invalid_files = [f for f in input_files if not is_valid_extension(f)]

    # Notify about invalid files
    for f in invalid_files:
        print(f"Note: {f} is of an invalid type and will be ignored.")

    # Check if there are no valid files
    if not valid_files:
        if len(sys.argv) == 1:
            parser.print_help()
        else:
            print("Nothing to process.")
        sys.exit(1)

    # Determine mode
    if not args.t and not args.title and not args.year and not args.DeepScan and \
       not args.season and not args.episode and not args.show and not args.genre and \
       not args.desc and not args.longdesc and not args.url and not args.advisory and not args.imdb and \
       not args.thetvdb and not args.mirror and not args.notools and not args.meta:
        mode = "View"
    elif args.meta or args.notools or args.title or args.year or args.season or args.episode or \
         args.show or args.genre or args.desc or args.longdesc or args.url or args.advisory or \
         args.imdb or args.thetvdb or args.mirror:
        mode = "Modify"

    # Process each file
    total = len(valid_files)
    for index, file in enumerate(valid_files, start=1):
        print("File:", file)
        print("----------------------------------------------------------------")

        if args.meta:
            print(f"Processing {file}: {index} / {total}")
            parsed = parse_meta_filename(file)
            if not parsed:
                print(f"Skipping {file}: could not parse sNNeNN from filename")
            else:
                show, season, episode, title = parsed
                command = build_meta_command(
                    default_cmd, file, show, season, episode, title
                )
                print(" ".join(shlex.quote(part) for part in command))
                subprocess.run(command)
        elif mode == "View":
            # Get metadata and display it in a consistent format
            metadata = get_metadata(default_cmd, file)
            
            if metadata:
                if not any(metadata.values()):
                    print("No metadata found.")
                else:
                    if metadata.get("title"):
                        print(f"Title: {metadata['title']}")
                    if metadata.get("show"):
                        print(f"TV Show: {metadata['show']}")
                    if metadata.get("season"):
                        print(f"Season: {metadata['season']}")
                    if metadata.get("episode"):
                        print(f"Episode: {metadata['episode']}")
                    if metadata.get("genre"):
                        print(f"Genre: {metadata['genre']}")
                    if metadata.get("desc"):
                        print(f"Description: {metadata['desc']}")
                    if metadata.get("url"):
                        print(f"URL: {metadata['url']}")
                    if metadata.get("year"):
                        print(f"Year: {metadata['year']}")
                    if metadata.get("advisory"):
                        print(f"Advisory: {metadata['advisory']}")
                    if metadata.get("imdb"):
                        print(f"IMDb ID: {metadata['imdb']}")
                    if metadata.get("thetvdb"):
                        print(f"TheTVDB ID: {metadata['thetvdb']}")
                    if metadata.get("encodingTool"):
                        print(f"Encoding Tool: {metadata['encodingTool']}")
            else:
                # Fallback to direct command if parsing fails
                command = build_command(default_cmd, file, args, mode)
                subprocess.run(command)
        else:
            command = build_command(default_cmd, file, args, mode)
            if command:
                subprocess.run(command)
            else:
                print("No valid command to execute.")
                
        if len(valid_files) > 1:
            print()

if __name__ == "__main__":
    main() 
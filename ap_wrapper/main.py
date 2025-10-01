#!/usr/bin/env python3

import os
import argparse
import subprocess
import shlex
import sys
from typing import List, Optional

def is_valid_extension(file_name: str) -> bool:
    """Check if the file has a valid extension for AtomicParsley processing.

    Args:
        file_name: Name of the file to check

    Returns:
        bool: True if the file has a valid extension, False otherwise
    """
    extension = file_name.split('.')[-1] if '.' in file_name else ''
    return extension.lower() in ['mp4', 'm4v']

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
                metadata["url"] = line.split("contains:")[1].strip()
            elif '"ldes"' in line and "contains:" in line:
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
            if source_metadata.get("episode"):
                command.extend(["--TVEpisodeNum", source_metadata["episode"]])
            if source_metadata.get("season"):
                command.extend(["--TVSeasonNum", source_metadata["season"]])
            if source_metadata.get("show"):
                command.extend(["--TVShowName", source_metadata["show"]])
            if source_metadata.get("genre"):
                command.extend(["--genre", source_metadata["genre"]])
            if source_metadata.get("desc"):
                command.extend(["--description", source_metadata["desc"]])
            if source_metadata.get("url"):
                command.extend(["--desc", source_metadata["url"]])
            if source_metadata.get("advisory"):
                command.extend(["--advisory", source_metadata["advisory"]])
            if source_metadata.get("title"):
                command.extend(["--title", source_metadata["title"]])
            if source_metadata.get("year"):
                command.extend(["--year", source_metadata["year"]])
            if source_metadata.get("imdb"):
                command.extend(["--xID", f"IMDbID={source_metadata['imdb']}"])
            if source_metadata.get("thetvdb"):
                command.extend(["--xID", f"TheTVDB={source_metadata['thetvdb']}"])
            
            # Always set encoding tool when mirroring, either to source value,
            # empty string if notools is set, or empty string if no encoding tool exists
            if args.notools:
                command.extend(["--encodingTool", ""])
            elif source_metadata.get("encodingTool"):
                command.extend(["--encodingTool", source_metadata["encodingTool"]])
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
                command.extend(["--long", args.desc])
            if args.url:
                command.extend(["--desc", args.url])
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
               "  ap --notools video.mp4           Remove encoding tool metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-t", action="store_true", default=False, help="View metadata in raw AtomicParsley format")
    parser.add_argument("-m", "--mirror", type=str, help="Mirror all metadata from specified file")
    parser.add_argument("--notools", action="store_true", default=False, help="Remove encoding tool metadata")
    parser.add_argument("--title", type=str, help="Set the title metadata")
    parser.add_argument("--episode", type=str, help="Set the TV episode number metadata")
    parser.add_argument("--season", type=str, help="Set the TV season number metadata")
    parser.add_argument("--show", type=str, help="Set the TV show name metadata")
    parser.add_argument("--genre", type=str, help="Set the genre metadata (comma separated values)")
    parser.add_argument("--desc", type=str, help="Set the description metadata")
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

    # Separate valid and invalid files
    valid_files = [f for f in args.files if is_valid_extension(f)]
    invalid_files = [f for f in args.files if not is_valid_extension(f)]

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
       not args.desc and not args.url and not args.advisory and not args.imdb and \
       not args.thetvdb and not args.mirror and not args.notools:
        mode = "View"
    elif args.notools or args.title or args.year or args.season or args.episode or \
         args.show or args.genre or args.desc or args.url or args.advisory or \
         args.imdb or args.thetvdb or args.mirror:
        mode = "Modify"

    # Process each file
    for file in valid_files:
        print("File:", file)
        print("----------------------------------------------------------------")
        
        if mode == "View":
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
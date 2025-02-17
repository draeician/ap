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
        if args.episode:
            command.extend(["--TVEpisodeNum", args.episode])
        if args.season:
            command.extend(["--TVSeasonNum", args.season])
        if args.show:
            command.extend(["--TVShowName", args.show])
        if args.genre:
            command.extend(["--genre", args.genre])
        if args.desc:
            command.extend(["--description", args.desc])
        if args.longdesc:
            command.extend(["--long", args.longdesc])
        if args.advisory:
            command.extend(["--advisory", args.advisory])
        if args.title:
            command.extend(["--title", args.title])
        if args.year:
            command.extend(["--year", args.year])
        if args.notools:
            command.extend(["--encodingTool", ""])
        else:
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
    parser = argparse.ArgumentParser(description="AtomicParsley Wrapper")
    parser.add_argument("-t", action="store_true", default=False, help="View Existing Metadata")
    parser.add_argument("--notools", action="store_true", default=False, help="Remove Encoding Tools Metadata")
    parser.add_argument("--title", type=str, help="Set the Title metadata")
    parser.add_argument("--episode", type=str, help="Set the TVEpisodeNum metadata")
    parser.add_argument("--season", type=str, help="Set the TVSeasonNum metadata")
    parser.add_argument("--show", type=str, help="Set the TVShowName metadata")
    parser.add_argument("--genre", type=str, help="Set the genre metadata")
    parser.add_argument("--desc", type=str, help="Set the description metadata")
    parser.add_argument("--longdesc", type=str, help="Set the long description metadata")
    parser.add_argument("--advisory", type=str, help="Set the advisory metadata to 'clean' or 'explicit'")
    parser.add_argument("--year", type=str, help="Set the Year metadata")
    parser.add_argument("--DeepScan", action="store_true", default=False, help="Perform a deep scan")
    parser.add_argument("--wipe", action="store_true", default=False, help="Wipe all metadata (ignores other metadata switches)")
    parser.add_argument("files", nargs="*", help="Media files to process")

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
       not args.desc and not args.longdesc and not args.advisory:
        mode = "View"
    elif args.notools or args.title or args.year or args.season or args.episode or \
         args.show or args.genre or args.desc or args.longdesc or args.advisory:
        mode = "Modify"

    # Process each file
    for file in valid_files:
        command = build_command(default_cmd, file, args, mode)
        if command:
            print("File:", file)
            print("----------------------------------------------------------------")
            subprocess.run(command)
            if len(valid_files) > 1:
                print()
        else:
            print("No valid command to execute.")

if __name__ == "__main__":
    main() 
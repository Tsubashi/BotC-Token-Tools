"""Trim Icons."""
# Standard Library
import argparse
from pathlib import Path
import sys

# Third Party
from rich import print
from rich.live import Live
from wand.color import Color
from wand.image import Image

# Application Specific
from ..helpers.progress_group import setup_progress_group


def _parse_args():
    parser = argparse.ArgumentParser(
        prog="botc_tokens trim-icons",
        description='Find all icons in a folder and trim away extra space.'
    )
    parser.add_argument('target_directory', type=str,
                        help='The directory containing the icons.')
    parser.add_argument("-i", "--in-place", action="store_true", default=False,
                        help="Overwrite the original files.")

    args = parser.parse_args(sys.argv[2:])
    return args


def run():
    """Find all icons in a folder and trim away extra space."""
    args = _parse_args()
    # Ensure the target directory exists
    if not Path(args.target_directory).is_dir():
        print(f"[red]Error:[/] {args.target_directory} is not a directory.")
        return 1

    # Find all the icon images
    progress_group, overall_progress, step_progress = setup_progress_group()
    with Live(progress_group):
        icon_files = list(Path(args.target_directory).rglob("*.png"))

        if not icon_files:
            print("[red]Error:[/] No icons found.")
            return 1

        # Trim the icons
        task = overall_progress.add_task("Trimming Icons", total=len(icon_files))

        for icon_file in icon_files:
            with Image(filename=icon_file) as img:
                # Save the original size so we can check if anything changed
                original_size = img.size

                # Remove the extra space around the icon
                img.trim(color=Color('rgba(0,0,0,0)'), fuzz=0)

                # Check to see if anything changed, no need to save if nothing changed
                if img.size == original_size:
                    overall_progress.update(task, increment=1)
                    continue

                if args.in_place:
                    img.save(filename=str(icon_file))
                else:
                    img.save(filename=str(icon_file.with_name(f"{icon_file.stem}_trimmed{icon_file.suffix}")))
            overall_progress.update(task, increment=1)

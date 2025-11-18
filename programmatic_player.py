#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Programmatic Display Player

Runs mathematical/procedural programs on the FlaschPlayer LED display.
Programs are Python modules that implement a render() function.

Usage:
    python3 programmatic_player.py programs.plasma
    python3 programmatic_player.py programs.mandelbrot -x 5 -y 3
    python3 programmatic_player.py programs.plasma --rotate
"""

import argparse
import importlib
import logging
import sys
import time
from signal import signal, SIGINT
from pathlib import Path

import display as d
from config import settings

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger("programmatic_player")


def discover_programs():
    """
    Discover all available program modules in the programs directory.

    Returns:
        List of program module names (e.g., ['programs.plasma', 'programs.mandelbrot'])
    """
    programs_dir = Path(__file__).parent / 'programs'
    program_files = sorted(programs_dir.glob('*.py'))

    programs = []
    for program_file in program_files:
        # Skip __init__.py and any private modules
        if program_file.stem.startswith('_'):
            continue

        module_name = f'programs.{program_file.stem}'

        # Try to import to verify it has a render function
        try:
            module = importlib.import_module(module_name)
            if hasattr(module, 'render'):
                programs.append(module_name)
        except Exception as e:
            logger.warning(f"Skipping {module_name}: {e}")

    return programs


def init_display(x_boxes, y_boxes, rotate_90):
    """
    Initialize the display (NeoPixel or PyGame).

    Args:
        x_boxes: Number of boxes horizontally
        y_boxes: Number of boxes vertically
        rotate_90: Whether to rotate display 90 degrees

    Returns:
        Display object (NeoPixelDisplay or PyGameDisplay)
    """
    led_count = x_boxes * y_boxes * 20

    if rotate_90:
        x_res = x_boxes * 4
        y_res = y_boxes * 5
    else:
        x_res = x_boxes * 5
        y_res = y_boxes * 4

    settings.display_resolution = (x_res, y_res)
    logger.info(f"Display resolution: {x_res}x{y_res}")

    if settings.use_neopixel:
        logger.info("Initializing NeoPixel display")
        from layout import full_layout
        layout_matrix = full_layout(x_boxes, y_boxes, False, False, rotate_90)
        display = d.NeoPixelDisplay(
            led_count,
            x_boxes,
            y_boxes,
            layout=layout_matrix,
            rotate_90=rotate_90
        )
    else:
        logger.info("Initializing PyGame display (dev mode)")
        display = d.PyGameDisplay(x_res, y_res, 50)

    return display


def run_programs(display, program_names, start_index=0):
    """
    Run programmatic renderers with ability to cycle between them.

    The program modules must implement:
        render(display, width, height, frame) - Called every frame
        get_fps() - Optional, returns desired FPS (default 30)

    Args:
        display: Display object
        program_names: List of program module names
        start_index: Index of program to start with
    """
    width, height = settings.display_resolution

    current_index = start_index
    frame_num = 0
    switch_program = True  # Flag to reload program

    logger.info(f"Available programs: {', '.join([p.split('.')[-1] for p in program_names])}")
    logger.info("Use LEFT/RIGHT or UP/DOWN arrow keys to switch programs")
    logger.info("Press Ctrl+C or close window to exit")

    try:
        while display.is_running():
            # Load/reload program if needed
            if switch_program:
                program_name = program_names[current_index]
                logger.info(f"Loading program [{current_index + 1}/{len(program_names)}]: {program_name}")

                # Reload the module to reset any state
                if program_name in sys.modules:
                    importlib.reload(sys.modules[program_name])
                program_module = importlib.import_module(program_name)

                # Get FPS from program or use default
                fps = getattr(program_module, 'get_fps', lambda: 30)()
                frame_delay = 1.0 / fps
                logger.info(f"Running at {fps} FPS")

                frame_num = 0
                switch_program = False

            # Update brightness from settings
            display.set_brightness()

            # Call the program's render function
            program_module.render(display, width, height, frame_num)

            # Show the frame and get any commands
            command = display.show()

            # Handle program switching
            if command == 'next_program':
                current_index = (current_index + 1) % len(program_names)
                switch_program = True
                logger.info("Switching to next program...")
            elif command == 'prev_program':
                current_index = (current_index - 1) % len(program_names)
                switch_program = True
                logger.info("Switching to previous program...")

            # Sleep to maintain FPS
            if not switch_program:  # Don't sleep if we're switching
                time.sleep(frame_delay)
                frame_num += 1

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.exception(f"Error running program: {e}")
        raise


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run programmatic displays on FlaschPlayer'
    )
    parser.add_argument(
        'program',
        nargs='?',  # Make program optional
        help='Python module path (e.g., programs.plasma). If not specified, starts with first available program.'
    )
    parser.add_argument(
        '-x', '--x-boxes',
        type=int,
        default=5,
        help='Number of boxes horizontally (default: 5)'
    )
    parser.add_argument(
        '-y', '--y-boxes',
        type=int,
        default=3,
        help='Number of boxes vertically (default: 3)'
    )
    parser.add_argument(
        '-r', '--rotate',
        action='store_true',
        help='Rotate display 90 degrees'
    )

    args = parser.parse_args()

    # Discover all available programs
    available_programs = discover_programs()

    if not available_programs:
        logger.error("No programs found in programs/ directory")
        sys.exit(1)

    # Determine starting program
    start_index = 0
    if args.program:
        # User specified a program
        if args.program in available_programs:
            start_index = available_programs.index(args.program)
        else:
            logger.error(f"Program '{args.program}' not found")
            logger.error(f"Available programs: {', '.join(available_programs)}")
            sys.exit(1)

    # Initialize display
    display = init_display(args.x_boxes, args.y_boxes, args.rotate)

    # Set up signal handler for graceful exit
    def handler(signal_received, frame):
        logger.info('SIGINT or CTRL-C detected. Exiting gracefully')
        sys.exit(0)

    signal(SIGINT, handler)

    # Run the programs with cycling support
    run_programs(display, available_programs, start_index)


if __name__ == '__main__':
    main()

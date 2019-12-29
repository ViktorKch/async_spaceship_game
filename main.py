import time
import curses
import asyncio
import random
import os
from fire_animation import fire
from curses_tools import draw_frame, read_controls, get_frame_size
from itertools import cycle

TIC_TIMEOUT = 0.1
SYMBOLS = ['+', '*', '.', ':']

def get_frames_from_dir(directory_with_frames):
    frames = []
    for frame_file in os.listdir(f"{directory_with_frames}"):
        with open(f"{directory_with_frames}/{frame_file}") as _file:
            frames.append(_file.read())
    return frames

async def blink(canvas, row, column, symbol='*'):

    state = random.randint(0,3)
    while True:
        if state == 0:
            canvas.addstr(row, column, symbol, curses.A_DIM)
            for tic in range(20):
                await asyncio.sleep(0)
            state += 1

        if state == 1:
            canvas.addstr(row, column, symbol)
            for tic in range(3):
                await asyncio.sleep(0)
            state += 1

        if state == 2:
            canvas.addstr(row, column, symbol, curses.A_BOLD)
            for tic in range(5):
                await asyncio.sleep(0)
            state += 1

        if state == 3:
            canvas.addstr(row, column, symbol)
            for tic in range(3):
                await asyncio.sleep(0)
            state = 0

async def animate_spaceship(canvas, row, column, *frames):
    last_frame = None
    prev_row, prev_column = row, column
    min_x, min_y = 1, 1
    max_x, max_y = canvas.getmaxyx()

    while True:
        for frame in cycle(frames):
            delta_row, delta_column, space = read_controls(canvas)
            frame_rows, frame_columns = get_frame_size(frame)

            if prev_column + delta_column + frame_columns > max_y - 1 or prev_column + delta_column + 1 < min_y + 1:
                delta_column = 0
            if prev_row + delta_row + frame_rows > max_x - 1 or prev_row + delta_row + 1 < min_x + 1:
                delta_row = 0

            if last_frame:
                draw_frame(canvas, prev_row, prev_column, last_frame, negative=True)

            prev_row = new_row = prev_row + delta_row
            prev_column = new_column = prev_column + delta_column
            draw_frame(canvas, new_row, new_column, frame)

            last_frame = frame

            for _ in range(2):
                await asyncio.sleep(0)

def star_generator(height, width, number=300):

    for star in range(number):
        y_pos = random.randint(1, height - 2)
        x_pos = random.randint(1, width - 2)
        symbol = random.choice(SYMBOLS)

        yield y_pos, x_pos, symbol

def main(canvas):
    canvas.border()
    curses.curs_set(False)
    canvas.nodelay(True)

    rocket_frames = get_frames_from_dir('animation_frames')

    height, width = canvas.getmaxyx()

    x_start = width / 2
    y_start = height / 2

    coroutines = [blink(canvas, row, column, symbol) for row, column, symbol in star_generator(height, width)]

    coroutines.append(animate_spaceship(canvas, y_start, x_start, *rocket_frames))

    while True:
        
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        if len(coroutines) == 0:
            break

        canvas.refresh()
        time.sleep(TIC_TIMEOUT)

if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
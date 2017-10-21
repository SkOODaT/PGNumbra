# Helper function to calculate start and end line for paginated output
import logging
import math
import os
import platform
import shlex
import struct
import subprocess
import time
from datetime import datetime
from threading import Thread

from pgnumbra.utils import get_pokemon_name


def input_processor(state):
    while True:
        # Wait for the user to press a key.
        command = raw_input()

        if command.isdigit():
            state['page'] = int(command)
        elif command == 'q':
            os._exit(0)


def print_status(scanners):
    state = {
        'page': 1
    }
    # Start another thread to get user input.
    t = Thread(target=input_processor,
               name='input_processor',
               args=(state,))
    t.daemon = True
    t.start()

    while True:
        time.sleep(1)

        lines = []

        total_pages = print_scanners(lines, state, scanners)

        # Footer
        lines.append('Page {}/{}. Page number to switch pages.'.format(
            state['page'], total_pages))

        # Print lines
        os.system('cls' if os.name == 'nt' else 'clear')
        print ('\n'.join(lines)).encode('utf-8')


def determine_seen_pokemon(scanners):
    seen = {}
    for t in scanners:
        for pid in t.seen_pokemon:
            seen[pid] = get_pokemon_name(pid)
    return seen


def print_scanners(lines, state, scanners):
    def scanner_line(current_line, scanner, seen_pokemon):
        km_walked_f = scanner.get_stats('km_walked', None)
        if km_walked_f is not None:
            km_walked_str = '{:.0f}'.format(km_walked_f)
        else:
            km_walked_str = ""
        warn = scanner.get_state('warn')
        warned = '' if warn is None else ('Yes' if warn else 'No')
        ban = scanner.get_state('banned')
        banned = '' if ban is None else ('Yes' if ban else 'No')
        cols = [
            current_line,
            scanner.username,
            scanner.get_stats('level', ''),
            km_walked_str,
            warned,
            banned
        ]
        if ban == True:
            cols.append('Account banned!')
            return msg_tmpl.format(*cols)
        elif not scanner.seen_pokemon:
            cols.append(scanner.last_msg or '')
            return msg_tmpl.format(*cols)
        else:
            for pid in sorted(seen_pokemon):
                cols.append(scanner.seen_pokemon.get(pid, ''))
            return line_tmpl.format(*cols)

    len_num = str(len(str(len(scanners))))
    len_username = str(reduce(lambda l1, l2: max(l1, l2),
                              map(lambda s: len(s.username), scanners)))
    line_tmpl = u'{:' + len_num + '} | {:' + len_username + '} | {:3} | {:4} | {:3} | {:3}'
    msg_tmpl = line_tmpl + u' | {}'

    # Top line
    lines.append(msg_tmpl.format('', '', '', '', '', '', 'Pokemon'))

    cols = ['#', 'Account', 'Lvl', 'km', 'Wrn', 'Ban']
    seen_pokemon = determine_seen_pokemon(scanners)
    for pid in sorted(seen_pokemon):
        pname = seen_pokemon[pid]
        len_name = str(len(pname))
        line_tmpl += u' | {:' + len_name + u'}'
        cols.append(pname)

    lines.append(line_tmpl.format(*cols))
    return print_lines(lines, scanner_line, scanners, 4, state, seen_pokemon)


def print_lines(lines, print_entity, entities, addl_lines, state, seen_pokemon):
    # Pagination.
    start_line, end_line, total_pages = calc_pagination(len(entities), addl_lines,
                                                        state)

    current_line = 0
    for e in entities:
        # Skip over items that don't belong on this page.
        current_line += 1
        if current_line < start_line:
            continue
        if current_line > end_line:
            break

        lines.append(print_entity(current_line, e, seen_pokemon))

    return total_pages


def calc_pagination(total_rows, non_data_rows, state):
    width, height = get_terminal_size()
    # Title and table header is not usable space
    usable_height = height - non_data_rows
    # Prevent people running terminals only 6 lines high from getting a
    # divide by zero.
    if usable_height < 1:
        usable_height = 1

    total_pages = int(math.ceil(total_rows / float(usable_height)))

    # Prevent moving outside the valid range of pages.
    if state['page'] > total_pages:
        state['page'] = total_pages
    if state['page'] < 1:
        state['page'] = 1

    # Calculate which lines to print (1-based).
    start_line = usable_height * (state['page'] - 1) + 1
    end_line = start_line + usable_height - 1

    return start_line, end_line, total_pages


def hr_tstamp(tstamp):
    if isinstance(tstamp, float):
        return datetime.fromtimestamp(tstamp).strftime("%H:%M:%S")
    else:
        return tstamp


def get_terminal_size():
    """ getTerminalSize()
     - get width and height of console
     - works on linux,os x,windows,cygwin(windows)
     originally retrieved from:
     http://stackoverflow.com/questions/566746/how-to-get-console-window-width-in-python
    """
    current_os = platform.system()
    tuple_xy = None
    if current_os == 'Windows':
        tuple_xy = _get_terminal_size_windows()
        if tuple_xy is None:
            tuple_xy = _get_terminal_size_tput()
            # Needed for window's python in cygwin's xterm!
    if current_os in ['Linux', 'Darwin'] or current_os.startswith('CYGWIN'):
        tuple_xy = _get_terminal_size_linux()
    if tuple_xy is None:
        tuple_xy = (80, 25)      # Default value.
    return tuple_xy


def _get_terminal_size_windows():
    try:
        from ctypes import windll, create_string_buffer
        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (bufx, bufy, curx, cury, wattr,
             left, top, right, bottom,
             maxx, maxy) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except:
        pass


def _get_terminal_size_tput():
    # Get terminal width.
    # src: How do I find the width & height of a terminal window?
    # url: http://stackoverflow.com/q/263890/1706351
    try:
        cols = int(subprocess.check_call(shlex.split('tput cols')))
        rows = int(subprocess.check_call(shlex.split('tput lines')))
        return (cols, rows)
    except:
        pass


def _get_terminal_size_linux():
    def ioctl_GWINSZ(fd):
        try:
            import fcntl
            import termios
            cr = struct.unpack('hh',
                               fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))
            return cr
        except:
            pass
    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        try:
            cr = (os.environ['LINES'], os.environ['COLUMNS'])
        except:
            return None
    return int(cr[1]), int(cr[0])

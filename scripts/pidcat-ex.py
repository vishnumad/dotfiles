#!/usr/bin/python -u

# Copyright 2009, The Android Open Source Project
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Script to highlight adb logcat output for console
# Originally written by Jeff Sharkey, http://jsharkey.org/
# Piping detection and popen() added by other Android team members
# Package filtering and output improvements by Jake Wharton, http://jakewharton.com

import argparse
import sys
import re
import time
import subprocess
from subprocess import PIPE

__version__ = '2.2.0'

LOG_LEVELS = 'VDIWEF'
LOG_LEVELS_MAP = dict([(LOG_LEVELS[i], i) for i in range(len(LOG_LEVELS))])
parser = argparse.ArgumentParser(description='Filter logcat by package name')
parser.add_argument('package', nargs='*', help='Application package name(s)')
parser.add_argument('-w', '--tag-width', metavar='N', dest='tag_width', type=int, default=23, help='Width of log tag')
parser.add_argument('-l', '--min-level', dest='min_level', type=str,
                    choices=LOG_LEVELS+LOG_LEVELS.lower(), default='V',
                    help='Minimum level to be displayed')
parser.add_argument('--color-gc', dest='color_gc', action='store_true',
                    help='Color garbage collection')
parser.add_argument('--always-display-tags', dest='always_tags', action='store_true',
                    help='Always display the tag name')
parser.add_argument('--current', dest='current_app', action='store_true',
                    help='Filter logcat by current running app')
parser.add_argument('-s', '--serial', dest='device_serial', help='Device serial number (adb -s option)')
parser.add_argument('-d', '--device', dest='use_device', action='store_true',
                    help='Use first device for log input (adb -d option)')
parser.add_argument('-e', '--emulator', dest='use_emulator', action='store_true',
                    help='Use first emulator for log input (adb -e option)')
parser.add_argument('-c', '--clear', dest='clear_logcat', action='store_true',
                    help='Clear the entire log before running')
parser.add_argument('-t', '--tag', dest='tag', action='append', help='Filter output by specified tag(s)')
parser.add_argument('-i', '--ignore-tag', dest='ignored_tag', action='append',
                    help='Filter output by ignoring specified tag(s)')
parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__,
                    help='Print the version number and exit')
parser.add_argument('-a', '--all', dest='all', action='store_true', default=False, help='Print all log messages')
parser.add_argument('--timestamp', dest='add_timestamp', action='store_true', default=True,
                    help='Prepend each line of output with the current time.')
parser.add_argument('--extra-header-width', metavar='N', dest='extra_header_width', type=int, default=0,
                    help='Width of customized log header. If you have your own header besides Android log header, '
                         'this option will further indent your wrapped lines with additional width')
parser.add_argument('--grep', dest='grep_words', metavar='WORD_LIST_TO_GREP', action='append',
                    help='Filter lines with words in log messages. The words are delimited with \'|\', '
                         'where each word can be tailed with a color initialed with \'\\\'. If no color '
                         'is specified, \'RED\' will be the default color. For example, option '
                         '--grep=\'word1|word2\\CYAN\' means to filter out all lines containing either '
                         '\'word1\' or \'word2\', and \'word1\' will appear in default color \'RED\', '
                         'while \'word2\' will be in the specified color \'CYAN\'. Supported colors '
                         '(case ignored): {BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE, BG_BLACK, '
                         'BG_RED, BG_GREEN, BG_YELLOW, BG_BLUE, BG_MAGENTA, BG_CYAN, BG_WHITE, NONE}. '
                         'The color with prefix \'BG_\' is background color. And color \'NONE\' '
                         'means NOT highlighting with color. You can have multiple \'--grep\' '
                         'options in the command line, and if so, the command will grep all of the key words '
                         'in all \'--grep\' options.  Escape \'|\' with \'\\|\', and \'\\\' with \'\\\\\'.')
parser.add_argument('--hl', dest='highlight_words', metavar='WORD_LIST_TO_HIGHLIGHT', action='append',
                    help='Words to highlight in log messages. Unlike \'--grep\' option, '
                         'this option will only highlight the specified words with specified '
                         'color but does not filter any lines. Except this, the format and supported '
                         'colors are the same as \'--grep\'. You can have multiple \'--hl\' options in '
                         'the command line, and if so, the command will highlight all of the key words '
                         'in all \'--hl\' options')
parser.add_argument('--grepv', dest='grepv_words', metavar='WORD_LIST_TO_EXCLUDE', action='append',
                    help='Exclude lines with words from log messages. The format and supported colors are '
                         'the same as \'--grep\'. Note that if both \'--grepv\' and \'--grep\' are provided '
                         'and they contain the same word, the line will always show, which means \'--grep\' '
                         'overwrites \'--grepv\' for the same word they both contain. You can have multiple '
                         '\'--grepv\' options in the command line, and if so, the command will exclude the '
                         'lines containing any keywords in all \'--grepv\' options')
parser.add_argument('--igrep', dest='igrep_words', metavar='WORD_LIST_TO_GREP', action='append',
                    help='The same as \'--grep\', just ignore case')
parser.add_argument('--ihl', dest='ihighlight_words', metavar='WORD_LIST_TO_HIGHLIGHT', action='append',
                    help='The same as \'--hl\', just ignore case')
parser.add_argument('--igrepv', dest='igrepv_words', metavar='WORD_LIST_TO_EXCLUDE', action='append',
                    help='The same as \'--grepv\', just ignore case')
parser.add_argument('--rgrep', dest='rgrep_words', metavar='REGEX_LIST_TO_GREP', action='append',
                    help='The same as \'--grep\', just using regular expressions in python style '
                         'as described in \'https://docs.python.org/2/library/re.html\'. '
                         'In the regular expression, make sure to '
                         'escape \'|\' with \'\\|\', and \'\\\' with \'\\\\\'')
parser.add_argument('--rhl', dest='rhighlight_words', metavar='REGEX_LIST_TO_HIGHLIGHT', action='append',
                    help='The same as \'--hl\', just using regular expressions in python style '
                         'as described in \'https://docs.python.org/2/library/re.html\'. '
                         'In the regular expression, make sure to '
                         'escape \'|\' with \'\\|\', and \'\\\' with \'\\\\\'')
parser.add_argument('--rgrepv', dest='rgrepv_words', metavar='REGEX_LIST_TO_EXCLUDE', action='append',
                    help='The same as \'--grepv\', just using regular expressions in python style '
                         'as described in \'https://docs.python.org/2/library/re.html\'. '
                         'In the regular expression, make sure to '
                         'escape \'|\' with \'\\|\', and \'\\\' with \'\\\\\'')
parser.add_argument('--keep-all-errors', dest='keep_errors', action='store_true',
                    help='Do not filter any error or fatal logs from \'pidcat-ex\' output. This is quite helpful to '
                         'avoid ignoring information about exceptions, crash stacks and assertion failures')
parser.add_argument('--keep-all-warnings', dest='keep_warnings', action='store_true',
                    help='Do not filter any warning, error or fatal logs from \'pidcat-ex\' output. '
                         'This is quite helpful to '
                         'avoid ignoring information about exceptions, crash stacks and assertion failures')
parser.add_argument('--tee', dest='file_name', type=str, default='',
                    help='Besides stdout output, also output the filtered result (after grep/grepv) to the file')
parser.add_argument('--tee-pidcat', dest='pidcat_file_name', type=str, default='',
                    help='Besides stdout output, also output the unfiltered original pidcat-ex result '
                         '(all pidcat-ex formatted lines) to the file')
parser.add_argument('--tee-adb', dest='adb_output_file_name', type=str, default='',
                    help='Output original adb result (raw adb output) to the file')
parser.add_argument('--pipe', dest='terminal_width_for_pipe_mode', type=int, default=-1,
                    help='Note: you need to give terminal width as the value, just put `tput cols` here. '
                         'When running in pipe mode, the script will take input from \'stdin\' rather '
                         'than launching adb itself. The usage becomes something like '
                         '\"adb -d logcat | pidcat-ex --pipe `tput cols` com.testapp\". This is very useful '
                         'when you want to apply any third-party scripts on the adb output before pidcat-ex '
                         'cutting each line, like using 3rd-party scripts to grep or hilight with colors '
                         '(such as using \'ack\' or \'h\' command) to keywords. For example, '
                         '\"adb -d logcat | h -i \'battery\' | pidcat-ex --pipe `tput cols` com.testapp\"')
parser.add_argument('--hide-header', dest='hide_header_regex', action='append',
                    help='Remove the header in each line that matches the regular expression. '
                         'Note that Android adb header is NOT considered here. '
                         'The parameter is regular expression. When this option provided, the script will match the '
                         'head of each log line (not including the Android adb header) '
                         'with the regular expression, and remove the matched header in the '
                         'output. This is useful when your own log has big long headers in each line which you don\'t '
                         'care and want to hide them from the output. The regular expression syntax is in python '
                         'style as described in \'https://docs.python.org/2/library/re.html\'. You can specify '
                         'multiple \'--hide-header\' options and if the header matches any of them, it will be '
                         'removed from output')
parser.add_argument('--addr2line-tool', type=str, dest='addr2line_tool',
                    metavar='ADDR2LINE_TOOL_PATH',
                    help='This option along with \'--addr2line-bin\' '
                         '(you have to give values to both these parameters) '
                         'will help you automatically '
                         'symbolicate the native crash addresses found in the log that match your '
                         'native code binary file with debug information, such as '
                         '\'.so\' lib file. \'ADDR2LINE_TOOL_PATH\' is the path to '
                         'the \'xxx-addr2line\', which should be found in your Android SDK directory. ')

parser.add_argument('--addr2line-bin', type=str, dest='addr2line_bin',
                    metavar='NATIVE_DEBUG_BIN_FILE_PATH', action='append',
                    help='This option along with `--addr2line-tool` (you have to give values to both these parameters) '
                         'will help you automatically '
                         'symbolicate the native crash addresses found in the log that match your '
                         'native code binary file with debug information, such as '
                         '\'.so\' lib file. \'NATIVE_DEBUG_SO_LIB_FILE_PATH\' is the file path to '
                         'your debug version native binary file with debug symbols in it. '
                         'You can provide multiple \'--addr2line-bin\' options to symbolicate '
                         'crashes of multiple native binary files. The script can automatically match the correct '
                         'binary file for each crash log line. '
                         'Note that your \'NATIVE_DEBUG_SO_LIB_FILE_PATH\' '
                         'version has to match the addresses in the crash log, otherwise, the symbolicated result '
                         'would not be correct')


PID_LINE = re.compile(r'^\w+\s+(\w+)\s+\w+\s+\w+\s+\w+\s+\w+\s+\w+\s+\w\s([\w|./]+)$')
PID_START = re.compile(r'^.*: Start proc ([a-zA-Z0-9._:]+) for ([a-z]+ [^:]+): pid=(\d+) uid=(\d+) gids=(.*)$')
PID_START_5_1 = re.compile(r'^.*: Start proc (\d+):([a-zA-Z0-9._:]+)/[a-z0-9]+ for (.*)$')
PID_START_DALVIK = re.compile(r'^E/dalvikvm\(\s*(\d+)\): >>>>> ([a-zA-Z0-9._:]+) \[ userId:0 \| appId:(\d+) \]$')
PID_KILL = re.compile(r'^Killing (\d+):([a-zA-Z0-9._:]+)/[^:]+: (.*)$')
PID_LEAVE = re.compile(r'^No longer want ([a-zA-Z0-9._:]+) \(pid (\d+)\): .*$')
PID_DEATH = re.compile(r'^Process ([a-zA-Z0-9._:]+) \(pid (\d+)\) has died.?$')
LOG_LINE = re.compile(r'^[0-9-]+ ([0-9:.]+) ([A-Z])/(.+?)\( *(\d+)\): (.*?)$')
LOG_LINE_NO_TIME = re.compile(r'([A-Z])/(.+?)\( *(\d+)\): (.*?)$')
LOG_LINE_DEFAULT_FMT = re.compile(r'^[0-9-]+ ([0-9:.]+)\s*([0-9]+)\s*[0-9]+ ([A-Z]) (.+?): (.*?)$')
BUG_LINE = re.compile(r'.*nativeGetEnabledTags.*')
BACKTRACE_LINE = re.compile(r'^#(.*?)pc\s(.*?)$')
NATIVE_CRASH_LINE = re.compile(r'#[0-9]{2}[\s]+pc[\s]+([0-9a-zA-Z]+)[\s]+(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))')
FILE_PATH = re.compile(r'^(.*/)?(?:$|(.+?)(?:(\.[^.]*$)|$))')

args = parser.parse_args()

min_level = LOG_LEVELS_MAP[args.min_level.upper()]

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

color_dict = {'BLACK': BLACK, 'RED': RED, 'GREEN': GREEN, 'YELLOW': YELLOW,
              'BLUE': BLUE, 'MAGENTA': MAGENTA, 'CYAN': CYAN, 'WHITE': WHITE,
              'NONE': None}
contrast_color_dict = {BLACK: WHITE, RED: BLACK, GREEN: BLACK, YELLOW: BLACK,
                       BLUE: BLACK, MAGENTA: BLACK, CYAN: BLACK, WHITE: BLACK}


def empty(vector):
    return vector is None or len(vector) <= 0


RESET = '\033[0m'
EOL = '\033[K'


def termcolor(fg=None, bg=None, bold=False, ul=False):
    codes = []
    if fg is not None:
        codes.append('3%d' % fg)
    if bg is not None:
        codes.append('10%d' % bg)
    res = '\033['
    if bold:
        res += '1;'
    if ul:
        res += '4;'
    if codes:
        res += ';'.join(codes)
    res += 'm'
    return res


def colorize(message, fg=None, bg=None, bold=False, ul=False):
    return termcolor(fg, bg, bold, ul) + message + RESET


def pause(tm):
    for i in range(0, tm - 1):
        sys.stdout.write("Continue anyway in %d seconds ...\r" % (tm - i))
        time.sleep(1)
    sys.stdout.write("\r\n")


def print_error(error_msg):
    print('\n' + colorize(error_msg, fg=RED, bold=True, ul=True) + '\n')
    pause(5)


def extract_color_from_word_and_convert_esc_chars(word):
    word = word.replace('\|', '|')
    w = word
    c = RED
    bg = False
    delimiter = '\\'
    index = word.rfind(delimiter)
    while index > 0 and word[index - 1] == '\\':
        index = word.rfind(delimiter, 0, index - 1)
    if index != -1:
        w = word[0:index]
        raw_color_word = word[index + len(delimiter):]
        try:
            color_word = raw_color_word.upper()
            if color_word[:3] == 'BG_':
                bg = True
                color_word = color_word[3:]
            c = color_dict[color_word]
        except KeyError:
            print_error('Wrong color name: \'' + raw_color_word + '\'')
            c = RED
            bg = False
    w = w.replace('\\\\', '\\')
    return w, c, bg


def parse_keywords(keyword_str_list):
    if empty(keyword_str_list):
        return []
    else:
        res = []
        for words in keyword_str_list:
            prev = 0
            idx = words.find('|')
            while idx != -1:
                if idx <= 0 or words[idx - 1] != '\\':
                    w, c, bg = extract_color_from_word_and_convert_esc_chars(words[prev:idx])
                    if not empty(w):
                        res.append([w, c, bg])
                    prev = idx + 1
                idx = words.find('|', idx + 1)
            w, c, bg = extract_color_from_word_and_convert_esc_chars(words[prev:])
            if not empty(w):
                res.append([w, c, bg])
        return res

grep_words_with_color = parse_keywords(args.grep_words)
highlight_words_with_color = parse_keywords(args.highlight_words)
excluded_words = parse_keywords(args.grepv_words)
igrep_words_with_color = parse_keywords(args.igrep_words)
ihighlight_words_with_color = parse_keywords(args.ihighlight_words)
iexcluded_words = parse_keywords(args.igrepv_words)
rgrep_words_with_color = parse_keywords(args.rgrep_words)
rhighlight_words_with_color = parse_keywords(args.rhighlight_words)
rexcluded_words = parse_keywords(args.rgrepv_words)

package = args.package

base_adb_command = ['adb']
if args.device_serial:
    base_adb_command.extend(['-s', args.device_serial])
if args.use_device:
    base_adb_command.append('-d')
if args.use_emulator:
    base_adb_command.append('-e')

if args.current_app:
    system_dump_command = base_adb_command + ["shell", "dumpsys", "activity", "activities"]
    system_dump = subprocess.Popen(system_dump_command, stdout=PIPE, stderr=PIPE).communicate()[0]
    running_package_name = re.search(".*TaskRecord.*A[= ]([^ ^}]*)", system_dump).group(1)
    package.append(running_package_name)

if len(package) == 0:
    args.all = True

# Store the names of packages for which to match all processes.
catchall_package = list(filter(lambda package: package.find(":") == -1, package))
# Store the name of processes to match exactly.
named_processes = list(filter(lambda package: package.find(":") != -1, package))
# Convert default process names from <package>: (cli notation) to <package>
# (android notation) in the exact names match group.
named_processes = map(lambda package:
                      package if package.find(":") != len(package) - 1 else package[:-1], named_processes)

header_size = args.tag_width + 1 + 3 + 1  # space, level, space

width = args.terminal_width_for_pipe_mode
if width == -1:
    try:
        # Get the current terminal width
        import fcntl
        import termios
        import struct
        h, width = struct.unpack('hh', fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack('hh', 0, 0)))
    except:
        width = 100
        print_error('PLEASE SPECIFY TERMINAL WIDTH !!! It looks the script is running in pipe mode. '
                    'Please just add \'--pipe=`tput cols`\' as a parameter of pidcat-ex')

tee_file = None
if not empty(args.file_name):
    tee_file = open(args.file_name, 'w')

tee_pidcat_file = None
if not empty(args.pidcat_file_name):
    tee_pidcat_file = open(args.pidcat_file_name, 'w')

tee_adb_file = None
if not empty(args.adb_output_file_name):
    tee_adb_file = open(args.adb_output_file_name, 'wb')


def hide_header(line, regex_list):
    for regex in regex_list:
        matches = re.match(regex, line)
        if matches:
            return line[matches.end():], matches.groups(), True
    return line, [], False


def output_line(line, keep_line_on_stdout = True):
    if tee_pidcat_file is not None:
        tee_pidcat_file.write(line)
        tee_pidcat_file.write('\n')
        tee_pidcat_file.flush()

    if keep_line_on_stdout:
        print(line)
        sys.stdout.flush()
        if tee_file is not None:
            tee_file.write(line)
            tee_file.write('\n')
            tee_file.flush()


def does_match_grep(message, grep_words_with_color, ignore_case):
    if not empty(grep_words_with_color):
        for word, c, bg in grep_words_with_color:
            if len(word) > 0 and ((not ignore_case and word in message) or
                                  (ignore_case and word.upper() in message.upper())):
                return True
    return False


def does_match_regex_grep(message, regex_grep_words_with_color):
    if not empty(regex_grep_words_with_color):
        for pattern, c, bg in regex_grep_words_with_color:
            if len(pattern) > 0 and re.search(pattern, message) is not None:
                return True
    return False


def does_match_grepv(message, grepv_words, ignore_case):
    if not empty(grepv_words):
        for word, c, bg in grepv_words:
            if len(word) > 0 and ((not ignore_case and word in message) or
                                  (ignore_case and word.upper() in message.upper())):
                return True
    return False


def does_match_regex_grepv(message, rgrepv_words):
    if not empty(rgrepv_words):
        for pattern, c, bg in rgrepv_words:
            if len(pattern) > 0 and re.search(pattern, message) is not None:
                return True
    return False


def colorize_substr(str, start_index, end_index, color, bg):
    fg_color = None
    bg_color = None
    ul = False
    if bg:
        bg_color = color
        try:
            fg_color = contrast_color_dict[color]
        except KeyError:
            pass
    else:
        fg_color = color
        ul = True
    colored_word = colorize(str[start_index:end_index], fg_color, bg_color, bold=True, ul=ul)
    return str[:start_index] + colored_word + str[end_index:], start_index + len(colored_word)


ANSI_ESC_PATTERN = r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})*(;[0-9]{3})?)?[m|K]'


def highlight(line, words_to_color, ignore_case=False, is_regex=False):
    for word, c, bg in words_to_color:
        if len(word) > 0:
            index = 0
            word_len = len(word)
            while index < len(line):
                try:
                    if is_regex:
                        re_res = re.search(word, line[index:])
                        if re_res:
                            index += re_res.start()
                            word_len = re_res.end() - re_res.start()
                        else:
                            break
                    elif ignore_case:
                        index = line.upper().index(word.upper(), index)
                    else:
                        index = line.index(word, index)
                except ValueError:
                    break
                line, index = colorize_substr(line, index, index + word_len, c, bg)

    return line


# All ANSI escape codes are not counted in this `substr` function but are kept in the substring
def substr(unstripped_str, start, end):
    res = ''
    unstripped_i = 0
    idx = 0
    cur_esc = ''
    while unstripped_i < len(unstripped_str):
        match_res = re.match(ANSI_ESC_PATTERN, unstripped_str[unstripped_i:])
        if match_res:
            cur_esc = unstripped_str[match_res.start() + unstripped_i:match_res.end() + unstripped_i]
            if start <= idx <= end:
                res += cur_esc
            unstripped_i += match_res.end()
        else:
            if start <= idx < end:
                if len(cur_esc) > 0 and idx == start and len(res) == 0:
                    res += cur_esc
                res += unstripped_str[unstripped_i]
            unstripped_i += 1
            idx += 1

    if len(res) > 0 and res[-len(RESET):] != RESET and res[-len(EOL):] != EOL:
        res += RESET
    return res


def indent_wrap(message, total_width, subsequent_indent_width):
    if total_width == -1:
        return message

    message = message.replace('\t', ' ' * 4)
    stripped_message = re.sub(ANSI_ESC_PATTERN, '', message)

    wrap_area = total_width - subsequent_indent_width
    messagebuf = ''
    current = 0
    while current < len(stripped_message):
        next_pos = min(current + wrap_area, len(stripped_message))
        messagebuf += substr(message, current, next_pos)
        if next_pos < len(message):
            messagebuf += '\n'
            messagebuf += ' ' * subsequent_indent_width
        current = next_pos
    return messagebuf


def split_to_lines(message, total_width, initial_indent_width=0, subsequent_indent_width=0):
    if total_width == -1:
        return message
    message = message.replace('\t', ' ' * 4)
    lines = []

    current_indent = initial_indent_width
    current_line = ''
    current_esc = RESET
    current_line_stripped_len = 0
    idx = 0
    while idx < len(message):
        matches = re.match(ANSI_ESC_PATTERN, message[idx:])
        if matches:
            current_esc = message[idx + matches.start():idx + matches.end()]
            current_line += current_esc
            idx += matches.end()
        else:
            current_line += message[idx]
            current_line_stripped_len += 1
            if current_line_stripped_len >= total_width - current_indent:
                if current_line[-len(RESET):] != RESET:
                    current_line += RESET
                lines.append(current_line)
                current_indent = subsequent_indent_width
                if current_esc == RESET:
                    current_line = ''
                else:
                    current_line = current_esc
                current_line_stripped_len = 0
            idx += 1
    if len(current_line) > 0:
        lines.append(current_line)
    return lines


LAST_USED = [RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN]
KNOWN_TAGS = {
    'dalvikvm': WHITE,
    'Process': WHITE,
    'ActivityManager': WHITE,
    'ActivityThread': WHITE,
    'AndroidRuntime': CYAN,
    'jdwp': WHITE,
    'StrictMode': WHITE,
    'DEBUG': YELLOW,
}


def allocate_color(tag):
    # this will allocate a unique format for the given tag
    # since we dont have very many colors, we always keep track of the LRU
    if tag not in KNOWN_TAGS:
        KNOWN_TAGS[tag] = LAST_USED[0]
    color = KNOWN_TAGS[tag]
    if color in LAST_USED:
        LAST_USED.remove(color)
        LAST_USED.append(color)
    return color


RULES = {
    # StrictMode policy violation; ~duration=319 ms:
    # android.os.StrictMode$StrictModeDiskWriteViolation: policy=31 violation=1
    re.compile(r'^(StrictMode policy violation)(; ~duration=)(\d+ ms)')
    : r'%s\1%s\2%s\3%s' % (termcolor(RED), RESET, termcolor(YELLOW), RESET),
}

# Only enable GC coloring if the user opted-in
if args.color_gc:
    # GC_CONCURRENT freed 3617K, 29% free 20525K/28648K, paused 4ms+5ms, total 85ms
    key = re.compile(r'^(GC_(?:CONCURRENT|FOR_M?ALLOC|EXTERNAL_ALLOC|EXPLICIT) )'
                     r'(freed <?\d+.)(, \d+% free \d+./\d+., )(paused \d+ms(?:\+\d+ms)?)')
    val = r'\1%s\2%s\3%s\4%s' % (termcolor(GREEN), RESET, termcolor(YELLOW), RESET)

    RULES[key] = val


TAGTYPES = {
    'V': colorize(' V ', fg=WHITE, bg=BLACK),
    'D': colorize(' D ', fg=BLACK, bg=BLUE),
    'I': colorize(' I ', fg=BLACK, bg=GREEN),
    'W': colorize(' W ', fg=BLACK, bg=YELLOW),
    'E': colorize(' E ', fg=BLACK, bg=RED),
    'F': colorize(' F ', fg=BLACK, bg=RED),
}

adb_command = base_adb_command[:]
adb_command.append('logcat')
adb_command.extend(['-v', 'time', 'brief'])

# Clear log before starting logcat
if args.clear_logcat:
    adb_clear_command = list(adb_command)
    adb_clear_command.append('-c')
    adb_clear = subprocess.Popen(adb_clear_command)

    while adb_clear.poll() is None:
        pass


# This is a ducktype of the subprocess.Popen object
class FakeStdinProcess():
    def __init__(self):
        self.stdout = sys.stdin

    def poll(self):
        return None


if sys.stdin.isatty():
    adb = subprocess.Popen(adb_command, stdin=PIPE, stdout=PIPE)
else:
    adb = FakeStdinProcess()
pids = set()
last_tag = None
app_pid = None


def match_packages(token):
    if len(package) == 0:
        return True
    if token in named_processes:
        return True
    index = token.find(':')
    return (token in catchall_package) if index == -1 else (token[:index] in catchall_package)


def parse_death(tag, message):
    if tag != 'ActivityManager':
        return None, None
    kill = PID_KILL.match(message)
    if kill:
        pid = kill.group(1)
        package_line = kill.group(2)
        if match_packages(package_line) and pid in pids:
            return pid, package_line
    leave = PID_LEAVE.match(message)
    if leave:
        pid = leave.group(2)
        package_line = leave.group(1)
        if match_packages(package_line) and pid in pids:
            return pid, package_line
    death = PID_DEATH.match(message)
    if death:
        pid = death.group(2)
        package_line = death.group(1)
        if match_packages(package_line) and pid in pids:
            return pid, package_line
    return None, None


def parse_start_proc(line):
    start = PID_START_5_1.match(line)
    if start is not None:
        line_pid, line_package, target = start.groups()
        return line_package, target, line_pid, '', ''
    start = PID_START.match(line)
    if start is not None:
        line_package, target, line_pid, line_uid, line_gids = start.groups()
        return line_package, target, line_pid, line_uid, line_gids
    start = PID_START_DALVIK.match(line)
    if start is not None:
        line_pid, line_package, line_uid = start.groups()
        return line_package, '', line_pid, line_uid, ''
    return None


def tag_in_tags_regex(tag, tags):
    return any(re.match(r'^' + t + r'$', tag) for t in map(str.strip, tags))


ps_command = base_adb_command + ['shell', 'ps']
ps_pid = subprocess.Popen(ps_command, stdin=PIPE, stdout=PIPE, stderr=PIPE)
while True:
    try:
        line = ps_pid.stdout.readline().decode('utf-8', 'replace').strip()
    except KeyboardInterrupt:
        print(RESET + EOL + '\n')
        print('KeyboardInterrupt')
        break
    if len(line) == 0:
        break

    pid_match = PID_LINE.match(line)
    if pid_match is not None:
        pid = pid_match.group(1)
        proc = pid_match.group(2)
        if proc in catchall_package:
            seen_pids = True
            pids.add(pid)


def add_timestap_header(time, line):
    if args.add_timestamp:
        line = time + " | " + line
    return line


if args.terminal_width_for_pipe_mode is not -1:
    input_src = sys.stdin
else:
    input_src = adb.stdout

try:
    while (args.terminal_width_for_pipe_mode is -1 and adb.poll() is None) or args.terminal_width_for_pipe_mode is not -1:
        try:
            line = input_src.readline().decode('utf-8', 'replace').strip()
            if tee_adb_file is not None:
                tee_adb_file.write(line.encode('utf-8'))
                tee_adb_file.write('\n'.encode('utf-8'))
                tee_adb_file.flush()
        except KeyboardInterrupt:
            print(RESET + EOL + '\n')
            print('KeyboardInterrupt')
            break
        if len(line) == 0:
            break

        bug_line = BUG_LINE.match(line)
        if bug_line is not None:
            continue

        log_line = LOG_LINE.match(line)
        if log_line:
            time, level, tag, owner, message = log_line.groups()
        else:
            log_line = LOG_LINE_NO_TIME.match(line)
            if log_line:
                level, tag, owner, message = log_line.groups()
                time = ''
            else:
                log_line = LOG_LINE_DEFAULT_FMT.match(line)
                if log_line:
                    time, owner, level, tag, message = log_line.groups()
                else:
                    continue

        tag = tag.strip()
        start = parse_start_proc(line)
        if start:
            line_package, target, line_pid, line_uid, line_gids = start
            if match_packages(line_package):
                pids.add(line_pid)

                app_pid = line_pid

                linebuf  = '\n'
                linebuf += colorize(' ' * (header_size - 1), bg=WHITE)
                linebuf += indent_wrap(' Process %s created for %s\n' % (line_package, target), width, header_size + args.extra_header_width)
                linebuf += colorize(' ' * (header_size - 1), bg=WHITE)
                linebuf += ' PID: %s   UID: %s   GIDs: %s' % (line_pid, line_uid, line_gids)
                linebuf += '\n'
                output_line(linebuf)
                last_tag = None # Ensure next log gets a tag printed

        dead_pid, dead_pname = parse_death(tag, message)
        if dead_pid:
            pids.remove(dead_pid)
            linebuf  = '\n'
            linebuf += colorize(' ' * (header_size - 1), bg=RED)
            linebuf += ' Process %s (PID: %s) ended' % (dead_pname, dead_pid)
            linebuf += '\n'
            output_line(linebuf)
            last_tag = None # Ensure next log gets a tag printed

        # Make sure the backtrace is printed after a native crash
        if tag == 'DEBUG':
            bt_line = BACKTRACE_LINE.match(message.lstrip())
            if bt_line is not None:
                message = message.lstrip()
                owner = app_pid

        if not args.all and owner not in pids:
            continue
        if level in LOG_LEVELS_MAP and LOG_LEVELS_MAP[level] < min_level:
            continue
        if args.ignored_tag and tag_in_tags_regex(tag, args.ignored_tag):
            continue
        if args.tag and not tag_in_tags_regex(tag, args.tag):
            continue

        linebuf = ''

        if args.tag_width > 0:
            # right-align tag title and allocate color if needed
            if tag != last_tag or args.always_tags:
                last_tag = tag
                color = allocate_color(tag)
                tag = tag[-args.tag_width:].rjust(args.tag_width)
                linebuf += colorize(tag, fg=color)
            else:
                linebuf += ' ' * args.tag_width
            linebuf += ' '

        # write out level colored edge
        if level in TAGTYPES:
            linebuf += TAGTYPES[level]
        else:
            linebuf += ' ' + level + ' '
        linebuf += ' '

        if args.keep_errors and (level == 'F' or level == 'E'):
            keep_line_on_stdout = True
        elif args.keep_warnings and (level == 'F' or level == 'E' or level == 'W'):
            keep_line_on_stdout = True
        elif args.addr2line_tool and args.addr2line_bin and NATIVE_CRASH_LINE.match(message):
            keep_line_on_stdout = True
        else:
            keep_line_on_stdout = False

            matches_grep = does_match_grep(message, grep_words_with_color, False)
            matches_igrep = does_match_grep(message, igrep_words_with_color, True)
            machtes_rgrep = does_match_regex_grep(message, rgrep_words_with_color)

            matches_grepv = does_match_grepv(message, excluded_words, False)
            matches_igrepv = does_match_grepv(message, iexcluded_words, True)
            machtes_rgrepv = does_match_regex_grepv(message, rexcluded_words)

            if matches_grep or matches_igrep or machtes_rgrep:
                keep_line_on_stdout = True
            elif matches_grepv or matches_igrepv or machtes_rgrepv:
                keep_line_on_stdout = False
            else:
                if empty(grep_words_with_color) and empty(igrep_words_with_color) and empty(rgrep_words_with_color):
                    keep_line_on_stdout = True
                else:
                    keep_line_on_stdout = False

        # format tag message using rules
        for matcher in RULES:
            replace = RULES[matcher]
            message = matcher.sub(replace, message)

        addr2line_lines = []
        if (level == 'F' or level == 'E') and args.addr2line_tool and args.addr2line_bin:
            for i in range(0, len(message)):
                matches_native_crash = NATIVE_CRASH_LINE.match(message[i:])
                if matches_native_crash:
                    crash_addr, crash_dir, crash_file_name, crash_ext_name = matches_native_crash.groups()
                    if crash_ext_name is not None:
                        crash_ext_name = crash_ext_name.split()[0]
                    tool = args.addr2line_tool
                    for lib_path in args.addr2line_bin:
                        matches_lib_path = FILE_PATH.match(lib_path)
                        if matches_lib_path:
                            lib_dir, lib_file_name, lib_ext_name = matches_lib_path.groups()
                            if crash_file_name == lib_file_name and crash_ext_name == lib_ext_name:
                                command = tool + ' -C -f -e ' + lib_path + ' ' + crash_addr
                                addr2line_res = subprocess.Popen(command, shell=True,
                                                                 stdout=subprocess.PIPE).stdout.read()
                                lines = addr2line_res.decode("utf-8").split('\n')
                                for line in lines:
                                    line = colorize(line, fg=BLACK, bg=GREEN, bold=True)
                                    line = add_timestap_header(time, line)
                                    line = linebuf + line
                                    addr2line_lines.append(line)
                                break
                    break

        words_to_color = grep_words_with_color + highlight_words_with_color
        iwords_to_color = igrep_words_with_color + ihighlight_words_with_color
        rwords_to_color = rgrep_words_with_color + rhighlight_words_with_color

        extracted_header = []
        if not empty(args.hide_header_regex):
            message, extracted_header, header_hidden = hide_header(message, args.hide_header_regex)
        message = ' '.join(extracted_header) + ' ' + message

        message = highlight(message, words_to_color, ignore_case=False)
        message = highlight(message, iwords_to_color, ignore_case=True)
        message = highlight(message, rwords_to_color, is_regex=True)

        message = add_timestap_header(time, message)

        lines = split_to_lines(message, width, header_size, header_size + args.extra_header_width)

        linebuf += ('\n' + ' ' * (header_size + args.extra_header_width)).join(lines)

        output_line(linebuf, keep_line_on_stdout)

        if not empty(addr2line_lines):
            for line in addr2line_lines:
                if not empty(line):
                    output_line(line, True)

except KeyboardInterrupt:
    print(RESET + EOL + '\n')
    print('KeyboardInterrupt')

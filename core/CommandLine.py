# core/CommandLine.py
import pygame as pg
import time
import types
import logging

from os.path import join

from .Envelopes import DirectionCommand, SonarCommand, DroneCommand, HitCommand, SurfaceCommand, SilenceCommand
from path import get_fonts_path
from config import AppConfig
from enums import codes, direction, command_type, hit_type, state, scene_state


class CommandLine:

    _send_to_operator: types.FunctionType

    _backspace_state: state
    _backspace_timer: int

    _config: AppConfig

    def __init__(self, config: AppConfig, send_to_operator_delegate: types.FunctionType):
        self._log = logging.getLogger(__name__)
        
        self._config = config
        self._send_to_operator = send_to_operator_delegate

        self._backspace_state = state.IDLE
        self._backspace_timer = 0

        font_path: str = join(get_fonts_path(), config.commandline.font)
        self._font: pg.font.Font = pg.font.Font(font_path, config.commandline.font_size)

        self._x, self._y = config.commandline.pos
        self._bottom: int = config.commandline.bottom
        self._default_text: str = config.commandline.default_text
        self._cut_off: int = len(self._default_text)
        self._text: str = self._default_text
        self._text_color = config.commandline.font_color
        self._text_surface: pg.Surface = self._font.render(self._text, True, self._text_color)

        self._history: list[str] = config.commandline.starting_text[::]
        self._history_indx: int = 0
        self._dy: int = config.commandline.font_size + config.commandline.font_spacing
        self._delta: int = 0

        self._cursor: pg.Rect = pg.Rect(0, 0, 8, 16)  # Construct dynamically, or set in the config
        self.adjust_cursor()

    def draw(self, screen: pg.Surface) -> None:
        offset: int = self._dy
        for text in self._history[::-1]:
            text_surface: pg.Surface = self._font.render(text, True, self._text_color)
            screen.blit(text_surface, (self._x, self._y + self._delta - offset))
            offset += self._dy

        screen.blit(self._text_surface, (self._x, self._y + self._delta))

        if time.time() % 1 > 0.5:
            pg.draw.rect(screen, self._text_color, self._cursor)

    def handle_event(self, event: pg.event.Event) -> scene_state:
        if event.type == pg.KEYDOWN:
            match event.key:
                case pg.K_RETURN:
                    self.append_history(self._text)
                    code = self.process_args(self.get_args())
                    if code == codes.EXIT:
                        return scene_state.POP_SCENE
                    self._text = self._default_text
                    self.update_text_surface()
                    self.adjust_cursor()
                case pg.K_BACKSPACE:
                    self._backspace_state = state.BUFFER
                    self._backspace_timer = 0
                    self.delete_char()
                    if event.mod & pg.KMOD_LCTRL:
                        self.delete_word()
                case pg.K_UP:
                    ...
                case pg.K_DOWN:
                    ...
                case _:
                    self._text += event.unicode
                    self.update_text_surface()
                    self.adjust_cursor()
        elif event.type == pg.KEYUP:
            match event.key:
                case pg.K_BACKSPACE:
                    self._backspace_state = state.IDLE
                    self._backspace_timer = 0
        return scene_state.CONTINUE

    def tick(self, dt: int):
        match self._backspace_state:
            case state.BUFFER:
                self._backspace_timer += dt
                if self._backspace_timer >= self._config.commandline.backspace_buffer:
                    self._backspace_state = state.REPEAT
                    self._backspace_timer = 0
            case state.REPEAT:
                self._backspace_timer += dt
                if self._backspace_timer >= self._config.commandline.backspace_repeat:
                    repeat_num: int = self._backspace_timer // self._config.commandline.backspace_repeat
                    while repeat_num > 0:
                        self.delete_char()
                        if pg.key.get_mods() & pg.KMOD_LCTRL:
                            self.delete_word()
                        repeat_num -= 1
                    self._backspace_timer %= self._config.commandline.backspace_repeat

    def get_last_char(self) -> str:
        if len(self._text) > self._cut_off:
            return self._text[-1]
        else:
            return ''

    def update_text_surface(self) -> None:
        self._text_surface = self._font.render(self._text, True, self._text_color)

    def get_args(self) -> list[str]:
        return self._text[self._cut_off:].split()

    def adjust_cursor(self) -> None:
        rect: pg.Rect = self._text_surface.get_rect(topleft=(self._x, self._y + self._delta))
        self._cursor.topleft = rect.topright

    def delete_char(self) -> None:
        if len(self._text) > self._cut_off:
            self._text = self._text[:-1]
            self.update_text_surface()
            self.adjust_cursor()

    def delete_word(self) -> None:
        while self.get_last_char() not in {' ', ''}:
            self.delete_char()

    def process_code(self, code: codes):
        match code:
            case codes.NO_COMMAND:
                self.append_history("ERROR: No command provided")
            case codes.COMMAND_NOT_RECOGNIZED:
                self.append_history("ERROR: Command not recognized")

    def process_args(self, args: list[str]) -> codes:
        if len(args) == 0:
            self.append_history("ERROR: No Command Detected")
            return

        command_args: list[str] = args[1:]
        return_code: codes

        match args[0].lower():
            case "direction" | "d":
                return_code = self.execute_direction(command_args)
            case "sonar" | "s":
                return_code = self.execute_sonar(command_args)
            case "drone" | "dr":
                return_code = self.execute_drone(command_args)
            case "hit" | "h":
                return_code = self.execute_hit(command_args)
            case "surface" | "su":
                return_code = self.execute_surface(command_args)
            case "silence" | "si":
                return_code = self.execute_silence(command_args)
            case "help":
                return_code = self.execute_help(command_args)
            case "exit":
                return_code = codes.EXIT
            case _:
                self.append_history("ERROR: Command Not Recognized")
                return codes.UNKNOWN

        match return_code:

            # Direction
            case codes.HEADING_ADDED: self.append_history("Heading Added")
            case codes.INTERSECTING_PATH: self.append_history("ERROR: Intersecting Path")

            # Sonar
            case codes.SONAR_ADDED: self.append_history("Sonar Added")

            # Drone
            case codes.DRONE_ADDED: self.append_history("Drone Added")

            # Hit
            case codes.HIT_ADDED: self.append_history("Hit Added")

            # Surface
            case codes.SURFACE_ADDED: self.append_history("Surface Added")

            # Silence
            case codes.HEADING_SILENCED: self.append_history("Current Heading Silenced")
            
            case codes.EXIT: self.append_history("Exiting...")

        return return_code

    def execute_direction(self, args: list[str]) -> codes:
        # >d[irection] <n[orth] | e[ast] | s[outh] | w[est]>
        if len(args) != 1:
            self.append_history(f"Unexpected arguments - expected 1, got {len(args)}")
            return codes.UNKNOWN

        envelope: DirectionCommand = DirectionCommand(
            command=command_type.DIRECTION,
            d=direction.NONE
        )

        match args[0].lower():

            case "north" | "n":
                envelope.d = direction.NORTH

            case "east" | "e":
                envelope.d = direction.EAST

            case "south" | "s":
                envelope.d = direction.SOUTH

            case "west" | "w":
                envelope.d = direction.WEST

            case _:
                self.append_history(f"Argument not recognized - expected <n[orth] | <e[ast] | s[outh] | w[est]>, got {args[0]}")
                return codes.UNKNOWN

        return self._send_to_operator(envelope)

    def execute_sonar(self, args: list[str]) -> codes:
        # >s[onar] -<rc | rs | cs> <arg1> <arg2>
        if len(args) != 3:
            self.append_history(f"Unexpected arguments - expected 3, got {len(args)}")
            return

        if not args[0].startswith("-"):
            self.append_history(f"Missing flag - first argument must be one of -rc, -rs, -cs (or a permutation of them), got {args[0]}")
            self.append_history("-rc denotes the next argument will be the row, followed by the column")
            self.append_history("-rs denotes the next argument will be the row, followed by the sector")
            self.append_history("-cs denotes the next argument will be the column, followed by the sector")
            return

        if len(args[0]) != 3:
            self.append_history(f"Invalid flag - expected 2, got {len(args[0]) - 1}")
            return

        flags: list[str] = []
        for char in args[0][1:].lower():
            if char not in {'r', 'c', 's'}:
                self.append_history(f"Invalid flag - must be one of r, c, or s, got {char}")
                return
            elif char in flags:
                self.append_history("Repeated flag - only one of each type of flag may be used")
                return
            flags.append(char)

        envelope: SonarCommand = SonarCommand(
            command=command_type.SONAR,
            row=-1,
            col=-1,
            sec=-1
        )

        indx: int = 1
        for flag in flags:
            arg: str = args[indx].lower()
            match flag:
                case "r":
                    row: int
                    if (row := self._validate_row(arg)) == -1:
                        return codes.UNKNOWN
                    envelope.row = row
                case "c":
                    column: int
                    if (column := self._validate_col(arg)) == -1:
                        return codes.UNKNOWN
                    envelope.col = column
                case "s":
                    sector: int
                    if (sector := self._validate_sec(arg)) == -1:
                        return codes.UNKNOWN
                    envelope.sec = sector
                case _:
                    assert False, "Unreachable"
            indx += 1

        return self._send_to_operator(envelope)

    def execute_drone(self, args: list[str]) -> codes:
        # >dr[one] <sector> <True | False>
        if len(args) != 2:
            self.append_history(f"Unexpected arguments - expected 2, got {len(args)}")
            return codes.UNKNOWN

        sector: int
        if (sector := self._validate_sec(args[0])) == -1:
            return codes.UNKNOWN

        arg_bool: bool

        match args[1].lower():

            case "true" | "t":
                arg_bool = True

            case "false" | "f":
                arg_bool = False

            case _:
                self.append(f"Invalid bool - expected t[rue] or f[alse], got {args[1]}")
                return codes.UNKNOWN

        envelope: DroneCommand = DroneCommand(
            command=command_type.DRONE,
            sec=sector,
            valid=arg_bool
        )

        return self._send_to_operator(envelope)

    def execute_hit(self, args: list[str]) -> codes:
        # >h[it] <row> <column> <d[irect] | i[ndirect] | m[iss]>
        if len(args) != 3:
            self.append_history(f"Unexpected arguments - expected 3, got {len(args)}")
            return codes.UNKNOWN

        row: int
        if (row := self._validate_row(args[0])) == -1:
            return codes.UNKNOWN

        column: int
        if (column := self._validate_col(args[1])) == -1:
            return codes.UNKNOWN

        envelope: HitCommand = HitCommand(
            command=command_type.HIT,
            row=row,
            col=column,
            hit=hit_type.UNKNOWN
        )

        match args[2].lower():

            case "direct" | "d":
                envelope.hit = hit_type.DIRECT

            case "indirect" | "i":
                envelope.hit = hit_type.INDIRECT

            case "miss" | "m":
                envelope.hit = hit_type.MISS

            case _:
                self.append_history(f"Invalid hit type - expected <d[irect] | i[ndirect] | m[iss]> got {args[2]}")
                return codes.UNKNOWN

        return self._send_to_operator(envelope)

    def execute_surface(self, args: list[str]) -> codes:
        # >su[rface] <sector>
        if len(args) != 1:
            self.append_history(f"Unexpected arguments - expected 1, got {len(args)}")
            return codes.UNKNOWN

        sector: int
        if (sector := self._validate_sec(args[0])) == -1:
            return codes.UNKNOWN

        envelope: SurfaceCommand = SurfaceCommand(
            command=command_type.SURFACE,
            sec=sector
        )

        return self._send_to_operator(envelope)

    def execute_silence(self, args: list[str]) -> codes:
        # >si[lence]
        if len(args) != 0:
            self.append_history(f"Unexpected arguments - expected 0, got {len(args)}")
            return codes.UNKNOWN

        envelope: SilenceCommand = SilenceCommand(
            command=command_type.SILENCE
        )

        return self._send_to_operator(envelope)

    def execute_help(self, args: list[str]) -> codes:
        # >help [command_name]
        if len(args) != 0 and len(args) != 1:
            self.append_history(f"Unexpected arguments - expected 0 or 1, got {len(args)}")
            return codes.UNKNOWN

        help_text: str
        if len(args) == 0:
            help_text = self._config.commandline.help_info["help"]
        else:
            help_text = self._config.commandline.help_info[args[0].lower()]
        self.append_history_mul(help_text)

    def _validate_row(self, arg_raw: str) -> int:
        if not arg_raw.isnumeric():
            self.append_history(f"Invalid row - expected a number, got {arg_raw}")
            return -1

        arg_num: int = int(arg_raw)
        if arg_num < 1 or arg_num > 15:
            self.append_history(f"Invalid row - expected 1-15, got {arg_num}")
            return -1

        return arg_num - 1  # Range of 1-15 is transformed into 0-14 so the index starts at 0

    def _validate_col(self, arg_raw: str) -> int:
        if len(arg_raw) != 1:
            self.append_history(f"Invalid column - expected 1 character, got {len(arg_raw)}")
            return -1

        arg_unicode: int = ord(arg_raw.lower())
        if arg_unicode < ord('a') or arg_unicode > ord('o'):
            self.append_history(f"Invalid column - expected a-o, got {arg_raw}")
            return -1

        return arg_unicode - ord('a')  # Rango of a-o is transformed to 0-14 so it starts at 0

    def _validate_sec(self, arg_raw: str) -> int:
        if not arg_raw.isnumeric():
            self.append(f"Invalid sector - expected a number, got {arg_raw}")
            return -1

        arg_num: int = int(arg_raw)
        if arg_num < 1 or arg_num > 9:
            self.append(f"Invalid sector - expected 1-9, got {arg_num}")
            return -1

        return arg_num  # Sectors don't need to start at 0 since they're not tied to an array

    def append_history(self, text: str) -> None:
        self._history.append(text)
        self._delta = min(self._delta + self._dy, self._bottom)

    def append_history_mul(self, texts: list[str]) -> None:
        for text in texts:
            self._history.append(text)
        self._delta = min(self._delta + self._dy * len(texts), self._bottom)

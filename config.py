# config.py
from dataclasses import dataclass
from typing import Tuple
from os.path import join, exists
import json

from path import get_config_path


@dataclass
class TitleSceneConfig:
    font: str
    button_font_size: int
    title_font_size: int
    start_button_pos: tuple[int, int]
    options_button_pos: tuple[int, int]
    button_width: int
    button_height: int
    button_border_radius: int
    button_border_width: int
    captain_text_pos: tuple[int, int]
    sonar_text_pos: tuple[int, int]
    resolution: tuple[int, int]
    title_box_rect: tuple[int, int, int, int]
    fade_step: int


@dataclass
class TileConfig:
    active_color: Tuple[int, int, int]
    font: str
    font_size: int
    land_color: Tuple[int, int, int]
    water_color: Tuple[int, int, int]
    target_color: Tuple[int, int, int]
    side_length: int
    target_radius: int
    border_radius: int
    border_width: int


@dataclass
class CommandHelpConfig:
    command_name: str
    aliases: list[str]
    flags: list[str]
    description: list[str]


@dataclass
class CommandLineConfig:
    font: str
    font_size: int
    font_spacing: int
    font_color: Tuple[int, int, int]
    pos: Tuple[int, int]
    bottom: int
    default_text: str
    starting_text: list[str]
    help_info: dict[str, CommandHelpConfig]
    backspace_buffer: int
    backspace_repeat: int


@dataclass
class ColorConfig:
    black: Tuple[int, int, int]
    white: Tuple[int, int, int]
    title: tuple[int, int, int]


@dataclass
class MapConfig:
    standard_length: int
    small_length: int
    spacing: int
    grid_size: int
    pos: Tuple[int, int]


@dataclass
class WindowConfig:
    caption: str
    icon_name: str
    _780p: Tuple[int, int]


@dataclass
class MusicConfig:
    title_intro: str
    title_loop: str


@dataclass
class GeneralConfig:
    fps: int
    default_font: str


@dataclass
class AppConfig:
    title_scene: TitleSceneConfig
    tile: TileConfig
    commandline: CommandLineConfig
    colors: ColorConfig
    maps: MapConfig
    window: WindowConfig
    music: MusicConfig
    general: GeneralConfig

    @staticmethod
    def fetch() -> 'AppConfig':
        config_path: str = join(get_config_path(), "config.json")
        valid = False
        if exists(config_path):
            with open(config_path, "r") as f:
                config: 'AppConfig' = json.load(f)
            if AppConfig.validate(config):
                valid = True
        
        if valid:
            return config
        else:
            return AppConfig.default()
    
    @staticmethod
    def validate(config: 'AppConfig') -> bool:
        return True
    
    @staticmethod
    def default() -> 'AppConfig':
        return AppConfig(
            title_scene=TitleSceneConfig(
                font="Px437_DG_One_bold.ttf",
                button_font_size=16,
                title_font_size=56,
                start_button_pos=(132.5, 250),
                options_button_pos=(132.5, 300),
                button_width=200,
                button_height=30,
                button_border_radius=4,
                button_border_width=1,
                captain_text_pos=(36.5, 35),
                sonar_text_pos=(92.5, 111),
                resolution=(465, 400),
                title_box_rect=(15, 15, 435, 165),
                fade_step=15
            ),
            tile=TileConfig(
                active_color=(250, 128, 114),
                font="Px437_EagleSpCGA_Alt1-2y.ttf",
                font_size=16,
                land_color=(6, 255, 6),
                water_color=(10, 80, 255),
                target_color=(255, 6, 0),
                side_length=30,
                target_radius=2,
                border_radius=2,
                border_width=1
            ),
            commandline=CommandLineConfig(
                font="Px437_EagleSpCGA_Alt1-2y.ttf",
                font_size=16,
                font_spacing=4,
                font_color=(204, 204, 204),
                pos=(650, 76),
                bottom=650,
                default_text="C:\\Users\\User>",
                starting_text=[
                    "Microsoft Windows [Version 10.0.19044.2604]",
                    "(c) Microsoft Corporation. All rights reserved.",
                    ""
                ],
                help_info={
                    "help": CommandHelpConfig(
                        command_name="help",
                        aliases=[],
                        flags=[],
                        description=[]
                    ),
                    "direction": CommandHelpConfig(
                        command_name="direction",
                        aliases=[
                            "d"
                        ],
                        flags=[],
                        description=[]
                    )
                },
                backspace_buffer=400,
                backspace_repeat=50
            ),
            colors=ColorConfig(
                black=(0, 0, 0),
                white=(255, 255, 255),
                title=(6, 100, 6)
            ),
            maps=MapConfig(
                standard_length=15,
                small_length=10,
                spacing=8,
                grid_size=15,
                pos=(50, 50)
            ),
            window=WindowConfig(
                caption="Caption Sonar",
                icon_name="radar.png",
                _780p=(1280, 720)
            ),
            music=MusicConfig(
                title_intro="intro_title_screen.wav",
                title_loop="loop_title_screen.wav"
            ),
            general=GeneralConfig(
                fps=60,
                default_font="arial"
            )
        )

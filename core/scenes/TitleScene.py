# core/scenes/TitleScene.py
import pygame as pg
from os.path import join
import logging

from .Scene import Scene
from config import AppConfig
from enums import scene_state
from path import get_fonts_path, get_media_path
from ..ux import Button

class TitleScene(Scene):
    
    # User Events
    _PLAY_BUTTON_CLICK: int = pg.USEREVENT + 1
    _OPTIONS_BUTTON_CLICK: int = pg.USEREVENT + 2
    _MUSIC_END: int = pg.USEREVENT + 3
    _FADE: int = pg.USEREVENT + 4
    
    def __init__(self, config: AppConfig):
        self._log = logging.getLogger(__name__)
        self._config = config
        self.set_window_config(self._config.title_scene.resolution)
        
        self._intro_music = join(get_media_path(), self._config.music.title_intro)
        self._loop_music = join(get_media_path(), self._config.music.title_loop)
        
        font_path = join(get_fonts_path(), self._config.title_scene.font)
        title_font = pg.font.Font(font_path, self._config.title_scene.title_font_size)
        button_font = pg.font.Font(font_path, self._config.title_scene.button_font_size)
        
        self._captain_surface = title_font.render("CAPTAIN", True, self._config.colors.title)
        self._sonar_suface = title_font.render("SONAR", True, self._config.colors.title)
        
        self._captain_pos = self._config.title_scene.captain_text_pos
        self._sonar_pos = self._config.title_scene.sonar_text_pos

        active = self._config.colors.white
        default = self._config.colors.title
        
        self._play_button = Button(self._config, "play", button_font, active, default, self._PLAY_BUTTON_CLICK)
        self._play_button.set_rect(
            self._config.title_scene.start_button_pos,
            self._config.title_scene.button_width,
            self._config.title_scene.button_height
        )
        
        self._options_button = Button(self._config, "options", button_font, active, default, self._OPTIONS_BUTTON_CLICK)
        self._options_button.set_rect(
            self._config.title_scene.options_button_pos,
            self._config.title_scene.button_width,
            self._config.title_scene.button_height
        )
        
        self._title_rect = pg.Rect(*self._config.title_scene.title_box_rect)
        
        self._fade_surface = pg.Surface(self._config.title_scene.resolution)
        self._fade_surface.fill(self._config.colors.black)
        pg.mixer.music.set_endevent(self._MUSIC_END)
        
        self._da = 1
        self._fade_max = 255
        self._fade_step = self._config.title_scene.fade_step
        self._fade_timer = 0
        self._fade_state = True
        
        self.reset_intro_anim()
    
    def tick(self, dt: int) -> scene_state:
        return_state = scene_state.CONTINUE
        
        for event in pg.event.get():
            self._play_button.handle_event(event)
            self._options_button.handle_event(event)
            return_state = self.mutate_state(return_state, self.handle_event(event))

        if self._fade_state:
            self._fade_timer += dt
            if self._fade_timer > self._fade_step:
                fade_num = self._fade_timer // self._fade_step
                alpha = max(self._fade_surface.get_alpha() - (fade_num * self._da), 0)
                if alpha == 0:
                    self._fade_state = False
                self._fade_surface.set_alpha(alpha)
                self._fade_timer %= self._fade_step
            
        
        self._screen.fill(self._config.colors.black)
        
        self.draw()
        
        pg.display.flip()
        
        return return_state
        
    def draw(self) -> None:
        # Buttons
        self._play_button.draw(self._screen)
        self._options_button.draw(self._screen)
        
        # Rects
        pg.draw.rect(self._screen, self._config.colors.title, self._title_rect, self._config.title_scene.button_border_width, self._config.title_scene.button_border_radius)
        
        # Text
        self._screen.blit(self._captain_surface, self._captain_pos)
        self._screen.blit(self._sonar_suface, self._sonar_pos)
        
        # Fade Surface
        self._screen.blit(self._fade_surface, (0, 0))
    
    def handle_event(self, event: pg.event.Event) -> scene_state:
        if event.type == pg.QUIT:
            return scene_state.QUIT
        elif event.type == self._MUSIC_END:
            pg.mixer.music.play(-1)
        elif event.type == pg.USEREVENT:
            if event.dict.get("button_type") == self._PLAY_BUTTON_CLICK:
                self._log.info("Play button clicked")
                return scene_state.PUSH_GAME_SCENE
            elif event.dict.get("button_type") == self._OPTIONS_BUTTON_CLICK:
                self._log.info("Options button clicked")
                return scene_state.PUSH_OPTIONS_SCENE
        return scene_state.CONTINUE
    
    def reset_intro_anim(self) -> None:
        self._fade_surface.set_alpha(self._fade_max)
        self._fade_state = True
        
        pg.mixer.music.load(self._intro_music)
        pg.mixer.music.queue(self._loop_music)
        pg.mixer.music.play()
    
    def on_enter(self) -> None:
        self.set_window_config(self._config.title_scene.resolution)
        # Add end event for music
        pg.mixer.music.set_endevent(self._MUSIC_END)
        pg.mixer.music.load(self._loop_music)
        pg.mixer.music.play(-1)
    
    def on_exit(self) -> None:
        pg.mixer.music.stop()
        # Remove end event for music
        pg.mixer.music.set_endevent()
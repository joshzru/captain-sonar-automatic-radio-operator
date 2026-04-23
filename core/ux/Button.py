# core/ux/Button.py
import pygame as pg
import logging

from config import AppConfig


class Button:
    """A button that pushes a user event on clickl
    """
    _rect: pg.rect.Rect = None
    _active = False
    
    def __init__(self, config: AppConfig, text: str, font: pg.font.Font, active: tuple[int, int ,int], default: tuple[int, int, int], flag: str | None=None):
        self._log = logging.getLogger(__name__)
        self._font = font
        self._flag = flag
        
        self._active_color = active
        self._default_color = default
        self._border_width = config.title_scene.button_border_width
        self._border_radius = config.title_scene.button_border_radius
        
        self._active_surface = self._font.render(text, True, active)
        self._default_surface = self._font.render(text, True, default)
        self._text_pos = (0, 0)
    
    def set_rect(self, pos: tuple[int, int], w: int, h: int) -> None:
        x, y = pos
        self._rect = pg.Rect(x, y, w, h)
        self.center_text()
    
    def center_text(self) -> None:
        if self._rect is None:
            return
        
        x, y = self._active_surface.get_rect(center=self._rect.center).topleft
        self._text_pos = (x, y)
    
    def draw(self, screen: pg.Surface):
        if self._active:
            pg.draw.rect(screen, self._active_color, self._rect, self._border_width, self._border_radius)
            screen.blit(self._active_surface, self._text_pos)
        else:
            pg.draw.rect(screen, self._default_color, self._rect, self._border_width, self._border_radius)
            screen.blit(self._default_surface, self._text_pos)
    
    def handle_event(self, event: pg.event.Event):
        if event.type == pg.MOUSEMOTION:
            self._active = self._rect.collidepoint(*event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and self._active:
            self.post_event()
    
    def post_event(self):
        if self._flag is not None:
            pg.event.post(pg.event.Event(pg.USEREVENT, button_type=self._flag))
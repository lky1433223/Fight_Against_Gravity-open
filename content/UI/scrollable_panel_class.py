import pygame
import os
import sys
from content.scene.scene_font import SceneFont
from content.UI.scrollbar import ScrollBar
from content.UI.panel_class import Panel


class ScrollablePanel(Panel):
    def __init__(self, settings, rect, text, font_size, ctrlrs=[], boxes=[], others=[], text_pos=1):
        """
        rect: 一个四元组，text:panel要显示的文字，
        buttons: panel里的按钮组件，列表形式
        boxes: panel里的输入框组件，列表形式,
        relative_pos: 组件相对于panel的比例,值为二维列表的字典形式.二维数组第一个值为横向比例，第二个值为纵向比例
        text_pos: 文字在panel中的位置，0靠上，1居中，2靠下
        """
        # 在panel里面画一个surface，把panel的surface画到
        # 把东西画到panel上，再把panel画到screen上。
        super().__init__(rect, text, font_size, ctrlrs, boxes, others, text_pos)
        height = self.rect.height
        # 计算surface的长
        for objs in self.loaded.values():
            for obj in objs:
                if obj.rect.bottom > height:
                    height = obj.rect.bottom
        self.surface = pygame.Surface((self.rect.width, height))
        self.surface.set_colorkey(self.color_key)
        self.surface.fill(self.color_key)

        # 滚动条协调
        sb_left = self.rect.width - 15
        self.scrollbar = ScrollBar([sb_left, 0, self.rect.height], settings)

    def render(self, screen, rect=pygame.Rect(0, 0, 0, 0)):
        if self.is_show:
            self.surface.fill(self.color)
            width, height = self.text_surface.get_size()
            if self.text_pos == 1:
                left = int((self.rect.width - width) / 2)
                top = int((self.rect.height - height) / 2)
            else:  # self.text_pos == 0
                left = int((self.rect.width - width) / 2)
                top = 20
            self.surface.blit(self.text_surface, (left, top))
            for objs in self.loaded.values():
                for obj in objs:
                    obj.render(self.surface)
            self.scrollbar.render(self.surface, self.scrollbar.ratio*(self.surface.get_height()-self.rect.height))
            screen.blit(self.surface, self.rect,
                        pygame.Rect(0, self.scrollbar.ratio*(self.surface.get_height()-self.rect.height),
                                    self.rect.width, self.rect.height))

    def update(self, event, pos_offset=(0, 0)) -> bool:
        if not self.is_able:
            return False
        pos_offset0 = pos_offset
        pos_offset = (self.rect[0]+pos_offset[0],
                      self.rect[1]+pos_offset[1]-self.scrollbar.ratio*(self.surface.get_height()-self.rect.height))
        self.scrollbar.deal_event(event, (self.rect[0] + pos_offset0[0], self.rect[1] + pos_offset0[1]))
        if self.deal_event_mouse(event, pos_offset, pos_offset0):
            return True
        self.deal_event_key(event)
        return False

    def update_mouse_motion(self, event, pos_offset=(0, 0)):
        pos_offset = (self.rect[0]+pos_offset[0],
                      self.rect[1]+pos_offset[1]-self.scrollbar.ratio*(self.surface.get_height()-self.rect.height))
        for bt in self.loaded['ctrlrs'][::-1]:
            if hasattr(bt, 'update_mouse_motion'):
                bt.update_mouse_motion(event, pos_offset)

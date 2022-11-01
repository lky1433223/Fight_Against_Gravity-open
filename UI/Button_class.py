# -*- coding: utf-8 -*-
import pygame
from Label_Class import Label

'''
按钮控件，主体是一个承载图像的surface和一个承载文字的Label控件
本质上是一个响应鼠标点击的矩形区域
使用方法，制定好参数创建好一个Button，然后render即可
'''


class Control:
    def __init__(self, rect: pygame.Rect, img_file: str, img_sub: int, text, font_info):
        """
        rect: pygame.Rect对象,决定控制组件的位置,也用于创建label, img_file: 图片文件路径,img_sub: 一个整数,表示这个图要被切成几张,text:文本内容,font_info: 字体设置
        属性：is_show: 是否显示这个控件，is_active:控件是否被激活，__img: 被加载好的图像，img_width:底图的长度，sub_img_width:子图宽度
        status:用于标记这个按钮可用还是不可用。
        """
        self.is_show = 1
        self.is_active = 0
        self.status = 1
        self.rect = rect
        self.img_sub = img_sub
        self.text = text
        self.font_info = font_info

        # 下面来处理控制组建的图像，加载进去并形成一个list
        if img_file is None:
            self.__img = None
            self.img_width = 0
        else:
            self.__img = pygame.image.load(img_file)
            self.__img = pygame.transform.smoothscale(self.__img, (self.rect.width, self.rect.height))
            self.__img.set_colorkey((246, 246, 246))
            self.__imgList = []

        # sub_width是指单独一个小按钮的宽度，整个img是一串连续的小按钮，我只在这里进行裁剪
        img_rect = self.__img.get_rect()
        sub_width = int(img_rect.width / img_sub)
        x = 0
        for i in range(self.img_sub):
            self.__imgList.append(self.__img.subsurface((x, 0), (sub_width, img_rect.height)))
            x += sub_width
        self.sub_img_width = sub_width

        # 下面设定Label对象，对于纯图片的按钮，没有text，没有text就没有label
        if text is None:
            self.label = None
        else:
            self.label = Label(rect.left, rect.top, text, font_info)

    def render(self, surface):
        if self.is_show:
            if self.__img is not None:
                surface.blit(self.__img, (self.rect.left, self.rect.top))
                # if self.status < self.img_sub:
                #     surface.blit(self.__imgList[self.status], (self.rect.left, self.rect.top))
            if self.label is not None:
                self.label.render(surface)

    def is_over(self, point) -> bool:
        if self.status <= 0:
            bflag = False
        else:
            bflag = self.rect.collidepoint(point)
        return bflag

    def check_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            return self.is_over(event.pos)

    def disable(self):
        self.status = 0

    def enable(self):
        self.status = 1

    def hide(self):
        self.is_show = 0


class Button(Control):
    def __init__(self, name: str, event_id, rect, img_file, img_sub, text="", font_info=None):
        Control.__init__(self, rect, img_file, img_sub, text, font_info)

        self.name = name
        self.event_id = event_id

    def set_text(self, text):
        self.label.set_text(text)

    # update :按钮更新状态，并上传事件
    def update(self, event):
        if self.check_click(event):
            data = {"from_ui": self.name, "status": self.status}
            ev = pygame.event.Event(self.event_id, data)
            pygame.event.post(ev)


class CheckBox(Control):
    def __init__(self, btn_name, rect, img_file, img_sub, text, font_info):
        Control.__init__(self, rect, img_file, img_sub, text, font_info)

        self.name = btn_name

        # 调整文字的位置
        if self.label is not None:
            x = rect.left + self.img_width
            y = rect.top + int(rect.height / 2)
            self.label.set_pos(x, y, 0, 1)

        self.status = 1

    def set_selected(self, flag):
        if flag:
            self.status = 2
        elif self.status > 0:
            self.status = 1

    def get_selected(self):
        return self.status == 2

    def update(self, event):
        if self.check_click(event):
            if self.status == 1:
                self.status = 2
            elif self.status == 2:
                self.status = 1


class RadioButton(CheckBox):
    def __init__(self, group_id, btn_name, rect, img_file, img_sub, text, font_info):
        CheckBox.__init__(self, btn_name, rect, img_file, img_sub, text, font_info)
        RADIO_CHANGE = pygame.USEREVENT + 7

        self.group_id = group_id
        self.event_id = RADIO_CHANGE

    def change_selected(self, group_id, from_id):
        if self.group_id == group_id:
            self.set_selected(self.name == from_id)

    def update(self, event):
        if self.check_click(event):
            data = {"from_ui": self.name}
            ev = pygame.event.Event(self.event_id, data)
            pygame.event.post(ev)
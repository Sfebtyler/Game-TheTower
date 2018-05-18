import pygame,sys


def sprite_sheet(size, file, pos=(0, 0)):

    # sprite size
    len_sprt_x, len_sprt_y = size
    # where to find first sprite on sheet
    sprt_rect_x, sprt_rect_y = pos

    # Load the sheet
    sheet = file
    sheet_rect = sheet.get_rect()
    sprites = []
    # rows
    for i in range(0, sheet_rect.height-len_sprt_y, size[1]):
        # columns
        for i in range(0, sheet_rect.width-len_sprt_x, size[0]):
            # find sprite you want
            sheet.set_clip(pygame.Rect(sprt_rect_x, sprt_rect_y, len_sprt_x, len_sprt_y))
            # grab the sprite you want
            sprite = sheet.subsurface(sheet.get_clip())
            sprites.append(sprite)

        sprt_rect_y += len_sprt_y
        sprt_rect_x = 0
    return sprites

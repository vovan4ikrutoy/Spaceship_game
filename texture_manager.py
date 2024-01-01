from pygame import image


cached_textures = dict()


def load_texture(img: str):
    global cached_textures
    if cached_textures.get(img) is not None:
        return cached_textures[img]
    else:
        cached_textures[img] = image.load(img)
        return cached_textures[img]

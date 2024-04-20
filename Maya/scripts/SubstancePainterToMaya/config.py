PLUGIN_NAME = 'Substance to Maya'
PLUGIN_VERSION = '0.5'
TEXTURE_FOLDER = 'textures'
INFOS = 'Original script by Tristan Legranche \ngithub.com/Strangenoise/SubstancePainterToMaya/\n\nUpdated workflow for Python3, Unreal, USD, and MaterialX by Derek Flood \nsharktacos.github.io/VFX-software-prefs '

PAINTER_IMAGE_EXTENSIONS = [
    'bmp', 'ico', 'jpeg', 'jpg', 'jng', 'pbm', 'pbmraw', 'pgm', 'pgmraw', 'png', 'ppm', 'ppmraw', 'targa',
    'tiff', 'tga', 'wbmp', 'xpm', 'gif', 'hdr', 'exr', 'j2k', 'jp2', 'pfm', 'webp', 'jpeg-xr', 'psd', 'tif'
]


BASE_COLOR = [
    'baseColor', 'BaseColor', 'basecolor', 'color', 'Color', 'albedo', 'Albedo', 'dif'
]
HEIGHT = [
    'height', 'Height', 'bump', 'Bump', 'bmp', 'BumpMap', 'bumpMap'
]
METALNESS = [
    'metal', 'Metal', 'metalness', 'Metalness', 'mtl', 'met'
]
NORMAL = [
    'normal', 'Normal', 'normalMap', 'NormalMap', 'nor'
]
ROUGHNESS = [
    'roughness', 'Roughness', 'specularRoughness', 'SpecularRoughness', 'specular', 'Specular', 'spc', 'ruf', 'orm', 'ORM'
]
MATTE = [
    'Matte', 'matte', 'msk'
]
LAYER = [
    'Layer', 'layer', 'lyr'
]
DISPLACE = [
    'displace', 'Displace', 'Displacement', 'displacement', 'displacementMap', 'DisplacementMap', 'dsp', 'disp'
]
OPACITY = [
    'Opacity', 'opacity', 'transparency', 'Transparency'
]
SUBSURFACE = [
    'subsurfaceColor', 'SubsurfaceColor', 'SSS', 'SSSColor', 'SSScolor', 'sss', 'sssColor', 'ssscolor'
]
EMISSION = [
    'emission', 'Emission', 'emissive', 'Emissive', 'light', 'Light', 'emi', 'Emi'
]

DELIMITERS = '-|_|@|\+| |\.'


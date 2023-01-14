
class config:
        
    def __init__(self):
        self.MAP_LIST = [
            '---- Choose', 'color', 'normal', 'specularColor',
            '---- Common Material Attributes', 'color', 'transparency', 
            'ambientColor', 'incandescence', 'bumpMapping', 
            'diffuse', 'translucence', 'translucenceDepth', 
            'translucenceFocus',
            '---- Specular Shading', 'eccentricity', 'specularRollOff', 
            'specularColor', 'reflectivity', 'reflectedColor',
            '---- Don\'t use'
        ]


        self.MAP_LIST_REAL_ATTRIBUTES = [
            '---- Choose', 'color', 'normalCamera', 'specularColor',
            '---- Common Material Attributes', 'color', 'transparency', 
            'ambientColor', 'incandescence', 'normalCamera', 
            'diffuse', 'translucence', 'translucenceDepth', 
            'translucenceFocus',
            '---- Specular Shading', 'eccentricity', 'specularRollOff', 
            'specularColor', 'reflectivity', 'reflectedColor',
            '---- Don\'t use'
        ]

        self.MAPS_INDICES = {
            'color': [
                ['baseColor', 'BaseColor', 'basecolor', 'color', 'Color','albedo', 'Albedo', 'diffuse', 'Diffuse', 'diff', 'Diff', 'dif'],
                1
            ],
            'normal': [
                ['normal', 'Normal', 'normalMap', 'NormalMap', 'nor'],
                2
            ],
            'roughness': [
                ['OcclusionRoughnessMetallic', 'OcclusionRoughnessMetal', 'OcclusionRoughnessMetalness', 'orm', 'ORM', 'roughness', 'Roughness', 'specularRoughness', 'SpecularRoughness', 'specular', 'Specular', 'spc', 'ruf', 'specularColor'],
                3
            ]
        }

        self.MAP_LIST_COLOR_ATTRIBUTES_INDICES = [1, 2, 3]
        self.DONT_USE_IDS = [0, 4, 14, 20]
        self.SHADER = 'blinn'
        self.NORMAL_NODE = 'bump2d'
        self.MIX_NODE = 'mix2'

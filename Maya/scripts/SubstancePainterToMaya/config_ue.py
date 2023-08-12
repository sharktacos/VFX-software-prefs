
class config:
        
    def __init__(self):
        self.MAP_LIST = [
            '---- Choose', 'color', 'normal', 'specularColor', 'emissive',
            '---- Common Material Attributes', 'color', 'transparency', 
            'ambientColor', 'incandescence', 'bumpMapping', 
            'diffuse', 'translucence', 'translucenceDepth', 
            'translucenceFocus',
            '---- Specular Shading', 'eccentricity', 'specularRollOff', 
            'specularColor', 'reflectivity', 'reflectedColor',
            '---- Don\'t use'
        ]


        self.MAP_LIST_REAL_ATTRIBUTES = [
            '---- Choose', 'color', 'normalCamera', 'specularColor', 'incandescence',
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
                ['OcclusionRoughnessMetallic', 'OcclusionRoughnessMetal', 'OcclusionRoughnessMetalness', 'orm', 'ORM', 'art', 'ART', 'roughness', 'Roughness', 'specularRoughness', 'SpecularRoughness', 'specular', 'Specular', 'spc', 'ruf', 'specularColor'],
                3
            ],
            'emissive': [
                ['Emissive', 'emissive', 'incandescence', 'Incandescence', 'emissiveColor', 'EmissiveColor', 'emi', 'Emi', 'emission', 'Emission', 'light', 'Light'],
                4
            ]
        }

        self.MAP_LIST_COLOR_ATTRIBUTES_INDICES = [1, 2, 3, 4]
        self.DONT_USE_IDS = [0, 5, 15, 21]
        self.SHADER = 'blinn'
        self.NORMAL_NODE = 'bump2d'
        self.MIX_NODE = 'mix2'

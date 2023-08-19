
class config:

    def __init__(self):
        self.MAP_LIST = [
            '---- Choose', 'baseColor', 'bump', 'metalness', 'normal', 'specularRoughness',
            '---- Base', 'baseWeight', 'baseColor', 'diffuseRoughness', 'metalness',
            '---- Specular', 'specWeight', 'specColor', 'specularRoughness', 'specIoR', 'specAnisotropy', 'rotation',
            '---- Transmission', 'transWeight', 'transColor', 'depth', 'scatter', 'transAnisotropy', 'dispertionAbbe',
            'extraRoughness',
            '---- Subsurface', 'sssWeight', 'sssColor', 'radius', 'scale', 'sssAnisotropy',
            '---- Coat', 'coatWeight', 'coatColor', 'coatRoughness', 'coatIoR', 'coatNormal',
            '---- Sheen', 'sheenWeight', 'color', 'roughness',
            '---- Emission', 'emissionWeight', 'emissionColor',
            '---- Thin film', 'thickness', 'thinIoR',
            '---- Geometry', 'opacity', 'bump', 'normal', 'anisotropyTangent',
            '---- Matte', 'matteColor', 'matteOpacity', 'LayerShader Mix2', 'displacement',
            '---- Don\'t use'
        ]

        self.MAP_LIST_REAL_ATTRIBUTES = [
            '---- Choose', 'baseColor', 'normalCamera', 'metalness', 'normalCamera', 'specularRoughness',
            '---- Base', 'base', 'baseColor', 'diffuseRoughness', 'metalness',
            '---- Specular', 'specular', 'specularColor', 'specularRoughness', 'specularIOR', 'specularAnisotropy',
            'specularRotation',
            '---- Transmission', 'transmission', 'transmissionColor', 'transmissionDepth', 'transmissionScatter',
            'transmissionScatterAnisotropy', 'transmissionDispersion', 'transmissionExtraRoughness',
            '---- Subsurface', 'subsurface', 'subsurfaceColor', 'subsurfaceRadius', 'subsurfaceScale', 'subsurfaceAnisotropy',
            '---- Coat', 'coat', 'coatColor', 'coatRoughness', 'coatIOR', 'coatNormal',
            '---- Sheen', 'sheen', 'sheenColor', 'sheenRoughness',
            '---- Emission', 'emission', 'emissionColor',
            '---- Thin film', 'thinFilmThickness', 'thinFilmIOR',
            '---- Geometry', 'opacity', 'normalCamera', 'normalCamera', 'tangent',
            '---- Matte', 'aiMatteColor', 'aiMatteColorA', 'mix2', 'displacementShader',
            '---- Don\'t use'
        ]

        self.MAPS_INDICES = {
            'baseColor': [
                ['baseColor', 'BaseColor', 'basecolor', 'color', 'Color','albedo', 'Albedo', 'diffuse', 'Diffuse', 'diff', 'Diff', 'dif'],
                1
            ],
            'bump': [
                ['height', 'Height','bump', 'Bump', 'BumpMap', 'bumpMap', 'bmp', ],
                2
            ],
            'metalness': [
                ['metal', 'Metal', 'metalness', 'Metalness', 'metallic', 'Metallic', 'mtl', 'met'],
                3
            ],
            'normal': [
                ['normal', 'Normal', 'normalMap', 'NormalMap', 'nor'],
                4
            ],
            'roughness': [
                ['roughness', 'Roughness', 'specularRoughness', 'SpecularRoughness', 'specular', 'Specular', 'spec', 'Spec', 'spc', 'ruf'],
                5
            ],
            'matte': [
                ['Matte', 'matte', 'msk'],
                0
            ],
             'layer': [
                ['Layer', 'layer', 'lyr'],
                56
            ],
             'displacement': [
                ['displace', 'Displace', 'Displacement', 'displacement', 'displacementMap', 'DisplacementMap', 'dsp', 'disp'],
                57
            ],
            'opacity': [
                ['Opacity', 'opacity', 'transparency', 'Transparency'],
                49
            ],
            'subsurface': [
                ['subsurfaceColor', 'SubsurfaceColor', 'SSS', 'SSSColor', 'SSScolor', 'sss', 'sssColor', 'ssscolor'],
                28
            ],
            'emission': [
                ['emission', 'Emission', 'emissive', 'Emissive', 'light', 'Light'],
                44
            ]
        }

        self.MAP_LIST_COLOR_ATTRIBUTES_INDICES = [1, 4, 7, 13, 20, 21, 28, 29, 34, 37, 40, 44, 49, 51, 52, 54]
        self.DONT_USE_IDS = [0, 6, 11, 18, 26, 32, 38, 42, 45, 48, 53]
        self.MAP_LAYER_ID = [56]
        self.SHADER = 'aiStandardSurface'
        self.SHADER_LYR = 'aiLayerShader'
        self.MIX_NODE = 'mix2'
        self.NORMAL_NODE = 'aiNormalMap'
        self.BUMP_NODE = 'aiBump2d'

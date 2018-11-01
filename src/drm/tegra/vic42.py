#!/usr/bin/python3

import ctypes, enum
import drm.tegra

class Method(enum.IntEnum):
    def set_surface_offset(slot, surface):
        return 0x1200 + (slot * 0x60) + (surface * 0x0c)

    def set_surface_y_offset(slot, surface):
        return Method.set_surface_offset(slot, surface) + 0x00

    def set_surface_u_offset(slot, surface):
        return Method.set_surface_offset(slot, surface) + 0x04

    def set_surface_v_offset(slot, surface):
        return Method.set_surface_offset(slot, surface) + 0x08

    SET_APPLICATION_ID = 0x0200
    EXECUTE = 0x0300
    SET_CONTROL_PARAMS = 0x0704
    SET_CONFIG_STRUCT_OFFSET = 0x0708
    SET_FILTER_STRUCT_OFFSET = 0x070c
    SET_HIST_OFFSET = 0x0714
    SET_OUTPUT_SURFACE_LUMA_OFFSET = 0x0720

    SET_SURFACE_LUMA_OFFSET = set_surface_y_offset
    SET_SURFACE_CHROMA_U_OFFSET = set_surface_u_offset
    SET_SURFACE_CHROMA_V_OFFSET = set_surface_v_offset

class SlotConfig(ctypes.Structure):
    _fields_ = [
            ('SlotEnable', ctypes.c_uint64, 1),
            ('DeNoise', ctypes.c_uint64, 1),
            ('AdvancedDenoise', ctypes.c_uint64, 1),
            ('CadenceDetect', ctypes.c_uint64, 1),
            ('MotionMap', ctypes.c_uint64, 1),
            ('MMapCombine', ctypes.c_uint64, 1),
            ('IsEven', ctypes.c_uint64, 1),
            ('ChromaEven', ctypes.c_uint64, 1),
            ('CurrentFieldEnable', ctypes.c_uint64, 1),
            ('PrevFieldEnable', ctypes.c_uint64, 1),
            ('NextFieldEnable', ctypes.c_uint64, 1),
            ('NextNrFieldEnable', ctypes.c_uint64, 1),
            ('CurMotionFieldEnable', ctypes.c_uint64, 1),
            ('PrevMotionFieldEnable', ctypes.c_uint64, 1),
            ('PpMotionFieldEnable', ctypes.c_uint64, 1),
            ('CombMotionFieldEnable', ctypes.c_uint64, 1),
            ('FrameFormat', ctypes.c_uint64, 4),
            ('FilterLengthY', ctypes.c_uint64, 2),
            ('FilterLengthX', ctypes.c_uint64, 2),
            ('Panoramic', ctypes.c_uint64, 12),
            ('ChromaUpLengthY', ctypes.c_uint64, 2),
            ('ChromaUpLengthX', ctypes.c_uint64, 2),
            ('reserved0', ctypes.c_uint64, 18),
            ('DetailFltClamp', ctypes.c_uint64, 6),
            ('FilterNoise', ctypes.c_uint64, 10),
            ('FilterDetail', ctypes.c_uint64, 10),
            ('ChromaNoise', ctypes.c_uint64, 10),
            ('ChromaDetail', ctypes.c_uint64, 10),
            ('DeinterlaceMode', ctypes.c_uint64, 4),
            ('MotionAccumWeight', ctypes.c_uint64, 3),
            ('NoiseIir', ctypes.c_uint64, 11),
            ('LightLevel', ctypes.c_uint64, 4),
            ('reserved1', ctypes.c_uint64, 2),
            # 128
            ('SoftClampLow', ctypes.c_uint64, 10),
            ('SoftClampHigh', ctypes.c_uint64, 10),
            ('reserved2', ctypes.c_uint64, 12),
            ('reserved3', ctypes.c_uint64, 2),
            ('PlanarAlpha', ctypes.c_uint64, 8),
            ('ConstantAlpha', ctypes.c_uint64, 1),
            ('StereoInterleave', ctypes.c_uint64, 3),
            ('ClipEnabled', ctypes.c_uint64, 1),
            ('ClearRectMask', ctypes.c_uint64, 8),
            ('DegammaMode', ctypes.c_uint64, 2),
            ('reserved4', ctypes.c_uint64, 1),
            ('DecompressEnable', ctypes.c_uint64, 1),
            ('DecompressKind', ctypes.c_uint64, 4),
            ('reserved5', ctypes.c_uint64, 1),
            ('DecompressCtbCount', ctypes.c_uint64, 8),
            ('DecompressZbcColor', ctypes.c_uint64, 32),
            ('reserved6', ctypes.c_uint64, 24),
            # 256
            ('SourceRectLeft', ctypes.c_uint64, 30),
            ('reserved7', ctypes.c_uint64, 2),
            ('SourceRectRight', ctypes.c_uint64, 30),
            ('reserved8', ctypes.c_uint64, 2),
            ('SourceRectTop', ctypes.c_uint64, 30),
            ('reserved9', ctypes.c_uint64, 2),
            ('SourceRectBottom', ctypes.c_uint64, 30),
            ('reserved10', ctypes.c_uint64, 2),
            # 384
            ('DestRectLeft', ctypes.c_uint64, 14),
            ('reserved11', ctypes.c_uint64, 2),
            ('DestRectRight', ctypes.c_uint64, 14),
            ('reserved12', ctypes.c_uint64, 2),
            ('DestRectTop', ctypes.c_uint64, 14),
            ('reserved13', ctypes.c_uint64, 2),
            ('DestRectBottom', ctypes.c_uint64, 14),
            ('reserved14', ctypes.c_uint64, 2),
            ('B16ScalerEnable', ctypes.c_uint64, 1),
            ('reserved15', ctypes.c_uint64, 31),
            ('reserved16', ctypes.c_uint64, 32)
        ]

class SlotSurfaceConfig(ctypes.Structure):
    _fields_ = [
            ('SlotPixelFormat', ctypes.c_uint64, 7),
            ('SlotChromaLocHoriz', ctypes.c_uint64, 2),
            ('SlotChromaLocVert', ctypes.c_uint64, 2),
            ('SlotBlkKind', ctypes.c_uint64, 4),
            ('SlotBlkHeight', ctypes.c_uint64, 4),
            ('SlotCacheWidth', ctypes.c_uint64, 3),
            ('reserved0', ctypes.c_uint64, 10),
            ('SlotSurfaceWidth', ctypes.c_uint64, 14),
            ('SlotSurfaceHeight', ctypes.c_uint64, 14),
            ('reserved1', ctypes.c_uint64, 4),
            ('SlotLumaWidth', ctypes.c_uint64, 14),
            ('SlotLumaHeight', ctypes.c_uint64, 14),
            ('reserved2', ctypes.c_uint64, 4),
            ('SlotChromaWidth', ctypes.c_uint64, 14),
            ('SlotChromaHeight', ctypes.c_uint64, 14),
            ('reserved3', ctypes.c_uint64, 4)
        ]

class LumaKeyStruct(ctypes.Structure):
    _fields_ = [
            ('luma_coeff0', ctypes.c_uint64, 20),
            ('luma_coeff1', ctypes.c_uint64, 20),
            ('luma_coeff2', ctypes.c_uint64, 20),
            ('luma_r_shift', ctypes.c_uint64, 4),
            ('luma_coeff3', ctypes.c_uint64, 20),
            ('LumaKeyLower', ctypes.c_uint64, 10),
            ('LumaKeyUpper', ctypes.c_uint64, 10),
            ('LumaKeyEnabled', ctypes.c_uint64, 1),
            ('reserved0', ctypes.c_uint64, 2),
            ('reserved1', ctypes.c_uint64, 21)
        ]

class MatrixStruct(ctypes.Structure):
    _fields_ = [
            ('matrix_coeff00', ctypes.c_uint64, 20),
            ('matrix_coeff10', ctypes.c_uint64, 20),
            ('matrix_coeff20', ctypes.c_uint64, 20),
            ('matrix_r_shift', ctypes.c_uint64, 4),
            ('matrix_coeff01', ctypes.c_uint64, 20),
            ('matrix_coeff11', ctypes.c_uint64, 20),
            ('matrix_coeff21', ctypes.c_uint64, 20),
            ('reserved0', ctypes.c_uint64, 3),
            ('matrix_enable', ctypes.c_uint64, 1),
            ('matrix_coeff02', ctypes.c_uint64, 20),
            ('matrix_coeff12', ctypes.c_uint64, 20),
            ('matrix_coeff22', ctypes.c_uint64, 20),
            ('reserved1', ctypes.c_uint64, 4),
            ('matrix_coeff03', ctypes.c_uint64, 20),
            ('matrix_coeff13', ctypes.c_uint64, 20),
            ('matrix_coeff23', ctypes.c_uint64, 20),
            ('reserved2', ctypes.c_uint64, 4)
        ]

class ClearRectStruct(ctypes.Structure):
    _fields_ = [
            ('ClearRect0Left', ctypes.c_uint64, 14),
            ('reserved0', ctypes.c_uint64, 2),
            ('ClearRect0Right', ctypes.c_uint64, 14),
            ('reserved1', ctypes.c_uint64, 2),
            ('ClearRect0Top', ctypes.c_uint64, 14),
            ('reserved2', ctypes.c_uint64, 2),
            ('ClearRect0Bottom', ctypes.c_uint64, 14),
            ('reserved3', ctypes.c_uint64, 2),
            ('ClearRect1Left', ctypes.c_uint64, 14),
            ('reserved4', ctypes.c_uint64, 2),
            ('ClearRect1Right', ctypes.c_uint64, 14),
            ('reserved5', ctypes.c_uint64, 2),
            ('ClearRect1Top', ctypes.c_uint64, 14),
            ('reserved6', ctypes.c_uint64, 2),
            ('ClearRect1Bottom', ctypes.c_uint64, 14),
            ('reserved7', ctypes.c_uint64, 2)
        ]

class BlendingSlotStruct(ctypes.Structure):
    _fields_ = [
            ('reserved0', ctypes.c_uint64, 2),
            ('AlphaK1', ctypes.c_uint64, 8),
            ('reserved1', ctypes.c_uint64, 6),
            ('AlphaK2', ctypes.c_uint64, 8),
            ('reserved2', ctypes.c_uint64, 6),
            ('SrcFactCMatchSelect', ctypes.c_uint64, 3),
            ('reserved3', ctypes.c_uint64, 1),
            ('DstFactCMatchSelect', ctypes.c_uint64, 3),
            ('reserved4', ctypes.c_uint64, 1),
            ('SrcFactAMatchSelect', ctypes.c_uint64, 3),
            ('reserved5', ctypes.c_uint64, 1),
            ('DstFactAMatchSelect', ctypes.c_uint64, 3),
            ('reserved6', ctypes.c_uint64, 1),
            ('reserved7', ctypes.c_uint64, 4),
            ('reserved8', ctypes.c_uint64, 4),
            ('reserved9', ctypes.c_uint64, 4),
            ('reserved10', ctypes.c_uint64, 4),
            ('reserved11', ctypes.c_uint64, 2),
            ('OverrideR', ctypes.c_uint64, 10),
            ('OverrideG', ctypes.c_uint64, 10),
            ('OverrideB', ctypes.c_uint64, 10),
            ('reserved12', ctypes.c_uint64, 2),
            ('OverrideA', ctypes.c_uint64, 8),
            ('reserved13', ctypes.c_uint64, 2),
            ('UseOverrideR', ctypes.c_uint64, 1),
            ('UseOverrideG', ctypes.c_uint64, 1),
            ('UseOverrideB', ctypes.c_uint64, 1),
            ('UseOverrideA', ctypes.c_uint64, 1),
            ('MaskR', ctypes.c_uint64, 1),
            ('MaskG', ctypes.c_uint64, 1),
            ('MaskB', ctypes.c_uint64, 1),
            ('MaskA', ctypes.c_uint64, 1),
            ('reserved14', ctypes.c_uint64, 12)
        ]

class OutputConfig(ctypes.Structure):
    _fields_ = [
            ('AlphaFillMode', ctypes.c_uint64, 3),
            ('AlphaFillSlot', ctypes.c_uint64, 3),
            ('reserved0', ctypes.c_uint64, 2),
            ('BackgroundAlpha', ctypes.c_uint64, 8),
            ('BackgroundR', ctypes.c_uint64, 10),
            ('BackgroundG', ctypes.c_uint64, 10),
            ('BackgroundB', ctypes.c_uint64, 10),
            ('RegammaMode', ctypes.c_uint64, 2),
            ('OutputFlipX', ctypes.c_uint64, 1),
            ('OutputFlipY', ctypes.c_uint64, 1),
            ('OutputTranspose', ctypes.c_uint64, 1),
            ('reserved1', ctypes.c_uint64, 1),
            ('reserved2', ctypes.c_uint64, 12),
            ('TargetRectLeft', ctypes.c_uint64, 14),
            ('reserved3', ctypes.c_uint64, 2),
            ('TargetRectRight', ctypes.c_uint64, 14),
            ('reserved4', ctypes.c_uint64, 2),
            ('TargetRectTop', ctypes.c_uint64, 14),
            ('reserved5', ctypes.c_uint64, 2),
            ('TargetRectBottom', ctypes.c_uint64, 14),
            ('reserved6', ctypes.c_uint64, 2)
        ]

class OutputSurfaceConfig(ctypes.Structure):
    _fields_ = [
            ('OutPixelFormat', ctypes.c_uint64, 7),
            ('OutChromaLocHoriz', ctypes.c_uint64, 2),
            ('OutChromaLocVert', ctypes.c_uint64, 2),
            ('OutBlkKind', ctypes.c_uint64, 4),
            ('OutBlkHeight', ctypes.c_uint64, 4),
            ('reserved0', ctypes.c_uint64, 3),
            ('reserved1', ctypes.c_uint64, 10),
            ('OutSurfaceWidth', ctypes.c_uint64, 14),
            ('OutSurfaceHeight', ctypes.c_uint64, 14),
            ('reserved2', ctypes.c_uint64, 4),
            ('OutLumaWidth', ctypes.c_uint64, 14),
            ('OutLumaHeight', ctypes.c_uint64, 14),
            ('reserved3', ctypes.c_uint64, 4),
            ('OutChromaWidth', ctypes.c_uint64, 14),
            ('OutChromaHeight', ctypes.c_uint64, 14),
            ('reserved4', ctypes.c_uint64, 4)
        ]

class FilterCoeffStruct(ctypes.Structure):
    _fields_ = [
            ('f00', ctypes.c_uint64, 10),
            ('f10', ctypes.c_uint64, 10),
            ('f20', ctypes.c_uint64, 10),
            ('reserved0', ctypes.c_uint64, 2),
            ('f01', ctypes.c_uint64, 10),
            ('f11', ctypes.c_uint64, 10),
            ('f21', ctypes.c_uint64, 10),
            ('reserved1', ctypes.c_uint64, 2),
            ('f02', ctypes.c_uint64, 10),
            ('f12', ctypes.c_uint64, 10),
            ('f22', ctypes.c_uint64, 10),
            ('reserved2', ctypes.c_uint64, 2),
            ('f03', ctypes.c_uint64, 10),
            ('f13', ctypes.c_uint64, 10),
            ('f23', ctypes.c_uint64, 10),
            ('reserved3', ctypes.c_uint64, 2)
        ]

class PipeConfig(ctypes.Structure):
    _fields_ = [
            ('DownsampleHoriz', ctypes.c_uint64, 11),
            ('reserved0', ctypes.c_uint64, 5),
            ('DownsampleVert', ctypes.c_uint64, 11),
            ('reserved1', ctypes.c_uint64, 5),
            ('reserved2', ctypes.c_uint64, 32),
            ('reserved3', ctypes.c_uint64, 32),
            ('reserved4', ctypes.c_uint64, 32)
        ]

class SlotHistoryBuffer(ctypes.Structure):
    _fields_ = [
            ('OldCadence', ctypes.c_uint64, 32),
            ('OldDiff', ctypes.c_uint64, 32),
            ('OldWeave', ctypes.c_uint64, 32),
            ('OlderWeave', ctypes.c_uint64, 32)
        ]

class PartitionCrcStruct(ctypes.Structure):
    _fields_ = [
            ('crc0', ctypes.c_uint64, 32),
            ('crc1', ctypes.c_uint64, 32),
            ('crc2', ctypes.c_uint64, 32),
            ('crc3', ctypes.c_uint64, 32)
        ]

class SlotCrcStruct(ctypes.Structure):
    _fields_ = [
            ('crc0', ctypes.c_uint64, 32),
            ('crc1', ctypes.c_uint64, 32)
        ]

class StatusStruct(ctypes.Structure):
    _fields_ = [
            ('ErrorStatus', ctypes.c_uint64, 32),
            ('CycleCount', ctypes.c_uint64, 32),
            ('reserved0', ctypes.c_uint64, 32),
            ('reserved1', ctypes.c_uint64, 32)
        ]

class CoeffPhaseParamStruct(ctypes.Structure):
    _fields_ = [
            ('coeff_0', ctypes.c_uint64, 10),
            ('reserved0', ctypes.c_uint64, 6),
            ('coeff_1', ctypes.c_uint64, 10),
            ('reserved1', ctypes.c_uint64, 6),
            ('coeff_2', ctypes.c_uint64, 10),
            ('reserved2', ctypes.c_uint64, 6),
            ('coeff_3', ctypes.c_uint64, 10),
            ('reserved3', ctypes.c_uint64, 6)
        ]

class GeoTranConfigParamStruct(ctypes.Structure):
    _fields_ = [
            ('GeoTranEn', ctypes.c_uint64, 1),
            ('GeoTranMode', ctypes.c_uint64, 2),
            ('IPTMode', ctypes.c_uint64, 1),
            ('PixelFilterType', ctypes.c_uint64, 2),
            ('PixelFormat', ctypes.c_uint64, 7),
            ('CacheWidth', ctypes.c_uint64, 3),
            ('SrcBlkKind', ctypes.c_uint64, 4),
            ('SrcBlkHeight', ctypes.c_uint64, 4),
            ('DstBlkKind', ctypes.c_uint64, 4),
            ('DstBlkHeight', ctypes.c_uint64, 4),
            ('MskBitMapEn', ctypes.c_uint64, 1),
            ('MaskedPixelFillMode', ctypes.c_uint64, 1),
            ('XSobelMode', ctypes.c_uint64, 2),
            ('SubFrameEn', ctypes.c_uint64, 1),
            ('reserved0', ctypes.c_uint64, 3),
            ('XSobelBlkKind', ctypes.c_uint64, 4),
            ('XSobelBlkHeight', ctypes.c_uint64, 4),
            ('XSobelDSBlkKind', ctypes.c_uint64, 4),
            ('XSobelDSBlkHeight', ctypes.c_uint64, 4),
            ('reserved1', ctypes.c_uint64, 8),
            ('NonFixedPatchEn', ctypes.c_uint64, 1),
            ('HorRegionNum', ctypes.c_uint64, 2),
            ('VerRegionNum', ctypes.c_uint64, 2),
            ('reserved2', ctypes.c_uint64, 3),
            ('log2HorSpace_0', ctypes.c_uint64, 3),
            ('log2VerSpace_0', ctypes.c_uint64, 3),
            ('log2HorSpace_1', ctypes.c_uint64, 3),
            ('log2VerSpace_1', ctypes.c_uint64, 3),
            ('log2HorSpace_2', ctypes.c_uint64, 3),
            ('log2VerSpace_2', ctypes.c_uint64, 3),
            ('log2HorSpace_3', ctypes.c_uint64, 3),
            ('log2VerSpace_3', ctypes.c_uint64, 3),
            ('horRegionWidth_0', ctypes.c_uint64, 14),
            ('reserved3', ctypes.c_uint64, 2),
            ('horRegionWidth_1', ctypes.c_uint64, 14),
            ('reserved4', ctypes.c_uint64, 2),
            ('horRegionWidth_2', ctypes.c_uint64, 14),
            ('reserved5', ctypes.c_uint64, 2),
            ('horRegionWidth_3', ctypes.c_uint64, 14),
            ('reserved6', ctypes.c_uint64, 2),
            ('verRegionHeight_0', ctypes.c_uint64, 14),
            ('reserved7', ctypes.c_uint64, 2),
            ('verRegionHeight_1', ctypes.c_uint64, 14),
            ('reserved8', ctypes.c_uint64, 2),
            ('verRegionHeight_2', ctypes.c_uint64, 14),
            ('reserved9', ctypes.c_uint64, 2),
            ('verRegionHeight_3', ctypes.c_uint64, 14),
            ('reserved10', ctypes.c_uint64, 2),
            ('IPT_M11', ctypes.c_uint64, 32),
            ('IPT_M12', ctypes.c_uint64, 32),
            ('IPT_M13', ctypes.c_uint64, 32),
            ('IPT_M21', ctypes.c_uint64, 32),
            ('IPT_M22', ctypes.c_uint64, 32),
            ('IPT_M23', ctypes.c_uint64, 32),
            ('IPT_M31', ctypes.c_uint64, 32),
            ('IPT_M32', ctypes.c_uint64, 32),
            ('IPT_M33', ctypes.c_uint64, 32),
            ('SourceRectLeft', ctypes.c_uint64, 14),
            ('reserved11', ctypes.c_uint64, 2),
            ('SourceRectRight', ctypes.c_uint64, 14),
            ('reserved12', ctypes.c_uint64, 2),
            ('SourceRectTop', ctypes.c_uint64, 14),
            ('reserved13', ctypes.c_uint64, 2),
            ('SourceRectBottom', ctypes.c_uint64, 14),
            ('reserved14', ctypes.c_uint64, 2),
            ('SrcImgWidth', ctypes.c_uint64, 14),
            ('reserved15', ctypes.c_uint64, 2),
            ('SrcImgHeight', ctypes.c_uint64, 14),
            ('reserved16', ctypes.c_uint64, 2),
            ('SrcSfcLumaWidth', ctypes.c_uint64, 14),
            ('reserved17', ctypes.c_uint64, 2),
            ('SrcSfcLumaHeight', ctypes.c_uint64, 14),
            ('reserved18', ctypes.c_uint64, 2),
            ('SrcSfcChromaWidth', ctypes.c_uint64, 14),
            ('reserved19', ctypes.c_uint64, 2),
            ('SrcSfcChromaHeight', ctypes.c_uint64, 14),
            ('reserved20', ctypes.c_uint64, 2),
            ('DestRectLeft', ctypes.c_uint64, 14),
            ('reserved21', ctypes.c_uint64, 2),
            ('DestRectRight', ctypes.c_uint64, 14),
            ('reserved22', ctypes.c_uint64, 2),
            ('DestRectTop', ctypes.c_uint64, 14),
            ('reserved23', ctypes.c_uint64, 2),
            ('DestRectBottom', ctypes.c_uint64, 14),
            ('reserved24', ctypes.c_uint64, 2),
            ('SubFrameRectTop', ctypes.c_uint64, 14),
            ('reserved25', ctypes.c_uint64, 2),
            ('SubFrameRectBottom', ctypes.c_uint64, 14),
            ('reserved26', ctypes.c_uint64, 2),
            ('DestSfcLumaWidth', ctypes.c_uint64, 14),
            ('reserved27', ctypes.c_uint64, 2),
            ('DestSfcLumaHeight', ctypes.c_uint64, 14),
            ('reserved28', ctypes.c_uint64, 2),
            ('DestSfcChromaWidth', ctypes.c_uint64, 14),
            ('reserved29', ctypes.c_uint64, 2),
            ('DestSfcChromaHeight', ctypes.c_uint64, 14),
            ('reserved30', ctypes.c_uint64, 2),
            ('SparseWarpMapWidth', ctypes.c_uint64, 14),
            ('reserved31', ctypes.c_uint64, 2),
            ('SparseWarpMapHeight', ctypes.c_uint64, 14),
            ('reserved32', ctypes.c_uint64, 2),
            ('SparseWarpMapStride', ctypes.c_uint64, 14),
            ('reserved33', ctypes.c_uint64, 2),
            ('MaskBitMapWidth', ctypes.c_uint64, 14),
            ('reserved34', ctypes.c_uint64, 2),
            ('MaskBitMapHeight', ctypes.c_uint64, 14),
            ('reserved35', ctypes.c_uint64, 2),
            ('MaskBitMapStride', ctypes.c_uint64, 14),
            ('reserved36', ctypes.c_uint64, 2),
            ('XSobelWidth', ctypes.c_uint64, 14),
            ('reserved37', ctypes.c_uint64, 2),
            ('XSobelHeight', ctypes.c_uint64, 14),
            ('reserved38', ctypes.c_uint64, 2),
            ('XSobelStride', ctypes.c_uint64, 14),
            ('reserved39', ctypes.c_uint64, 2),
            ('DSStride', ctypes.c_uint64, 14),
            ('reserved40', ctypes.c_uint64, 2),
            ('XSobelTopOffset', ctypes.c_uint64, 32),
            ('reserved41', ctypes.c_uint64, 32),
            ('maskY', ctypes.c_uint64, 16),
            ('maskU', ctypes.c_uint64, 16),
            ('maskV', ctypes.c_uint64, 16),
            ('reserved42', ctypes.c_uint64, 16),
        ]

class TNR3ConfigParamStruct(ctypes.Structure):
    _fields_ = [
            ('TNR3En', ctypes.c_uint64, 1),
            ('BetaBlendingEn', ctypes.c_uint64, 1),
            ('AlphaBlendingEn', ctypes.c_uint64, 1),
            ('AlphaSmoothEn', ctypes.c_uint64, 1),
            ('TempAlphaRestrictEn', ctypes.c_uint64, 1),
            ('AlphaClipEn', ctypes.c_uint64, 1),
            ('BFRangeEn', ctypes.c_uint64, 1),
            ('BFDomainEn', ctypes.c_uint64, 1),
            ('BFRangeLumaShift', ctypes.c_uint64, 4),
            ('BFRangeChromaShift', ctypes.c_uint64, 4),
            ('SADMultiplier', ctypes.c_uint64, 6),
            ('reserved0', ctypes.c_uint64, 2),
            ('SADWeightLuma', ctypes.c_uint64, 6),
            ('reserved1', ctypes.c_uint64, 2),
            ('TempAlphaRestrictIncCap', ctypes.c_uint64, 11),
            ('reserved2', ctypes.c_uint64, 5),
            ('AlphaScaleIIR', ctypes.c_uint64, 11),
            ('reserved3', ctypes.c_uint64, 5),
            ('AlphaClipMaxLuma', ctypes.c_uint64, 11),
            ('reserved4', ctypes.c_uint64, 5),
            ('AlphaClipMinLuma', ctypes.c_uint64, 11),
            ('reserved5', ctypes.c_uint64, 5),
            ('AlphaClipMaxChroma', ctypes.c_uint64, 11),
            ('reserved6', ctypes.c_uint64, 5),
            ('AlphaClipMinChroma', ctypes.c_uint64, 11),
            ('reserved7', ctypes.c_uint64, 5),
            ('BetaCalcMaxBeta', ctypes.c_uint64, 11),
            ('reserved8', ctypes.c_uint64, 5),
            ('BetaCalcMinBeta', ctypes.c_uint64, 11),
            ('reserved9', ctypes.c_uint64, 5),
            ('BetaCalcBetaX1', ctypes.c_uint64, 11),
            ('reserved10', ctypes.c_uint64, 5),
            ('BetaCalcBetaX2', ctypes.c_uint64, 11),
            ('reserved11', ctypes.c_uint64, 5),
            ('BetaCalcStepBeta', ctypes.c_uint64, 11),
            ('reserved12', ctypes.c_uint64, 5),
            ('reserved13', ctypes.c_uint64, 16),
            ('BFDomainLumaCoeffC00', ctypes.c_uint64, 7),
            ('reserved14', ctypes.c_uint64, 1),
            ('BFDomainLumaCoeffC01', ctypes.c_uint64, 7),
            ('reserved15', ctypes.c_uint64, 1),
            ('BFDomainLumaCoeffC02', ctypes.c_uint64, 7),
            ('reserved16', ctypes.c_uint64, 1),
            ('BFDomainLumaCoeffC11', ctypes.c_uint64, 7),
            ('reserved17', ctypes.c_uint64, 1),
            ('BFDomainLumaCoeffC12', ctypes.c_uint64, 7),
            ('reserved18', ctypes.c_uint64, 1),
            ('BFDomainLumaCoeffC22', ctypes.c_uint64, 7),
            ('reserved19', ctypes.c_uint64, 1),
            ('reserved20', ctypes.c_uint64, 16),
            ('BFDomainChromaCoeffC00', ctypes.c_uint64, 7),
            ('reserved21', ctypes.c_uint64, 1),
            ('BFDomainChromaCoeffC01', ctypes.c_uint64, 7),
            ('reserved22', ctypes.c_uint64, 1),
            ('BFDomainChromaCoeffC02', ctypes.c_uint64, 7),
            ('reserved23', ctypes.c_uint64, 1),
            ('BFDomainChromaCoeffC11', ctypes.c_uint64, 7),
            ('reserved24', ctypes.c_uint64, 1),
            ('BFDomainChromaCoeffC12', ctypes.c_uint64, 7),
            ('reserved25', ctypes.c_uint64, 1),
            ('BFDomainChromaCoeffC22', ctypes.c_uint64, 7),
            ('reserved26', ctypes.c_uint64, 1),
            ('reserved27', ctypes.c_uint64, 16),
            ('LeftBufSize', ctypes.c_uint64, 32),
            ('TopBufSize', ctypes.c_uint64, 32),
            ('AlphaSufStride', ctypes.c_uint64, 14),
            ('reserved28', ctypes.c_uint64, 18)
        ]

class BFRangeTableItems(ctypes.Structure):
    _fields_ = [
            ('item0', ctypes.c_uint64, 7),
            ('reserved0', ctypes.c_uint64, 9),
            ('item1', ctypes.c_uint64, 7),
            ('reserved1', ctypes.c_uint64, 9),
            ('item2', ctypes.c_uint64, 7),
            ('reserved2', ctypes.c_uint64, 9),
            ('item3', ctypes.c_uint64, 7),
            ('reserved3', ctypes.c_uint64, 9)
        ]

class SlotStruct(ctypes.Structure):
    _fields_ = [
            ('slotConfig', SlotConfig),
            ('slotSurfaceConfig', SlotSurfaceConfig),
            ('lumaKeyStruct', LumaKeyStruct),
            ('colorMatrixStruct', MatrixStruct),
            ('gamutMatrixStruct', MatrixStruct),
            ('blendingSlotStruct', BlendingSlotStruct),
        ]

class FilterStruct(ctypes.Structure):
    _fields_ = [
            ('filterCoeffStruct', 520 * FilterCoeffStruct)
        ]

class ConfigStruct(ctypes.Structure):
    _fields_ = [
            ('pipeConfig', PipeConfig),
            ('outputConfig', OutputConfig),
            ('outputSurfaceConfig', OutputSurfaceConfig),
            ('outColorMatrixStruct', MatrixStruct),
            ('clearRectStruct', 4 * ClearRectStruct),
            ('slotStruct', 16 * SlotStruct),
        ]

class InterfaceStruct(ctypes.Structure):
    _fields_ = [
            ('partitionCrcStruct', 2 * PartitionCrcStruct)
        ]

class InputCrcStruct(ctypes.Structure):
    _fields_ = [
            ('slotCrcStruct', 16 * SlotCrcStruct)
        ]

class GeoTranConfigStruct(ctypes.Structure):
    _fields_ = [
            ('paramConfig', GeoTranConfigParamStruct),
            ('FilterCoeff', 17 * CoeffPhaseParamStruct),
            ('tnr3Config', TNR3ConfigParamStruct),
            ('BFRangeTableLuma', 16 * BFRangeTableItems),
            ('BFRangeTableChroma', 16 * BFRangeTableItems)
        ]

class VIC(drm.tegra.VIC):
    def clear(self, image, red, green, blue, alpha):
        mapping = self.config.map()

        config = ConfigStruct.from_buffer(mapping)
        config.outputConfig.AlphaFillMode = drm.tegra.VIC.AlphaFillMode.BACKGROUND
        config.outputConfig.BackgroundAlpha = int(alpha * 255)
        config.outputConfig.BackgroundR = int(red * 1023)
        config.outputConfig.BackgroundG = int(green * 1023)
        config.outputConfig.BackgroundB = int(blue * 1023)
        config.outputConfig.TargetRectTop = 0
        config.outputConfig.TargetRectLeft = 0
        config.outputConfig.TargetRectRight = image.width - 1
        config.outputConfig.TargetRectBottom = image.height - 1

        config.outputSurfaceConfig.OutPixelFormat = image.format
        config.outputSurfaceConfig.OutBlkKind = image.kind
        config.outputSurfaceConfig.OutBlkHeight = 0
        config.outputSurfaceConfig.OutSurfaceWidth = image.width - 1
        config.outputSurfaceConfig.OutSurfaceHeight = image.height - 1
        config.outputSurfaceConfig.OutLumaWidth = image.stride - 1
        config.outputSurfaceConfig.OutLumaHeight = image.height - 1
        config.outputSurfaceConfig.OutChromaWidth = 16383
        config.outputSurfaceConfig.OutChromaHeight = 16383

        del config
        mapping.close()

    def execute(self, output, inputs = []):
        job = drm.tegra.Job(self.channel)
        job.push_begin()

        self.map(output.buffer, drm.tegra.Mapping.Flags.WRITE)

        self.push_method(job, Method.SET_APPLICATION_ID, 1)
        self.push_method(job, Method.SET_CONTROL_PARAMS, (ctypes.sizeof(ConfigStruct) // 16) << 16)
        self.push_buffer(job, Method.SET_CONFIG_STRUCT_OFFSET, self.mappings[self.config], 0, 0)
        self.push_buffer(job, Method.SET_FILTER_STRUCT_OFFSET, self.mappings[self.filter], 0, 0)
        self.push_buffer(job, Method.SET_OUTPUT_SURFACE_LUMA_OFFSET, self.mappings[output.buffer], 0, 0)

        for i, image in enumerate(inputs):
            self.map(image.buffer, drm.tegra.Mapping.Flags.READ)

            self.push_buffer(job, Method.SET_SURFACE_LUMA_OFFSET(0, i), self.mappings[image.buffer], 0, 0)

        self.push_method(job, Method.EXECUTE, 1 << 8)
        job.push_sync_cond(self.syncpt, self.syncpt.COND_OP_DONE)
        job.push_end()

        job.submit()

        job.wait(250000000)

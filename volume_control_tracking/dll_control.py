import comtypes
from comtypes import *
import comtypes.client
from ctypes import POINTER
from ctypes.wintypes import DWORD, BOOL

MMDeviceApiLib = GUID("{2FDAAFA3-7523-4F66-9957-9D5E7FE698F6}")
IID_IMMDevice = GUID("{D666063F-1587-4E43-81F1-B948E807363F}")
IID_IMMDeviceEnumerator = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")
CLSID_MMDeviceEnumerator = GUID("{BCDE0395-E52F-467C-8E3D-C4579291692E}")
IID_IMMDeviceCollection = GUID("{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}")
IID_IAudioEndpointVolume = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")


class IMMDeviceCollection(IUnknown):
    _iid_ = GUID("{0BD7A1BE-7A1A-44DB-8397-CC5392387B5E}")
    pass


class IAudioEndpointVolume(IUnknown):
    _iid_ = GUID("{5CDF2C82-841E-4546-9722-0CF74078229A}")
    _methods_ = [
        STDMETHOD(HRESULT, "RegisterControlChangeNotify", []),
        STDMETHOD(HRESULT, "UnregisterControlChangeNotify", []),
        STDMETHOD(HRESULT, "GetChannelCount", []),
        COMMETHOD(
            [],
            HRESULT,
            "SetMasterVolumeLevel",
            (["in"], c_float, "fLevelDB"),
            (["in"], POINTER(GUID), "pguidEventContext"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "SetMasterVolumeLevelScalar",
            (["in"], c_float, "fLevelDB"),
            (["in"], POINTER(GUID), "pguidEventContext"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMasterVolumeLevel",
            (["out", "retval"], POINTER(c_float), "pfLevelDB"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetMasterVolumeLevelScalar",
            (["out", "retval"], POINTER(c_float), "pfLevelDB"),
        ),
    ]


class IMMDevice(IUnknown):
    _iid_ = GUID("{D666063F-1587-4E43-81F1-B948E807363F}")
    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "Activate",
            (["in"], POINTER(GUID), "iid"),
            (["in"], DWORD, "dwClsCtx"),
            (["in"], POINTER(DWORD), "pActivationParans"),
            (["out", "retval"], POINTER(POINTER(IAudioEndpointVolume)), "ppInterface"),
        ),
        STDMETHOD(HRESULT, "OpenPropertyStore", []),
        STDMETHOD(HRESULT, "GetId", []),
        STDMETHOD(HRESULT, "GetState", []),
    ]
    pass


class IMMDeviceEnumerator(comtypes.IUnknown):
    _iid_ = GUID("{A95664D2-9614-4F35-A746-DE8DB63617E6}")

    _methods_ = [
        COMMETHOD(
            [],
            HRESULT,
            "EnumAudioEndpoints",
            (["in"], DWORD, "dataFlow"),
            (["in"], DWORD, "dwStateMask"),
            (["out", "retval"], POINTER(POINTER(IMMDeviceCollection)), "ppDevices"),
        ),
        COMMETHOD(
            [],
            HRESULT,
            "GetDefaultAudioEndpoint",
            (["in"], DWORD, "dataFlow"),
            (["in"], DWORD, "role"),
            (["out", "retval"], POINTER(POINTER(IMMDevice)), "ppDevices"),
        ),
    ]


class AudioController:
    def __init__(self):
        self.enumerator = comtypes.CoCreateInstance(
            CLSID_MMDeviceEnumerator, IMMDeviceEnumerator, CLSCTX_INPROC_SERVER
        )
        self.endpoint = self.enumerator.GetDefaultAudioEndpoint(0, 1)
        self.volume = self.endpoint.Activate(IID_IAudioEndpointVolume, CLSCTX_INPROC_SERVER, None)

    def get_volume(self):
        volume_level = self.volume.GetMasterVolumeLevelScalar()
        return volume_level

    def set_volume(self, level):
        new_volume = self.get_volume() + level
        if new_volume < 0 or new_volume > 1:
            pass
        else:
            self.volume.SetMasterVolumeLevelScalar(new_volume, None)

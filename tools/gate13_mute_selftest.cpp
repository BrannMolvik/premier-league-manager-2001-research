// Minimal x86 Windows SDK self-test. No original game, DLL injection, GUI,
// nonzero PCM, endpoint master-volume control or other-process modification.
// Build with MSVC /W4 /WX; execute ONLY after approved Authenticode signing and
// SignTool verification. Passing this test does not authorize FM2001 execution.
#define WIN32_LEAN_AND_MEAN
#define NOMINMAX
#include <windows.h>
#include <mmdeviceapi.h>
#include <audiopolicy.h>
#include <mmsystem.h>
#include <wrl/client.h>
#include <array>
#include <cstdio>
#include <vector>

using Microsoft::WRL::ComPtr;
static_assert(sizeof(void*) == 4, "This probe must be built as native x86");

struct EndpointSession {
    ComPtr<ISimpleAudioVolume> volume;
    ComPtr<IAudioSessionControl2> control;
};

static HRESULT CheckMute(const std::vector<EndpointSession>& sessions) {
    if (sessions.empty()) return E_UNEXPECTED;
    for (const auto& session : sessions) {
        BOOL muted = FALSE;
        HRESULT hr = session.volume->GetMute(&muted);
        if (FAILED(hr)) return hr;
        if (!muted) return E_ACCESSDENIED;
        DWORD pid = 0;
        hr = session.control->GetProcessId(&pid);
        if (hr != S_OK || pid != GetCurrentProcessId()) return E_ACCESSDENIED;
    }
    return S_OK;
}

static HRESULT MuteOwnEmptySessions(std::vector<EndpointSession>& sessions) {
    ComPtr<IMMDeviceEnumerator> enumerator;
    HRESULT hr = CoCreateInstance(__uuidof(MMDeviceEnumerator), nullptr,
        CLSCTX_INPROC_SERVER, IID_PPV_ARGS(enumerator.GetAddressOf()));
    if (FAILED(hr)) return hr;
    ComPtr<IMMDeviceCollection> devices;
    hr = enumerator->EnumAudioEndpoints(eRender, DEVICE_STATE_ACTIVE, devices.GetAddressOf());
    if (FAILED(hr)) return hr;
    UINT count = 0;
    hr = devices->GetCount(&count);
    if (FAILED(hr)) return hr;
    if (count == 0 || count > 64) return E_UNEXPECTED;
    for (UINT i = 0; i < count; ++i) {
        ComPtr<IMMDevice> device;
        hr = devices->Item(i, device.GetAddressOf());
        if (FAILED(hr)) return hr;
        ComPtr<IAudioSessionManager> manager;
        hr = device->Activate(__uuidof(IAudioSessionManager), CLSCTX_INPROC_SERVER,
            nullptr, reinterpret_cast<void**>(manager.GetAddressOf()));
        if (FAILED(hr)) return hr;
        EndpointSession session;
        // NULL GUID, cross-process FALSE: creates THIS process's empty default
        // session before audio. No PID polling race, custom session or global mute.
        hr = manager->GetSimpleAudioVolume(nullptr, 0, session.volume.GetAddressOf());
        if (FAILED(hr)) return hr;
        ComPtr<IAudioSessionControl> control;
        hr = manager->GetAudioSessionControl(nullptr, 0, control.GetAddressOf());
        if (FAILED(hr)) return hr;
        hr = control.As(&session.control);
        if (FAILED(hr)) return hr;
        DWORD owner = 0;
        hr = session.control->GetProcessId(&owner);
        if (hr != S_OK || owner != GetCurrentProcessId()) return E_ACCESSDENIED;
        hr = session.volume->SetMute(TRUE, nullptr);
        if (FAILED(hr)) return hr;
        sessions.push_back(session); // retain controls through stream close
    }
    return CheckMute(sessions);
}

class WaveStream {
public:
    HWAVEOUT handle = nullptr;
    WAVEHDR header{};
    bool prepared = false;
    ~WaveStream() {
        if (handle) {
            waveOutReset(handle);
            if (prepared) waveOutUnprepareHeader(handle, &header, sizeof(header));
            waveOutClose(handle);
        }
    }
    WaveStream() = default;
    WaveStream(const WaveStream&) = delete;
    WaveStream& operator=(const WaveStream&) = delete;
};

static int Test(std::vector<EndpointSession>& sessions) {
    HRESULT hr = MuteOwnEmptySessions(sessions);
    if (FAILED(hr)) {
        std::printf("{\"passed\":false,\"stage\":\"pre_play_mute\",\"hresult\":\"0x%08lx\",\"original_executed\":false}\n",
                    static_cast<unsigned long>(hr));
        return 2;
    }
    std::array<short, 8820> zeros{}; // exactly 100 ms, 44.1 kHz stereo 16-bit PCM
    WaveStream wave; // reset/close before zero buffer and retained controls die
    WAVEFORMATEX format{};
    format.wFormatTag = WAVE_FORMAT_PCM;
    format.nChannels = 2;
    format.nSamplesPerSec = 44100;
    format.wBitsPerSample = 16;
    format.nBlockAlign = 4;
    format.nAvgBytesPerSec = 176400;
    MMRESULT mm = waveOutOpen(&wave.handle, WAVE_MAPPER, &format, 0, 0, CALLBACK_NULL);
    if (mm != MMSYSERR_NOERROR) {
        std::printf("{\"passed\":false,\"stage\":\"wave_open\",\"mmresult\":%u}\n", mm);
        return 3;
    }
    mm = waveOutSetVolume(wave.handle, 0xFFFFFFFF); // own legacy stream/session
    if (mm != MMSYSERR_NOERROR || FAILED(CheckMute(sessions))) return 4;
    wave.header.lpData = reinterpret_cast<LPSTR>(zeros.data());
    wave.header.dwBufferLength = static_cast<DWORD>(zeros.size() * sizeof(short));
    mm = waveOutPrepareHeader(wave.handle, &wave.header, sizeof(wave.header));
    if (mm != MMSYSERR_NOERROR) return 5;
    wave.prepared = true;
    if (FAILED(CheckMute(sessions))) return 6; // last barrier before first sample
    mm = waveOutWrite(wave.handle, &wave.header, sizeof(wave.header));
    if (mm != MMSYSERR_NOERROR) return 7;
    for (unsigned i = 0; i < 100; ++i) {
        if (FAILED(CheckMute(sessions))) return 8;
        if ((static_cast<volatile WAVEHDR*>(&wave.header)->dwFlags & WHDR_DONE) != 0) {
            std::printf("{\"passed\":true,\"pid\":%lu,\"render_endpoints_muted\":%zu,"
                        "\"mute_before_open\":true,\"mute_before_write\":true,"
                        "\"mute_during_zero_pcm\":true,\"legacy_full_volume_still_muted\":true,"
                        "\"original_executed\":false,\"original_launch_authorized\":false}\n",
                        GetCurrentProcessId(), sessions.size());
            return 0;
        }
        Sleep(10);
    }
    return 9; // bounded one second; RAII resets/closes any unfinished zero stream
}

int main() {
    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    if (FAILED(hr)) return 1;
    int result;
    {
        std::vector<EndpointSession> sessions;
        result = Test(sessions);
    }
    CoUninitialize();
    return result;
}

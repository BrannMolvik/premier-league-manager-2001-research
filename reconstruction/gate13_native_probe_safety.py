"""Offline native-probe prerequisite checks; never an original-launch permit.

dgVoodoo can skip malformed config and fall back to defaults. FullScreenMode
alone is insufficient while DirectX application-controlled mode is enabled.
Require every desktop-critical value explicitly; missing is not safe/default.
Actual non-exclusive behavior needs separate runtime qualification. Daniel
manages audio through Volume Mixer; it is not a technical prerequisite.
This module never launches, loads DLLs, or mutes audio.
"""
from __future__ import annotations

import configparser
from hashlib import sha256
from pathlib import Path

from gate13_button_source_trace import require_private_output_path

WRAPPER_SHA256 = '612a24408a090a3c6f3886557fa18034ee742e94ad0a40ebdf854d2816176c2e'
REQUIRED_SETTINGS = {
    ('General', 'OutputAPI'): 'd3d11_fl11_0',
    ('General', 'FullScreenMode'): 'false',
    ('General', 'CaptureMouse'): 'false',
    ('General', 'CenterAppWindow'): 'false',
    ('General', 'DisableScreenSaver'): 'false',
    ('GeneralExt', 'DesktopResolution'): '',
    ('GeneralExt', 'DesktopBitDepth'): '',
    ('GeneralExt', 'WindowedAttributes'): '',
    ('GeneralExt', 'FullscreenAttributes'): '',
    ('GeneralExt', 'FreeMouse'): 'true',
    ('GeneralExt', 'SystemHookFlags'): '',
    ('DirectX', 'DisableAndPassThru'): 'false',
    ('DirectX', 'AppControlledScreenMode'): 'false',
    ('DirectX', 'DisableAltEnterToToggleScreenMode'): 'true',
    ('DirectX', 'Resolution'): 'unforced',
}


class ProbeSafetyError(ValueError):
    pass


def check_windowed_config(text: str) -> dict:
    """Strict offline check, not the vendor parser nor proof of runtime safety."""
    if type(text) is not str:
        raise ProbeSafetyError('Expected textual private wrapper configuration')
    parser = configparser.ConfigParser(interpolation=None, strict=True)
    try:
        # Vendor Version precedes sections; do NOT turn it into inherited defaults.
        parser.read_string('[probe_metadata]\n' + text)
        if parser.defaults() or parser.get('probe_metadata', 'Version', fallback=None) != '0x287':
            raise ProbeSafetyError('Explicit supported Version 0x287 required; no DEFAULT inheritance')
        checked = {}
        for (section, name), expected in REQUIRED_SETTINGS.items():
            if not parser.has_option(section, name):
                raise ProbeSafetyError(f'Missing explicit safety setting: {section}.{name}')
            actual = parser.get(section, name).strip().lower()
            if actual != expected:
                raise ProbeSafetyError(f'Unsafe/unqualified setting: {section}.{name}')
            checked[f'{section}.{name}'] = actual
    except configparser.Error as exc:
        raise ProbeSafetyError('Malformed/duplicate configuration must not fall back to wrapper defaults') from exc
    return dict(offline_configuration_passed=True, checked_settings=checked,
                vendor_parser_qualified=False, runtime_nonexclusive_qualified=False,
                audio_condition='user_managed_volume_mixer', original_launch_authorized=False)


def check_private_stage(stage: Path) -> dict:
    stage = stage.resolve()
    wrapper, config = stage / 'DDraw.dll', stage / 'dgVoodoo.conf'
    require_private_output_path(wrapper)
    require_private_output_path(config)
    actual = sha256(wrapper.read_bytes()).hexdigest()
    if actual != WRAPPER_SHA256:
        raise ProbeSafetyError('Wrapper differs from the recorded private dgVoodoo 2.87.5 identity')
    data = config.read_bytes()
    report = check_windowed_config(data.decode('utf-8-sig'))
    return dict(report, wrapper_sha256=actual, config_sha256=sha256(data).hexdigest())

"""Offline checks must never confer original-launch authorization."""
import unittest

from gate13_native_probe_safety import ProbeSafetyError, REQUIRED_SETTINGS, check_windowed_config


def safe_text():
    lines = ['Version = 0x287']
    for section in ('General', 'GeneralExt', 'DirectX'):
        lines.append(f'[{section}]')
        lines.extend(f'{name} = {value}' for (owner, name), value in REQUIRED_SETTINGS.items() if owner == section)
    return '\n'.join(lines)


class NativeProbeSafetyTests(unittest.TestCase):
    def test_explicit_config_is_offline_only_not_a_launch_permit(self):
        result = check_windowed_config(safe_text())
        self.assertTrue(result['offline_configuration_passed'])
        for key in ('vendor_parser_qualified', 'runtime_nonexclusive_qualified',
                    'pre_play_process_local_silence_qualified', 'original_launch_authorized'):
            self.assertFalse(result[key])

    def test_every_required_value_must_be_explicit(self):
        for (_, name), value in REQUIRED_SETTINGS.items():
            with self.subTest(name=name), self.assertRaises(ProbeSafetyError):
                check_windowed_config(safe_text().replace(f'{name} = {value}', ''))

    def test_false_fullscreen_does_not_override_application_control(self):
        with self.assertRaisesRegex(ProbeSafetyError, 'AppControlledScreenMode'):
            check_windowed_config(safe_text().replace('AppControlledScreenMode = false', 'AppControlledScreenMode = true'))

    def test_passthrough_and_alt_enter_cannot_reenable_unsafe_execution(self):
        for name, value in (('DisableAndPassThru', 'true'), ('DisableAltEnterToToggleScreenMode', 'false')):
            with self.subTest(name=name), self.assertRaises(ProbeSafetyError):
                check_windowed_config(safe_text().replace(f'{name} = {REQUIRED_SETTINGS[("DirectX", name)]}', f'{name} = {value}'))

    def test_forced_desktop_or_topmost_or_capture_is_rejected(self):
        for section, name, value in (('GeneralExt','DesktopResolution','800x600'),
                                    ('GeneralExt','WindowedAttributes','alwaysontop'),
                                    ('GeneralExt','FullscreenAttributes','fake'),
                                    ('General','CaptureMouse','true')):
            with self.subTest(name=name), self.assertRaises(ProbeSafetyError):
                check_windowed_config(safe_text().replace(f'{name} = {REQUIRED_SETTINGS[(section,name)]}', f'{name} = {value}'))

    def test_malformed_duplicate_unknown_version_or_inheritance_rejected(self):
        for text in (safe_text()+'\nResolution = unforced', safe_text().replace('[DirectX]', '[DirectX'),
                     safe_text().replace('0x287', '0x286'), safe_text()+'\n[DEFAULT]\nunused=true'):
            with self.subTest(text=text[-40:]), self.assertRaises(ProbeSafetyError):
                check_windowed_config(text)


if __name__ == '__main__':
    unittest.main()

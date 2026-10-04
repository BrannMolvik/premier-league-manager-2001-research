"""Pure adjudication of private installed-provider DXGI observations.

No launch, security-policy changes, API adaptation or native gameplay evidence.
The installed Microsoft-Windows-DXGI manifest defines event 10/12 Windowed and
event 182 bFullscreen. A pointer from GetFullscreenState is NEVER a Boolean.
"""
from __future__ import annotations

from copy import deepcopy

DXGI_PROVIDER = 'Microsoft-Windows-DXGI'
MODE = 'dxgi_windowed_borderless_v1'


def windowed_dxgi_proof(report: dict, rows: list[dict], events_lost: int) -> dict:
    if type(events_lost) is not int or events_lost != 0:
        raise ValueError('Loss-free DXGI trace required')
    pid = report.get('process_id')
    handles = {r['returned_hwnd'] for r in report.get('native_window_creation_returns', [])}
    visible = report.get('display_observation', {}).get('visible_window_observations', {})
    stable = {hwnd for hwnd in handles if visible.get(str(hwnd), {}).get('samples', 0) >= 3
              and visible[str(hwnd)].get('duration_seconds', 0) >= 1}
    if type(pid) is not int or not stable or not rows:
        raise ValueError('Actual native HWND and stable visible observation required')
    matches = []
    for row in rows:
        if row.get('process_id') != pid or row.get('provider') != DXGI_PROVIDER:
            raise ValueError('DXGI evidence must be filtered to exact original PID/provider')
        fields = row.get('fields', {})
        if row.get('id') in (10, 12):
            if fields.get('Windowed') != 'true':
                raise ValueError('Missing/non-windowed swap-chain state')
            hwnd = int(fields['OutputWindow'], 0)
            if hwnd in stable and int(fields['Width']) > 1 and int(fields['Height']) > 1:
                matches.append(dict(hwnd=hwnd, width=int(fields['Width']), height=int(fields['Height']),
                                    swap_chain=fields['pIDXGISwapChain']))
        if row.get('id') == 182:
            if fields.get('bFullscreen') not in ('0', '0x0'):
                raise ValueError('Exclusive-fullscreen request or unknown value')
    if not matches:
        raise ValueError('No real windowed swap chain for the stable native HWND')
    return dict(mode=MODE, process_id=pid, events_lost=events_lost, matching_swap_chains=matches,
                relevant_event_count=len(rows), all_swap_chain_creations_windowed=True,
                no_exclusive_fullscreen_request=True)


def qualify_borderless(report: dict, rows: list[dict], events_lost: int) -> dict:
    """Complete a bounded captionless qualification with authoritative DXGI data."""
    if (report.get('schema_version') != 4 or report.get('stop_reason') != 'time_bound'
            or report.get('elapsed_seconds', 0) < 1
            or report.get('display_qualification_only') is not True
            or report.get('activation_trace_only') is True
            or report.get('presentation_shim_verified') is not True
            or report.get('private_wrapper_load_observed') is not True
            or report.get('native_graphics_initialization_accepted') is not True):
        raise ValueError('Complete bounded graphics/display observations required')
    problems = report.get('display_observation', {}).get('problems')
    allowed = {'probe_took_foreground', 'probe_took_focus'} if report.get(
        'approved_activation_windowed_qualification') is True else set()
    if not isinstance(problems, list) or not set(problems).issubset(allowed):
        raise ValueError('Non-activation desktop safety failure')
    result = deepcopy(report)
    result['dxgi_windowed_proof'] = windowed_dxgi_proof(report, rows, events_lost)
    result['qualification_mode'] = MODE
    result['native_debugger_stop_reason'] = result['stop_reason']
    result['stop_reason'] = 'display_qualification_complete'
    result['runtime_nonexclusive_qualified'] = True
    return result

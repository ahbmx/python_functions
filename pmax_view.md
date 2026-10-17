```python
#!/usr/bin/env python3
"""
powermax_layout.py - build an Excel workbook with a visual engine / director /
port layout of the LOCAL Dell PowerMax 2500 / 8000 arrays of a Unisphere
instance, using PyU4V for data collection and xlsxwriter for the workbook.

Sheets produced
  Summary               one row per array + one row per engine (COUNTIFS formulas)
  <model>_<sn> Layout   one visual sheet per array: engines -> directors -> ports
  Port Inventory        flat, filterable table of every port (feeds the formulas)

Authentication (environment variables)
  U4V_SERVER_IP    Unisphere host name / IP             (required)
  U4V_USERNAME     Unisphere user                       (required)
  U4V_PASSWORD     Unisphere password                   (required)
  U4V_PORT         Unisphere port                       (default 8443)
  U4V_VERIFY_SSL   true | false | /path/to/ca-bundle    (default true)

Only arrays that Unisphere reports as local are ever queried; remote arrays
(e.g. SRDF partners it merely knows about) are skipped.

Examples
  export U4V_SERVER_IP=unisphere.corp.local U4V_USERNAME=svc_report
  export U4V_PASSWORD='...'            # or read it from your secret store
  python powermax_layout.py
  python powermax_layout.py --array 000197600123 -o layout.xlsx
  python powermax_layout.py --demo     # synthetic data, no Unisphere needed

Requires: pip install PyU4V xlsxwriter
"""
import argparse
import json
import math
import os
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import xlsxwriter
from xlsxwriter.utility import xl_col_to_name

FONT = "Arial"

# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------


@dataclass
class Port:
    director_id: str            # e.g. FA-1D  or  OR-1C
    port_id: str                # e.g. 4
    protocol: str = "Other"     # FC / NVMe/FC / NVMe/TCP / iSCSI / SRDF FC ...
    state: str = "Unknown"      # Online / Offline / Unknown
    port_status: str = ""
    director_status: str = ""
    speed: str = ""
    max_speed: str = ""
    identifier: str = ""
    port_groups: Optional[int] = None
    masking_views: Optional[int] = None
    raw: dict = field(default_factory=dict)

    @property
    def full_id(self):
        return f"{self.director_id}:{self.port_id}"


@dataclass
class DirGroup:
    """One director ID (emulation instance), e.g. FA-1D, with its ports."""
    director_id: str
    emulation: str
    number: int
    ports: List[Port] = field(default_factory=list)
    raw: dict = field(default_factory=dict)


@dataclass
class ArrayData:
    sid: str
    model: str
    ucode: str = ""
    groups: List[DirGroup] = field(default_factory=list)
    demo: bool = False

    @property
    def model_short(self):
        m = re.search(r"(\d{4})", self.model)
        return m.group(1) if m else self.model.replace(" ", "")

    def all_ports(self):
        for g in self.groups:
            for p in g.ports:
                yield g, p


DIR_RE = re.compile(r"^([A-Za-z]{2})-(\d+)([A-Za-z]?)$")


def engine_of(director_number: int) -> int:
    """Engine N holds directors 2N-1 and 2N (same scheme on 8000 and 2500)."""
    return (director_number + 1) // 2


# --------------------------------------------------------------------------
# Normalisation helpers
# --------------------------------------------------------------------------

EMU_PROTOCOL = {"FA": "FC", "SE": "iSCSI", "EF": "FICON",
                "RF": "SRDF FC", "RE": "SRDF GigE"}
V4_PROTOCOL = {"SCSI_FC": "FC", "NVMe_FC": "NVMe/FC", "NVMe_TCP": "NVMe/TCP",
               "RDF_FC": "SRDF FC", "iSCSI": "iSCSI", "RDF_GigE": "SRDF GigE"}
PROTOCOLS = ["FC", "NVMe/FC", "NVMe/TCP", "iSCSI", "FICON",
             "SRDF FC", "SRDF GigE", "Other"]


def first(d: dict, *keys, default=""):
    for k in keys:
        if d and d.get(k) not in (None, ""):
            return d[k]
    return default


def norm_state(port_status, dir_status) -> str:
    p = str(port_status or "").strip().lower()
    d = str(dir_status or "").strip().lower()
    off = {"off", "offline", "down", "disabled"}
    on = {"on", "online", "up", "enabled"}
    if p in off or d in off:
        return "Offline"
    if p in on and (d in on or d == ""):
        return "Online"
    return "Unknown"


def fmt_speed(v) -> str:
    s = str(v).strip() if v not in (None, "") else ""
    return f"{s}G" if re.fullmatch(r"\d+(\.\d+)?", s) else s


def to_int(v):
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def port_sort_key(p: Port):
    n = to_int(p.port_id)
    return (0, n, "") if n is not None else (1, 0, str(p.port_id))


EMU_ORDER = ["FA", "SE", "EF", "OR", "RF", "RE"]


def group_sort_key(g: DirGroup):
    i = EMU_ORDER.index(g.emulation) if g.emulation in EMU_ORDER else 99
    return (g.number, i, g.director_id)


# --------------------------------------------------------------------------
# Live collection through PyU4V
# --------------------------------------------------------------------------


def u4v_settings() -> dict:
    """Read the Unisphere connection settings from the environment."""
    server = os.getenv("U4V_SERVER_IP")
    user = os.getenv("U4V_USERNAME")
    password = os.getenv("U4V_PASSWORD")
    missing = [n for n, v in (("U4V_SERVER_IP", server), ("U4V_USERNAME", user),
                              ("U4V_PASSWORD", password)) if not v]
    if missing:
        sys.exit("Missing environment variable(s): " + ", ".join(missing))

    verify_raw = os.getenv("U4V_VERIFY_SSL", "true").strip()
    if verify_raw.lower() in ("", "true", "1", "yes"):
        verify = True
    elif verify_raw.lower() in ("false", "0", "no"):
        verify = False
    else:
        verify = verify_raw                      # path to a CA bundle
    return {"server_ip": server, "username": user, "password": password,
            "port": int(os.getenv("U4V_PORT", "8443")), "verify": verify}


def connect(settings: dict, array_id=None):
    from PyU4V import U4VConn
    kw = dict(settings)
    if array_id:
        kw["array_id"] = array_id
    return U4VConn(**kw)


def collect_live_array(conn, sid, info, fetch_detail, warnings) -> ArrayData:
    model = str(info.get("model", "PowerMax")).replace("_", " ")
    arr = ArrayData(sid=sid, model=model,
                    ucode=str(info.get("ucode") or info.get("microcode") or ""))
    system = conn.system

    directors = system.get_director_list() or []
    print(f"  {sid} ({model}): {len(directors)} director IDs")
    for did in sorted(directors):
        m = DIR_RE.match(did)
        if not m:
            warnings.append(f"{sid}: skipped director ID with unexpected name '{did}'")
            continue
        emu, num = m.group(1).upper(), int(m.group(2))
        grp = DirGroup(director_id=did, emulation=emu, number=num)
        try:
            grp.raw = system.get_director(did) or {}
        except Exception as e:  # noqa: BLE001
            warnings.append(f"{sid}: get_director({did}) failed: {e}")
        dir_status = first(grp.raw, "director_status", "availability", "status")

        port_keys = []
        try:
            port_keys = system.get_director_port_list(did) or []
        except Exception as e:  # noqa: BLE001
            warnings.append(f"{sid}: port list for {did} failed: {e}")

        # PowerMax 2500/8500 ("OR-" directors): one director carries several
        # protocols; ask the API per protocol so each port can be labelled.
        proto_by_port = {}
        if emu == "OR":
            for api_name, label in V4_PROTOCOL.items():
                try:
                    for k in system.get_director_port_list(
                            did, filters={"enabled_protocol": api_name}) or []:
                        proto_by_port[str(k.get("portId"))] = label
                except Exception:  # noqa: BLE001
                    pass

        for k in port_keys:
            pid = str(k.get("portId"))
            detail = {}
            if fetch_detail:
                try:
                    detail = (system.get_director_port(did, pid) or {}
                              ).get("symmetrixPort", {}) or {}
                except Exception as e:  # noqa: BLE001
                    warnings.append(f"{sid}: get_director_port({did}:{pid}) failed: {e}")
            proto = proto_by_port.get(pid) or EMU_PROTOCOL.get(emu)
            if not proto:
                proto = V4_PROTOCOL.get(str(first(detail, "enabled_protocol")), "Other")
            dstat = first(detail, "director_status", default=dir_status)
            pstat = first(detail, "port_status")
            grp.ports.append(Port(
                director_id=did, port_id=pid, protocol=proto,
                state=norm_state(pstat, dstat),
                port_status=str(pstat), director_status=str(dstat),
                speed=fmt_speed(first(detail, "negotiated_speed")),
                max_speed=fmt_speed(first(detail, "max_speed")),
                identifier=str(first(detail, "identifier")),
                port_groups=to_int(first(detail, "num_of_port_groups", default=None)),
                masking_views=to_int(first(detail, "num_of_masking_views", default=None)),
                raw=detail))
        grp.ports.sort(key=port_sort_key)
        arr.groups.append(grp)
    arr.groups.sort(key=group_sort_key)
    return arr


def collect_live(args):
    warnings: List[str] = []
    settings = u4v_settings()
    conn0 = connect(settings)
    sids = args.array or conn0.common.get_array_list() or []
    wanted = [m.strip() for m in args.models.split(",") if m.strip()]
    arrays = []
    for sid in sids:
        info = conn0.common.get_array(sid) or {}
        model = str(info.get("model", ""))
        # LOCAL arrays only - never query arrays Unisphere merely knows about.
        if not info.get("local", False):
            print(f"  {sid}: not a local array, skipped")
            continue
        if wanted and not any(w in model for w in wanted):
            print(f"  {sid}: model '{model}' not in --models ({args.models}), skipped")
            continue
        conn = connect(settings, array_id=sid)
        arrays.append(collect_live_array(conn, sid, info,
                                         not args.no_port_detail, warnings))
    return arrays, warnings


# --------------------------------------------------------------------------
# Demo data (synthetic - only to preview the layout)
# --------------------------------------------------------------------------


def demo_arrays() -> List[ArrayData]:
    def mk(arr, did, ports, proto, speed):
        m = DIR_RE.match(did)
        g = DirGroup(did, m.group(1), int(m.group(2)))
        for i, pn in enumerate(ports):
            n = g.number
            state = "Online"
            if (n * 7 + i) % 23 == 0:
                state = "Offline"
            if (n * 5 + i) % 31 == 0:
                state = "Unknown"
            st = {"Online": "ON", "Offline": "OFF", "Unknown": ""}[state]
            host = proto in ("FC", "NVMe/FC", "NVMe/TCP", "iSCSI")
            g.ports.append(Port(
                did, str(pn), proto, state, st,
                "Online" if state != "Offline" else "Offline", speed,
                speed, f"5000097{n:02d}{i:02d}0{arr.sid[-4:]}" if proto != "iSCSI"
                else f"iqn.1992-04.com.emc:600009700{arr.sid[-4:]}{n}{i}",
                (i % 3) if host else None, (i * 2 % 5) if host else None))
        arr.groups.append(g)

    a = ArrayData("000197600123", "PowerMax 8000", "5978.711.711", demo=True)
    for d in range(1, 9):                      # 4 engines
        mk(a, f"FA-{d}D", range(4, 12), "FC", "16G")
        mk(a, f"SE-{d}E", range(0, 2), "iSCSI", "10G")
        if d <= 2:
            mk(a, f"RF-{d}F", range(0, 2), "SRDF FC", "16G")
    b = ArrayData("000120200456", "PowerMax 2500", "6079.175.0", demo=True)
    for d in range(1, 5):                      # 2 engines
        mk(b, f"OR-{d}C", range(0, 4), "FC", "32G")
        mk(b, f"OR-{d}C", range(4, 6), "NVMe/TCP", "25G")
        mk(b, f"OR-{d}C", range(6, 8), "SRDF FC", "32G")
    for arr in (a, b):
        merged: Dict[str, DirGroup] = {}       # OR-x repeats above: merge per ID
        for g in arr.groups:
            if g.director_id in merged:
                merged[g.director_id].ports += g.ports
            else:
                merged[g.director_id] = g
        arr.groups = sorted(merged.values(), key=group_sort_key)
        for g in arr.groups:
            g.ports.sort(key=port_sort_key)
    return [a, b]


# --------------------------------------------------------------------------
# Excel (xlsxwriter) helpers
# --------------------------------------------------------------------------

EMU_COLOR = {"FA": "#1F4E79", "SE": "#0E7C7B", "EF": "#6B3FA0", "OR": "#2F5597",
             "RF": "#C55A11", "RE": "#9C6500"}
STATE_STYLE = {  # fill, font colour
    "Online": ("#C6EFCE", "#006100"),
    "Offline": ("#FFC7CE", "#9C0006"),
    "Unknown": ("#E7E6E6", "#595959"),
}
NAVY = "#1B2A41"
SLATE = "#44546A"
CHASSIS = "#F2F2F2"
PORT_ROW_H = 64
HDR_ROW_H = 18


class Formats:
    """Cached xlsxwriter format factory (Arial throughout)."""

    def __init__(self, wb):
        self.wb = wb
        self.cache = {}

    def __call__(self, **kw):
        props = {"font_name": FONT, "font_size": 9, "valign": "vcenter"}
        props.update(kw)
        key = tuple(sorted(props.items()))
        if key not in self.cache:
            self.cache[key] = self.wb.add_format(props)
        return self.cache[key]


BORDER = {"border": 1, "border_color": "#A6A6A6"}


def banner(ws, F, row, c1, c2, text, bg, color="#FFFFFF", size=10, bold=True,
           align="left", height=None):
    f = F(bg_color=bg, font_color=color, font_size=size, bold=bold, align=align,
          indent=1 if align == "left" else 0)
    if c2 > c1:
        ws.merge_range(row, c1, row, c2, text, f)
    else:
        ws.write(row, c1, text, f)
    if height:
        ws.set_row(row, height)
    return f


def unique_sheet_name(base, used):
    name, n = base[:31], 2
    while name in used:
        suffix = f" {n}"
        name, n = base[:31 - len(suffix)] + suffix, n + 1
    used.add(name)
    return name


# --------------------------------------------------------------------------
# Layout sheet
# --------------------------------------------------------------------------


def draw_director(ws, F, groups, col0, row0, ppr, heights) -> int:
    """Draw the emulation groups of one director; returns rows used."""
    r = row0
    if not groups:
        banner(ws, F, r, col0, col0 + ppr - 1, "no external ports on this director",
               "#D9D9D9", "#595959", 8, False, "center")
        heights[r] = max(heights.get(r, 0), HDR_ROW_H)
        return 1
    for g in groups:
        banner(ws, F, r, col0, col0 + ppr - 1,
               f"{g.director_id}   ({len(g.ports)} ports)",
               EMU_COLOR.get(g.emulation, "#595959"), size=9)
        heights[r] = max(heights.get(r, 0), HDR_ROW_H)
        r += 1
        for i, p in enumerate(g.ports):
            rr, cc = r + i // ppr, col0 + i % ppr
            bg, fg = STATE_STYLE[p.state]
            spd = " ".join(x for x in (p.speed, p.protocol) if x)
            lines = [p.full_id, spd, p.state]
            if p.port_groups is not None or p.masking_views is not None:
                pg = p.port_groups if p.port_groups is not None else "-"
                mv = p.masking_views if p.masking_views is not None else "-"
                lines.append(f"PG {pg} | MV {mv}")
            ws.write(rr, cc, "\n".join(lines),
                     F(bg_color=bg, font_color=fg, font_size=8, align="center",
                       text_wrap=True, **BORDER))
            tip = [p.full_id, f"Protocol: {p.protocol}", f"State: {p.state}",
                   f"Port status: {p.port_status or 'n/a'}  /  "
                   f"Director status: {p.director_status or 'n/a'}",
                   f"Speed: {p.speed or 'n/a'} (max {p.max_speed or 'n/a'})",
                   f"WWPN/IQN: {p.identifier or 'n/a'}",
                   f"Port groups: {p.port_groups if p.port_groups is not None else 'n/a'}",
                   f"Masking views: {p.masking_views if p.masking_views is not None else 'n/a'}"]
            ws.write_comment(rr, cc, "\n".join(tip),
                             {"x_scale": 2.2, "y_scale": 2.2, "author": "powermax_layout"})
            heights[rr] = max(heights.get(rr, 0), PORT_ROW_H)
        r += math.ceil(len(g.ports) / ppr)
    return r - row0


def build_layout_sheet(ws, F, arr: ArrayData, ppr: int, inv_ref, counts):
    ws.hide_gridlines(2)
    ws.set_zoom(90)
    L0 = 1
    R0 = L0 + ppr + 1
    LAST = R0 + ppr - 1
    ws.set_column(0, 0, 2)
    ws.set_column(L0, LAST, 15)
    ws.set_column(L0 + ppr, L0 + ppr, 3)

    title = f"{arr.model}  -  Array {arr.sid}"
    if arr.ucode:
        title += f"  -  microcode {arr.ucode}"
    if arr.demo:
        title += "  [DEMO DATA]"
    banner(ws, F, 0, L0, LAST, title, NAVY, size=14, height=30)

    sn = f'"{arr.sid}"'
    A, J = inv_ref("A"), inv_ref("J")
    formula = (f'="Ports: "&COUNTIFS({A},{sn})'
               f'&"   Online: "&COUNTIFS({A},{sn},{J},"Online")'
               f'&"   Offline: "&COUNTIFS({A},{sn},{J},"Offline")'
               f'&"   Unknown: "&COUNTIFS({A},{sn},{J},"Unknown")')
    cached = (f"Ports: {counts(sid=arr.sid)}   Online: {counts(sid=arr.sid, state='Online')}"
              f"   Offline: {counts(sid=arr.sid, state='Offline')}"
              f"   Unknown: {counts(sid=arr.sid, state='Unknown')}")
    f_sub = banner(ws, F, 1, L0, LAST, "", "#D6DCE4", NAVY, 10, True, height=20)
    ws.write_formula(1, L0, formula, f_sub, cached)

    ws.write(2, L0, "Legend:", F(bold=True))
    for i, st in enumerate(("Online", "Offline", "Unknown")):
        bg, fg = STATE_STYLE[st]
        ws.write(2, L0 + 1 + i, st, F(bg_color=bg, font_color=fg, bold=True,
                                      align="center", **BORDER))
    ws.write(2, L0 + 4, "PG = port groups, MV = masking views (host-facing ports). "
             "Hover a port for WWPN/IQN and details.", F(font_size=8, italic=True))
    ws.write(3, L0, "Engine N = directors 2N-1 and 2N. Layout is logical "
             "(director / port ID), not a photo of the physical I/O slots.",
             F(font_size=8, italic=True))

    by_dir: Dict[int, List[DirGroup]] = defaultdict(list)
    for g in arr.groups:
        by_dir[g.number].append(g)
    engines = sorted({engine_of(n) for n in by_dir})

    row = 5
    heights: Dict[int, float] = {}
    for e in engines:
        dl, dr = 2 * e - 1, 2 * e
        gl = sorted([g for g in by_dir.get(dl, []) if g.ports], key=group_sort_key)
        gr = sorted([g for g in by_dir.get(dr, []) if g.ports], key=group_sort_key)

        banner(ws, F, row, L0, LAST, f"ENGINE {e}   -   directors {dl} & {dr}",
               NAVY, size=11, height=22)
        row += 1
        for col0, dn, gg in ((L0, dl, gl), (R0, dr, gr)):
            n_ports = sum(len(g.ports) for g in gg)
            present = dn in by_dir
            banner(ws, F, row, col0, col0 + ppr - 1,
                   f"DIRECTOR {dn}" + (f"   -   {n_ports} ports" if present
                                       else "   -   not present"),
                   SLATE if present else "#A6A6A6", size=10, height=20)
        row += 1

        need = max(sum(1 + math.ceil(len(g.ports) / ppr) for g in gg) or 1
                   for gg in (gl, gr))
        chassis = F(bg_color=CHASSIS)
        for rr in range(row, row + need):            # chassis background
            for cc in list(range(L0, L0 + ppr)) + list(range(R0, R0 + ppr)):
                ws.write_blank(rr, cc, None, chassis)
        draw_director(ws, F, gl, L0, row, ppr, heights)
        draw_director(ws, F, gr, R0, row, ppr, heights)
        row += need + 1                                # blank spacer row

    for r, h in heights.items():
        ws.set_row(r, h)
    ws.freeze_panes(4, 0)
    ws.set_landscape()
    ws.fit_to_pages(1, 0)


# --------------------------------------------------------------------------
# Inventory + summary sheets
# --------------------------------------------------------------------------

INV_HEADERS = ["Array SN", "Model", "Engine", "Director #", "Director ID",
               "Emulation", "Port", "Port ID", "Protocol", "State",
               "Port Status (raw)", "Director Status (raw)", "Negotiated Speed",
               "Max Speed", "WWPN / IQN", "Port Groups", "Masking Views"]
INV_WIDTHS = [15, 16, 8, 10, 12, 10, 7, 12, 12, 10, 14, 16, 14, 10, 38, 11, 13]


def build_inventory(ws, F, arrays):
    hdr = F(bg_color=NAVY, font_color="#FFFFFF", font_size=10, bold=True,
            align="center", text_wrap=True, **BORDER)
    for c, h in enumerate(INV_HEADERS):
        ws.write(0, c, h, hdr)
    r = 1
    for arr in arrays:
        for g, p in arr.all_ports():
            vals = [arr.sid, arr.model, engine_of(g.number), g.number,
                    g.director_id, g.emulation, p.port_id, p.full_id,
                    p.protocol, p.state, p.port_status, p.director_status,
                    p.speed, p.max_speed, p.identifier,
                    p.port_groups, p.masking_views]
            for c, v in enumerate(vals):
                if c == 9:
                    bg, fg = STATE_STYLE[p.state]
                    ws.write(r, c, v, F(bg_color=bg, font_color=fg, bold=True, **BORDER))
                elif v is None:
                    ws.write_blank(r, c, None, F(**BORDER))
                else:
                    ws.write(r, c, v, F(**BORDER))
            r += 1
    for i, w in enumerate(INV_WIDTHS):
        ws.set_column(i, i, w)
    ws.set_row(0, 30)
    ws.freeze_panes(1, 0)
    ws.autofilter(0, 0, max(r - 1, 1), len(INV_HEADERS) - 1)


def build_summary(ws, F, arrays, inv_ref, counts, warnings):
    ws.hide_gridlines(2)
    A, C, I, J = inv_ref("A"), inv_ref("C"), inv_ref("I"), inv_ref("J")
    ncols = 9 + len(PROTOCOLS)

    banner(ws, F, 0, 0, ncols - 1, "PowerMax port / engine summary", NAVY,
           size=14, height=30)
    note = ("All counts are formulas over the 'Port Inventory' sheet. "
            "Engine N = directors 2N-1 and 2N.")
    if any(a.demo for a in arrays):
        note += "   DEMO DATA - NOT REAL ARRAYS."
    ws.write(1, 0, note, F(italic=True))

    head = F(bg_color=SLATE, font_color="#FFFFFF", font_size=10, bold=True,
             align="center", text_wrap=True, **BORDER)
    cell_l = F(font_size=10, **BORDER)
    cell_c = F(font_size=10, align="center", **BORDER)
    cell_pct = F(font_size=10, align="center", num_format="0.0%", **BORDER)
    tot_c = F(font_size=10, bold=True, align="center", **BORDER)
    tot_pct = F(font_size=10, bold=True, align="center", num_format="0.0%", **BORDER)

    heads = (["Array SN", "Model", "Microcode", "Engines", "Total ports",
              "Online", "Offline", "Unknown", "% Online"] + PROTOCOLS)
    hr = 3
    for c, h in enumerate(heads):
        ws.write(hr, c, h, head)
    ws.set_row(hr, 30)

    first_r = hr + 1
    r = first_r
    for arr in arrays:
        x = r + 1                                    # Excel (1-based) row number
        sn = f"$A{x}"
        n_eng = max((engine_of(g.number) for g, _ in arr.all_ports()), default=0)
        tot = counts(sid=arr.sid)
        onl = counts(sid=arr.sid, state="Online")
        ws.write(r, 0, arr.sid, cell_l)
        ws.write(r, 1, arr.model, cell_l)
        ws.write(r, 2, arr.ucode, cell_l)
        ws.write_formula(r, 3, f"=_xlfn.MAXIFS({C},{A},{sn})", cell_c, n_eng)
        ws.write_formula(r, 4, f"=COUNTIFS({A},{sn})", cell_c, tot)
        for c, st in ((5, "Online"), (6, "Offline"), (7, "Unknown")):
            ws.write_formula(r, c, f'=COUNTIFS({A},{sn},{J},"{st}")', cell_c,
                             counts(sid=arr.sid, state=st))
        ws.write_formula(r, 8, f"=IF(E{x}=0,0,F{x}/E{x})", cell_pct,
                         onl / tot if tot else 0)
        for k, p in enumerate(PROTOCOLS):
            ws.write_formula(r, 9 + k, f'=COUNTIFS({A},{sn},{I},"{p}")', cell_c,
                             counts(sid=arr.sid, proto=p))
        r += 1
    last_r = r - 1

    ws.write(r, 0, "Total", F(font_size=10, bold=True, **BORDER))
    for c in range(1, ncols):
        ws.write_blank(r, c, None, F(font_size=10, bold=True, **BORDER))
    sum_cols = [4, 5, 6, 7] + list(range(9, ncols))
    for c in sum_cols:
        L = xl_col_to_name(c)
        cached = sum(counts(sid=a.sid, state=(["Online", "Offline", "Unknown"][c - 5]
                                               if 5 <= c <= 7 else None),
                            proto=(PROTOCOLS[c - 9] if c >= 9 else None))
                     for a in arrays)
        ws.write_formula(r, c, f"=SUM({L}{first_r + 1}:{L}{last_r + 1})",
                         tot_c, cached)
    gt, go = counts(), counts(state="Online")
    ws.write_formula(r, 8, f"=IF(E{r + 1}=0,0,F{r + 1}/E{r + 1})", tot_pct,
                     go / gt if gt else 0)

    # ports per engine
    r += 3
    ws.write(r - 1, 0, "Ports per engine", F(font_size=11, bold=True))
    for c, h in enumerate(["Array SN", "Model", "Engine", "Total ports",
                           "Online", "Offline", "Unknown"]):
        ws.write(r, c, h, head)
    r += 1
    for arr in arrays:
        for e in sorted({engine_of(g.number) for g, _ in arr.all_ports()}):
            x = r + 1
            ws.write(r, 0, arr.sid, cell_l)
            ws.write(r, 1, arr.model, cell_l)
            ws.write_number(r, 2, e, cell_c)
            ws.write_formula(r, 3, f"=COUNTIFS({A},$A{x},{C},$C{x})", cell_c,
                             counts(sid=arr.sid, engine=e))
            for c, st in ((4, "Online"), (5, "Offline"), (6, "Unknown")):
                ws.write_formula(r, c, f'=COUNTIFS({A},$A{x},{C},$C{x},{J},"{st}")',
                                 cell_c, counts(sid=arr.sid, engine=e, state=st))
            r += 1

    if warnings:
        r += 2
        ws.write(r, 0, "Collection warnings", F(font_size=11, bold=True,
                                                font_color="#9C0006"))
        for w in warnings[:200]:
            r += 1
            ws.write(r, 0, w, F(font_color="#9C0006"))

    ws.set_column(0, 1, 16)
    ws.set_column(2, 2, 13)
    ws.set_column(3, ncols - 1, 11)


# --------------------------------------------------------------------------
# Main
# --------------------------------------------------------------------------


def build_workbook(arrays, warnings, ppr, path):
    # python-side counts, written as cached formula results so viewers that do
    # not recalculate (previewers, some mobile apps) still show real numbers
    rows = [(a.sid, engine_of(g.number), p.state, p.protocol)
            for a in arrays for g, p in a.all_ports()]

    def counts(sid=None, engine=None, state=None, proto=None):
        return sum(1 for s, e, st, pr in rows
                   if (sid is None or s == sid) and (engine is None or e == engine)
                   and (state is None or st == state)
                   and (proto is None or pr == proto))

    last = max(len(rows) + 1, 2)

    def inv_ref(col):
        return f"'Port Inventory'!${col}$2:${col}${last}"

    wb = xlsxwriter.Workbook(path)
    wb.set_properties({"title": "PowerMax engine / port layout",
                       "comments": "Generated by powermax_layout.py"})
    F = Formats(wb)
    used = {"Summary", "Port Inventory"}
    ws_sum = wb.add_worksheet("Summary")
    layouts = [(a, wb.add_worksheet(unique_sheet_name(
        f"{a.model_short}_{a.sid[-4:]} Layout", used))) for a in arrays]
    ws_inv = wb.add_worksheet("Port Inventory")

    build_summary(ws_sum, F, arrays, inv_ref, counts, warnings)
    for a, ws in layouts:
        build_layout_sheet(ws, F, a, ppr, inv_ref, counts)
    build_inventory(ws_inv, F, arrays)
    ws_sum.activate()
    wb.close()


def main():
    ap = argparse.ArgumentParser(
        description="Excel layout of local PowerMax engines/directors/ports "
                    "via PyU4V (credentials come from U4V_* environment variables)")
    ap.add_argument("-o", "--output", default="powermax_layout.xlsx")
    ap.add_argument("--array", nargs="*",
                    help="array serial numbers (default: every local array "
                         "matching --models); non-local arrays are always skipped")
    ap.add_argument("--models", default="2500,8000",
                    help="model filter (default 2500,8000)")
    ap.add_argument("--ports-per-row", type=int, default=4,
                    help="ports drawn per row inside a director (default 4)")
    ap.add_argument("--no-port-detail", action="store_true",
                    help="skip per-port detail calls (faster; no status/speed/WWPN)")
    ap.add_argument("--dump-raw", metavar="FILE",
                    help="also save the raw API port/director data as JSON")
    ap.add_argument("--demo", action="store_true",
                    help="use synthetic data instead of contacting Unisphere")
    args = ap.parse_args()

    if args.demo:
        arrays, warnings = demo_arrays(), []
    else:
        try:
            arrays, warnings = collect_live(args)
        except ImportError:
            sys.exit("PyU4V is not installed:  pip install PyU4V")
    if not arrays:
        sys.exit("No local arrays collected - check U4V_* settings, --array, --models.")

    if args.dump_raw:
        dump = {a.sid: {g.director_id: {"director": g.raw,
                                        "ports": {p.port_id: p.raw for p in g.ports}}
                        for g in a.groups} for a in arrays}
        with open(args.dump_raw, "w") as fh:
            json.dump(dump, fh, indent=2, default=str)

    build_workbook(arrays, warnings, max(1, args.ports_per_row), args.output)
    print(f"Wrote {args.output}  ({len(arrays)} array(s), "
          f"{sum(1 for a in arrays for _ in a.all_ports())} ports)")
    for w in warnings[:20]:
        print("  warning:", w)
    if len(warnings) > 20:
        print(f"  ... {len(warnings) - 20} more warnings (see Summary sheet)")


if __name__ == "__main__":
    main()

```

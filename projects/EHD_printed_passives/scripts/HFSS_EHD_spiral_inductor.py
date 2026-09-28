# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------------
# Common helpers (AEDT native scripting: Tools > Run Script..., or
#   ansysedt.exe -ng -RunScriptAndExit <this file>).
# Works with IronPython 2.7 (older AEDT) and CPython (newer AEDT). No numpy.
#
# AnsysSim workspace convention: design (.aedt) -> ../design ,
#   results (.txt/.s2p) -> ../results  (edit DESIGN_DIR / RESULTS_DIR below
#   if you move this script).
# ---------------------------------------------------------------------------
import os, cmath, math

try:
    import ScriptEnv
    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
except Exception:
    pass  # already inside AEDT: oDesktop is provided


def u(v):
    return "%.6gum" % v


def msg(text):
    try:
        oDesktop.AddMessage("", "", 0, text)
    except Exception:
        print(text)


def attrs(name, mat, solve_inside=True, color="(143 175 143)", transp=0.0):
    return ["NAME:Attributes", "Name:=", name, "Flags:=", "", "Color:=", color,
            "Transparency:=", transp, "PartCoordinateSystem:=", "Global", "UDMId:=", "",
            "MaterialValue:=", "\"%s\"" % mat, "SolveInside:=", solve_inside]


def box(ed, name, x0, y0, z0, dx, dy, dz, mat, solve_inside=True, color="(143 175 143)", transp=0.0):
    ed.CreateBox(["NAME:BoxParameters", "XPosition:=", u(x0), "YPosition:=", u(y0), "ZPosition:=", u(z0),
                  "XSize:=", u(dx), "YSize:=", u(dy), "ZSize:=", u(dz)],
                 attrs(name, mat, solve_inside, color, transp))
    return name


def rect_z(ed, name, x0, x1, y0, y1, z):
    """sheet in the XY plane at height z"""
    xa, xb = min(x0, x1), max(x0, x1)
    ya, yb = min(y0, y1), max(y0, y1)
    ed.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
                        "XStart:=", u(xa), "YStart:=", u(ya), "ZStart:=", u(z),
                        "Width:=", u(xb - xa), "Height:=", u(yb - ya), "WhichAxis:=", "Z"],
                       attrs(name, "vacuum", True, "(255 200 0)", 0.0))
    return name


def rect_y_square(ed, name, xc, y, z0, size):
    """square sheet normal to Y (square, so width/height orientation cannot be mixed up)"""
    ed.CreateRectangle(["NAME:RectangleParameters", "IsCovered:=", True,
                        "XStart:=", u(xc - size / 2.0), "YStart:=", u(y), "ZStart:=", u(z0),
                        "Width:=", u(size), "Height:=", u(size), "WhichAxis:=", "Y"],
                       attrs(name, "vacuum", True, "(0 0 255)", 0.5))
    return name


def cyl_z(ed, name, xc, yc, z0, r, h, mat):
    ed.CreateCylinder(["NAME:CylinderParameters", "XCenter:=", u(xc), "YCenter:=", u(yc), "ZCenter:=", u(z0),
                       "Radius:=", u(r), "Height:=", u(h), "WhichAxis:=", "Z", "NumSides:=", "0"],
                      attrs(name, mat, False, "(255 128 64)", 0.0))
    return name


def unite(ed, names):
    if len(names) > 1:
        ed.Unite(["NAME:Selections", "Selections:=", ",".join(names)],
                 ["NAME:UniteParameters", "KeepOriginals:=", False])
    return names[0]


def subtract(ed, blank, tools, keep=False):
    ed.Subtract(["NAME:Selections", "Blank Parts:=", blank, "Tool Parts:=", ",".join(tools)],
                ["NAME:SubtractParameters", "KeepOriginals:=", keep])


def add_dielectric(dm, name, eps, tand):
    if not dm.DoesMaterialExist(name):
        dm.AddMaterial(["NAME:" + name, "CoordinateSystemType:=", "Cartesian",
                        "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
                        "permittivity:=", str(eps), "dielectric_loss_tangent:=", str(tand)])


def add_conductor(dm, name, sigma):
    if not dm.DoesMaterialExist(name):
        dm.AddMaterial(["NAME:" + name, "CoordinateSystemType:=", "Cartesian",
                        "BulkOrSurfaceType:=", 1, ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
                        "conductivity:=", str(sigma)])


def wave_port(bnd, name, sheet, x_sig_edge, x_gnd_edge, y, deembed_um):
    bnd.AssignWavePort(["NAME:" + name, "Objects:=", [sheet], "NumModes:=", 1,
                        "RenormalizeAllTerminals:=", True, "UseLineModeAlignment:=", False,
                        "DoDeembed:=", deembed_um > 0, "DeembedDist:=", u(deembed_um),
                        ["NAME:Modes", ["NAME:Mode1", "ModeNum:=", 1, "UseIntLine:=", True,
                                        ["NAME:IntLine", "Start:=", [u(x_gnd_edge), u(y), "0um"],
                                         "End:=", [u(x_sig_edge), u(y), "0um"]],
                                        "AlignmentGroup:=", 0, "CharImp:=", "Zpi", "RenormImp:=", "50ohm"]],
                        "ShowReporterFilter:=", False, "ReporterFilter:=", [True],
                        "UseAnalyticAlignment:=", False])


def setup_and_run(design, f_adapt_ghz, f_start_ghz, f_stop_ghz, npts):
    an = design.GetModule("AnalysisSetup")
    an.InsertSetup("HfssDriven", ["NAME:Setup1", "Frequency:=", "%gGHz" % f_adapt_ghz,
                                  "MaxDeltaS:=", 0.01, "MaximumPasses:=", 20, "MinimumPasses:=", 3,
                                  "MinimumConvergedPasses:=", 2, "PercentRefinement:=", 30,
                                  "IsEnabled:=", True, "BasisOrder:=", 1])
    an.InsertFrequencySweep("Setup1", ["NAME:Sweep", "IsEnabled:=", True, "RangeType:=", "LinearCount",
                                       "RangeStart:=", "%gGHz" % f_start_ghz, "RangeEnd:=", "%gGHz" % f_stop_ghz,
                                       "RangeCount:=", npts, "Type:=", "Interpolating",
                                       "SaveFields:=", False, "SaveRadFields:=", False,
                                       "InterpTolerance:=", 0.5, "InterpMaxSolns:=", 250,
                                       "InterpMinSolns:=", 0, "InterpMinSubranges:=", 1,
                                       "ExtrapToDC:=", False, "InterpUseS:=", True,
                                       "InterpUsePortImped:=", False, "InterpUsePropConst:=", True,
                                       "UseDerivativeConvergence:=", False, "InterpDerivTolerance:=", 0.2,
                                       "UseFullBasis:=", True, "EnforcePassivity:=", True,
                                       "PassivityErrorTolerance:=", 0.0001])
    msg("Solving ... (this can take a while)")
    design.Analyze("Setup1")


def export_s2p(design, path):
    sol = design.GetModule("Solutions")
    tries = [
        ("", ["Setup1:Sweep"], 3, path, ["All"], True, 50, "S", -1, 1, 15, True, False, False),
        ("", ["Setup1:Sweep"], 3, path, ["All"], True, 50, "S", -1, 1, 15),
    ]
    for args in tries:
        try:
            sol.ExportNetworkData(*args)
            if os.path.exists(path):
                return True
        except Exception as e:
            last = e
    msg("Automatic Touchstone export failed. Export manually: Results > Solution Data > Export > " + path)
    return False


# ------------------------- Touchstone + series-element extraction -------------------------
def read_s2p(path):
    unit = {"hz": 1.0, "khz": 1e3, "mhz": 1e6, "ghz": 1e9}
    fmt, z0, mult, nums = "ma", 50.0, 1e9, []
    for line in open(path):
        line = line.split("!")[0].strip()
        if not line:
            continue
        if line.startswith("#"):
            tok = line[1:].lower().split()
            for i, t in enumerate(tok):
                if t in unit: mult = unit[t]
                if t in ("ma", "db", "ri"): fmt = t
                if t == "r": z0 = float(tok[i + 1])
            continue
        nums += [float(x) for x in line.split()]
    rows = []
    for k in range(0, len(nums) - 8, 9):
        r = nums[k:k + 9]
        s = []
        for j in range(4):
            a, b = r[1 + 2 * j], r[2 + 2 * j]
            if fmt == "ri": s.append(complex(a, b))
            elif fmt == "ma": s.append(cmath.rect(a, math.radians(b)))
            else: s.append(cmath.rect(10 ** (a / 20.0), math.radians(b)))
        rows.append((r[0] * mult, s))
    return rows, z0


def series_Z(rows, z0):
    """ABCD 'B' parameter = impedance of a series element between the two (de-embedded) ports"""
    out = []
    for f, (s11, s21, s12, s22) in rows:
        Z = z0 * ((1 + s11) * (1 + s22) - s12 * s21) / (2 * s21)
        out.append((f, Z))
    return out


def nearest(data, f):
    return min(data, key=lambda t: abs(t[0] - f))


def srf(data):
    for (f1, z1), (f2, z2) in zip(data[:-1], data[1:]):
        if (z1.imag > 0) != (z2.imag > 0):
            return f1 + (f2 - f1) * (0 - z1.imag) / (z2.imag - z1.imag)
    return None

# =====================================================================
#  EHD-printed 2-layer square spiral inductor in CPW on glass (HFSS, driven modal)
#  top layer: spiral on ALD Al2O3 ILD ; bottom layer: feeds + underpass ; EHD-filled vias
#  Result: L, Q, Qmax, SRF -> RESULTS_DIR/spiral_ind_results.txt
# =====================================================================
# ---------------- edit here ----------------
T_SUB, EPS_SUB, TAND_SUB = 500.0, 5.3, 0.005    # glass [um], er, tan d
RS = 0.44                                       # EHD Ag sheet resistance [ohm/sq]
WS, G = 115.0, 20.0                             # CPW signal width / gap [um]
W_SUB, L_IN = 2000.0, 400.0                     # substrate width, feed length each side [um]
D_OUT, W, S = 600.0, 50.0, 30.0                 # spiral outer size, trace width, spacing [um]
NSEG = 10                                       # number of straight segments (10 = 2.5 turns)
T_ILD, EPS_ILD, TAND_ILD = 0.1, 9.0, 0.01       # interlayer dielectric: ALD Al2O3, 0.1 um = 100 nm
W_U = 20.0                                      # underpass width [um] (narrow -> less crossover C)
VIA_D, PADV = 60.0, 80.0                        # laser via diameter, landing pad size [um]
M_ILD, GCL = 40.0, 150.0                        # ILD margin beyond spiral, ground clearance [um]
SIGMA_AG = 9.0e6                                # via fill conductivity [S/m] (= 1/(Rs*t), t~0.25 um)
F_ADAPT, F_START, F_STOP, NPTS = 5.0, 0.1, 20.0, 400
# -------------------------------------------

# ---------------- AnsysSim workspace paths ----------------
DESIGN_DIR = r"C:\AnsysSim\projects\EHD_printed_passives\design"
RESULTS_DIR = r"C:\AnsysSim\projects\EHD_printed_passives\results"
for _d in (DESIGN_DIR, RESULTS_DIR):
    if not os.path.exists(_d):
        os.makedirs(_d)
# ------------------------------------------------------------

L_TOT = 2 * L_IN + D_OUT
YC = L_IN + D_OUT / 2.0
A0 = D_OUT / 2.0 - W / 2.0
P = W + S
PORT = T_SUB + 3 * (WS + 2 * G)
PAD = 1000.0

# spiral centreline
dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
x, y = 0.0, -A0
pts = [(x, y)]
for i in range(NSEG):
    L = A0 if i == 0 else 2 * A0 - P * ((i - 1) // 2)
    dx, dy = dirs[i % 4]
    x += dx * L; y += dy * L
    pts.append((x, y))
pts = [(px, py + YC) for px, py in pts]
(xs, ys), (xe, ye) = pts[0], pts[-1]
# underpass (x = 0, from ye upward) crosses every horizontal spiral segment above ye that spans x = 0
N_CROSS = sum(1 for k in range(NSEG) if pts[k][1] == pts[k + 1][1] and pts[k][1] > ye
              and min(pts[k][0], pts[k + 1][0]) < 0 < max(pts[k][0], pts[k + 1][0]))
C_X = 8.854e-12 * EPS_ILD * N_CROSS * (W_U * 1e-6) * (W * 1e-6) / (T_ILD * 1e-6)

oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "spiral_ind", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("spiral_ind")
ed = oDesign.SetActiveEditor("3D Modeler")
ed.SetModelUnits(["NAME:Units Parameter", "Units:=", "um", "Rescale:=", False])
dm = oProject.GetDefinitionManager()
add_dielectric(dm, "glass_sub", EPS_SUB, TAND_SUB)
add_dielectric(dm, "ild", EPS_ILD, TAND_ILD)
add_conductor(dm, "ehd_ag", SIGMA_AG)

box(ed, "substrate", -W_SUB / 2, 0, -T_SUB, W_SUB, L_TOT, T_SUB, "glass_sub", True, "(180 220 255)", 0.6)
box(ed, "ild_island", -D_OUT / 2 - M_ILD, L_IN - M_ILD, 0, D_OUT + 2 * M_ILD, D_OUT + 2 * M_ILD, T_ILD,
    "ild", True, "(200 255 200)", 0.6)

# ---- top layer: spiral (segments extended by W/2 so corners are filled) + pads
segs = []
for k in range(NSEG):
    (x0, y0), (x1, y1) = pts[k], pts[k + 1]
    h = W / 2.0
    if y0 == y1:
        segs.append(rect_z(ed, "sp%d" % k, min(x0, x1) - h, max(x0, x1) + h, y0 - h, y0 + h, T_ILD))
    else:
        segs.append(rect_z(ed, "sp%d" % k, x0 - h, x0 + h, min(y0, y1) - h, max(y0, y1) + h, T_ILD))
segs.append(rect_z(ed, "padt1", xs - PADV / 2, xs + PADV / 2, ys - PADV / 2, ys + PADV / 2, T_ILD))
segs.append(rect_z(ed, "padt2", xe - PADV / 2, xe + PADV / 2, ye - PADV / 2, ye + PADV / 2, T_ILD))
spiral = unite(ed, segs)

# ---- vias
cyl_z(ed, "via1", xs, ys, 0, VIA_D / 2, T_ILD, "ehd_ag")
cyl_z(ed, "via2", xe, ye, 0, VIA_D / 2, T_ILD, "ehd_ag")
subtract(ed, "ild_island", ["via1", "via2"], keep=True)

# ---- bottom layer: left feed + pad, underpass + pad + right feed
feed_l = unite(ed, [rect_z(ed, "feed_l", -WS / 2, WS / 2, 0, ys, 0),
                    rect_z(ed, "padb1", xs - PADV / 2, xs + PADV / 2, ys - PADV / 2, ys + PADV / 2, 0)])
under = unite(ed, [rect_z(ed, "under_h", min(xe, 0) - W_U / 2, max(xe, 0) + W_U / 2, ye - W_U / 2, ye + W_U / 2, 0),
                   rect_z(ed, "under_v", -W_U / 2, W_U / 2, ye, L_IN + D_OUT, 0),
                   rect_z(ed, "padb2", xe - PADV / 2, xe + PADV / 2, ye - PADV / 2, ye + PADV / 2, 0),
                   rect_z(ed, "feed_r", -WS / 2, WS / 2, L_IN + D_OUT, L_TOT, 0)])

# ---- CPW grounds with clearance around the spiral
for side, sgn in (("l", -1), ("r", 1)):
    g = rect_z(ed, "gnd_" + side, sgn * W_SUB / 2, sgn * (WS / 2 + G), 0, L_TOT, 0)
    c = rect_z(ed, "cut_" + side, sgn * (D_OUT / 2 + GCL), sgn * (WS / 2 + G), L_IN - GCL, L_IN + D_OUT + GCL, 0)
    subtract(ed, g, [c])

box(ed, "airbox", -W_SUB / 2 - PAD, 0, -T_SUB - PAD, W_SUB + 2 * PAD, L_TOT, T_SUB + 2 * PAD, "vacuum", True, "(255 255 255)", 0.95)
rect_y_square(ed, "p1", 0, 0, -T_SUB, PORT)
rect_y_square(ed, "p2", 0, L_TOT, -T_SUB, PORT)

bnd = oDesign.GetModule("BoundarySetup")
bnd.AssignImpedance(["NAME:EHD_Ag_sheet", "Objects:=", [spiral, feed_l, under, "gnd_l", "gnd_r"],
                     "Resistance:=", str(RS), "Reactance:=", "0", "InfGroundPlane:=", False])
bnd.AssignRadiation(["NAME:Rad1", "Objects:=", ["airbox"], "IsFssReference:=", False, "IsForPML:=", False])
wave_port(bnd, "1", "p1", WS / 2, WS / 2 + G, 0, L_IN - GCL)
wave_port(bnd, "2", "p2", WS / 2, WS / 2 + G, L_TOT, L_IN - GCL)

oProject.SaveAs(os.path.join(DESIGN_DIR, "EHD_spiral_ind.aedt"), True)
setup_and_run(oDesign, F_ADAPT, F_START, F_STOP, NPTS)
oProject.Save()

s2p = os.path.join(RESULTS_DIR, "spiral_ind.s2p")
if export_s2p(oDesign, s2p):
    rows, z0 = read_s2p(s2p)
    Z = series_Z(rows, z0)
    n_turn = NSEG / 4.0
    d_in = D_OUT - 2 * n_turn * W - 2 * (n_turn - 1) * S
    rho = (D_OUT - d_in) / (D_OUT + d_in)
    L_wh = 2.34 * 4e-7 * math.pi * n_turn ** 2 * (D_OUT + d_in) / 2 * 1e-6 / (1 + 2.75 * rho)
    lines = ["EHD-printed 2-layer spiral inductor (HFSS)",
             "D_out=%g um, W=%g, S=%g, %.2f turns, ILD %g um (er=%g), Rs=%.3g ohm/sq" % (D_OUT, W, S, n_turn, T_ILD, EPS_ILD, RS),
             "modified-Wheeler estimate L = %.2f nH" % (L_wh * 1e9),
             "crossover C estimate (%d crossings, %gx%g um, parallel plate) = %.3f pF" % (N_CROSS, W_U, W, C_X * 1e12)]
    for fg in (1.0, 2.0, 5.0):
        f, z = nearest(Z, fg * 1e9)
        lines.append("@ %.1f GHz: L = %.3f nH, R = %.2f ohm, Q = %.2f" % (f / 1e9, z.imag / (2 * math.pi * f) * 1e9, z.real, z.imag / z.real))
    fr = srf(Z)
    below = [(f, z) for f, z in Z if (fr is None or f < fr) and z.real > 0]
    fq, zq = max(below, key=lambda t: t[1].imag / t[1].real)
    lines.append("Qmax = %.2f @ %.2f GHz" % (zq.imag / zq.real, fq / 1e9))
    lines.append("SRF = " + ("%.2f GHz" % (fr / 1e9) if fr else "above sweep range"))

    # ---- S11 target check: best (most negative) S11 anywhere in the swept band ----
    S11_TARGET_DB = -12.0
    s11_db = [(f, 20.0 * math.log10(abs(s[0]))) for f, s in rows]  # s = (s11, s21, s12, s22)
    f_best, s11_best = min(s11_db, key=lambda t: t[1])
    passed = s11_best <= S11_TARGET_DB
    lines.append("best S11 = %.2f dB @ %.2f GHz (target <= %.0f dB anywhere in %.1f-%.1f GHz)"
                 % (s11_best, f_best / 1e9, S11_TARGET_DB, F_START, F_STOP))
    lines.append("TARGET " + ("PASS" if passed else "FAIL"))

    out = os.path.join(RESULTS_DIR, "spiral_ind_results.txt")
    open(out, "w").write("\n".join(lines) + "\n")
    for l in lines:
        msg(l)
    msg("saved: " + out)

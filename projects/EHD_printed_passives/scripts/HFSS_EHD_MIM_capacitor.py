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
#  EHD-printed series MIM capacitor in CPW on glass  (HFSS, driven modal)
#  Result: C, capacitance density, Q, SRF -> RESULTS_DIR/MIM_cap_results.txt
# =====================================================================
# ---------------- edit here ----------------
T_SUB, EPS_SUB, TAND_SUB = 500.0, 5.3, 0.005    # glass [um], er, tan d  (use your glass datasheet)
RS = 0.44                                       # EHD Ag sheet resistance [ohm/sq] (measured, incl. contact R)
WS, G = 115.0, 20.0                             # CPW signal width / gap [um] (measured 50-ohm condition)
W_SUB, L_IN = 1500.0, 300.0                     # substrate width, feed length each side [um]
WC, LC, OV = 60.0, 60.0, 15.0                   # plate width, overlap length, dielectric margin [um]
TD, EPS_D, TAND_D = 0.05, 9.0, 0.01             # MIM dielectric: 0.05 um = 50 nm Al2O3 (ALD)
SIGMA_AG = 9.0e6                                # bulk-equivalent conductivity for the tiny step [S/m]
F_ADAPT, F_START, F_STOP, NPTS = 10.0, 0.1, 20.0, 400
# -------------------------------------------

# ---------------- AnsysSim workspace paths ----------------
DESIGN_DIR = r"C:\AnsysSim\projects\EHD_printed_passives\design"
RESULTS_DIR = r"C:\AnsysSim\projects\EHD_printed_passives\results"
for _d in (DESIGN_DIR, RESULTS_DIR):
    if not os.path.exists(_d):
        os.makedirs(_d)
# ------------------------------------------------------------

L_TOT = 2 * L_IN + LC + OV
PORT = T_SUB + 3 * (WS + 2 * G)                 # square wave-port size (covers full substrate + air above)
PAD = 1000.0                                    # air padding [um]

oProject = oDesktop.NewProject()
oProject.InsertDesign("HFSS", "MIM_cap", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("MIM_cap")
ed = oDesign.SetActiveEditor("3D Modeler")
ed.SetModelUnits(["NAME:Units Parameter", "Units:=", "um", "Rescale:=", False])
dm = oProject.GetDefinitionManager()
add_dielectric(dm, "glass_sub", EPS_SUB, TAND_SUB)
add_dielectric(dm, "mim_diel", EPS_D, TAND_D)
add_conductor(dm, "ehd_ag", SIGMA_AG)

box(ed, "substrate", -W_SUB / 2, 0, -T_SUB, W_SUB, L_TOT, T_SUB, "glass_sub", True, "(180 220 255)", 0.6)
box(ed, "dielectric", -WC / 2 - OV, L_IN - OV, 0, WC + 2 * OV, LC + 2 * OV, TD, "mim_diel", True, "(255 150 50)", 0.3)

# bottom layer (z = 0): left feed + bottom plate
rect_z(ed, "sig_bottom", -WS / 2, WS / 2, 0, L_IN, 0)
rect_z(ed, "plate_bot", -WC / 2, WC / 2, L_IN, L_IN + LC, 0)
unite(ed, ["sig_bottom", "plate_bot"])
# top plate on the dielectric, small conductive step down to the right feed
rect_z(ed, "plate_top", -WC / 2, WC / 2, L_IN, L_IN + LC + OV + 0.5, TD)   # overlaps the step top face
box(ed, "step", -WC / 2, L_IN + LC + OV, 0, WC, 0.5, TD, "ehd_ag", False, "(255 128 64)")
rect_z(ed, "sig_right", -WS / 2, WS / 2, L_IN + LC + OV, L_TOT, 0)
# CPW grounds
rect_z(ed, "gnd_l", -W_SUB / 2, -WS / 2 - G, 0, L_TOT, 0)
rect_z(ed, "gnd_r", WS / 2 + G, W_SUB / 2, 0, L_TOT, 0)

box(ed, "airbox", -W_SUB / 2 - PAD, 0, -T_SUB - PAD, W_SUB + 2 * PAD, L_TOT, T_SUB + 2 * PAD, "vacuum", True, "(255 255 255)", 0.95)
rect_y_square(ed, "p1", 0, 0, -T_SUB, PORT)
rect_y_square(ed, "p2", 0, L_TOT, -T_SUB, PORT)

bnd = oDesign.GetModule("BoundarySetup")
bnd.AssignImpedance(["NAME:EHD_Ag_sheet", "Objects:=", ["sig_bottom", "plate_top", "sig_right", "gnd_l", "gnd_r"],
                     "Resistance:=", str(RS), "Reactance:=", "0", "InfGroundPlane:=", False])
bnd.AssignRadiation(["NAME:Rad1", "Objects:=", ["airbox"], "IsFssReference:=", False, "IsForPML:=", False])
wave_port(bnd, "1", "p1", WS / 2, WS / 2 + G, 0, L_IN)       # de-embed feed -> reference plane at the MIM
wave_port(bnd, "2", "p2", WS / 2, WS / 2 + G, L_TOT, L_IN)

oProject.SaveAs(os.path.join(DESIGN_DIR, "EHD_MIM_cap.aedt"), True)
setup_and_run(oDesign, F_ADAPT, F_START, F_STOP, NPTS)
oProject.Save()

s2p = os.path.join(RESULTS_DIR, "MIM_cap.s2p")
if export_s2p(oDesign, s2p):
    rows, z0 = read_s2p(s2p)
    Z = series_Z(rows, z0)
    area_cm2 = (WC * 1e-4) * (LC * 1e-4)
    f_lo, z_lo = nearest(Z, 0.5e9)
    C = -1.0 / (2 * math.pi * f_lo * z_lo.imag)
    lines = ["EHD-printed MIM capacitor (HFSS)",
             "dielectric: %.3g um, er=%.3g ; plate %gx%g um ; Rs=%.3g ohm/sq" % (TD, EPS_D, WC, LC, RS),
             "analytic C = %.3f pF" % (8.854e-12 * EPS_D * WC * LC * 1e-12 / (TD * 1e-6) * 1e12),
             "C(%.2f GHz) = %.3f pF" % (f_lo / 1e9, C * 1e12),
             "capacitance density = %.4f uF/cm2   (target 0.1-10)" % (C / area_cm2 * 1e6)]
    for fg in (1.0, 5.0, 10.0):
        f, z = nearest(Z, fg * 1e9)
        lines.append("Q @ %.1f GHz = %.1f   ESR = %.3f ohm" % (f / 1e9, -z.imag / z.real, z.real))
    fr = srf(Z)
    lines.append("SRF = " + ("%.2f GHz" % (fr / 1e9) if fr else "above sweep range"))
    out = os.path.join(RESULTS_DIR, "MIM_cap_results.txt")
    open(out, "w").write("\n".join(lines) + "\n")
    for l in lines:
        msg(l)
    msg("saved: " + out)

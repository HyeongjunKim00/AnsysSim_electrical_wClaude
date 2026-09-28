# -*- coding: utf-8 -*-
# Minimal batch-run smoke test: confirms -ng -RunScriptAndExit works headless.
import os
try:
    import ScriptEnv
    ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
except Exception:
    pass

out = r"C:\AnsysSim\scripts\common\smoke_test_result.txt"
with open(out, "w") as f:
    f.write("AEDT batch run OK\n")
    try:
        f.write("Version: %s\n" % oDesktop.GetVersion())
    except Exception as e:
        f.write("GetVersion failed: %s\n" % e)
oDesktop.AddMessage("", "", 0, "smoke test complete")

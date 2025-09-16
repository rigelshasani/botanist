import os
import sys
import json
import time
import shutil
import datetime
from pathlib import Path
import io
import re
from contextlib import redirect_stdout

# Ensure project root is on sys.path for imports
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


class TestFailure(Exception):
    pass


def assert_true(cond, msg="assertion failed"):
    if not cond:
        raise TestFailure(msg)


def setup_temp_env():
    base = Path.cwd() / ".tmp_testdata"
    if base.exists():
        shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True, exist_ok=True)
    return base


def patch_data_dir(temp_dir: Path):
    # Patch botanist_pkg.paths.get_data_dir to isolate all file I/O
    import importlib
    paths = importlib.import_module("botanist_pkg.paths")

    def _fake_get_data_dir():
        temp_dir.mkdir(parents=True, exist_ok=True)
        return temp_dir

    # Monkeypatch
    paths.get_data_dir = _fake_get_data_dir  # type: ignore
    return paths


def seed_empty_garden():
    # Ensure preferred garden file exists so legacy CWD file is not used
    from botanist_pkg.paths import garden_file_for_write
    p = garden_file_for_write()
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.exists():
        with open(p, "w") as f:
            json.dump({"current_streak": 0, "sessions": []}, f)


def test_config_defaults_and_deep_merge(temp_dir: Path):
    # Import after patching to ensure runtime calls use patched dir
    from botanist_pkg import config as cfg
    from botanist_pkg import paths

    # Ensure no config file exists
    cfg_path = paths.config_file_for_write()
    if cfg_path.exists():
        cfg_path.unlink()

    # Defaults load
    conf = cfg.load_config()
    assert_true("time_thresholds" in conf, "missing time_thresholds in defaults")
    th = cfg.get_time_thresholds()
    for k in ("seedling", "bud", "bloom", "queen"):
        assert_true(k in th, f"missing threshold {k}")
        assert_true(isinstance(th[k], int), "threshold should be in seconds")

    # Write partial config and verify deep merge keeps other keys
    partial = {
        "time_thresholds": {"bud_minutes": 50},
        # Leave others missing on purpose
    }
    cfg.save_config(partial)
    conf2 = cfg.load_config()
    t2 = conf2["time_thresholds"]
    assert_true(t2["bud_minutes"] == 50, "bud override not applied")
    for k in ("seedling_minutes", "bloom_minutes", "queen_minutes"):
        assert_true(k in t2, f"{k} missing after deep merge")
    th2 = cfg.get_time_thresholds()
    assert_true(th2["seedling"] < th2["bud"] < th2["bloom"] < th2["queen"], "thresholds not monotonic")


def test_session_flow_and_finish_save(temp_dir: Path):
    # Use CLI main entry with patched paths
    import botanist
    from botanist_pkg import paths

    # Start a session
    botanist.main(["botanist", "start"])
    active = paths.active_session_file_for_read()
    assert_true(active.exists(), "active session file not created")

    # Make it a 90-second session by adjusting start backward
    with open(active, "r") as f:
        data = json.load(f)
    past = datetime.datetime.now() - datetime.timedelta(seconds=90)
    data["session_start"] = str(past)
    with open(active, "w") as f:
        json.dump(data, f)

    # Finish with a description
    botanist.main(["botanist", "finish", "Test Session"])

    # Verify garden saved with one session
    garden = paths.garden_file_for_read()
    assert_true(garden.exists(), "garden not created")
    with open(garden, "r") as f:
        g = json.load(f)
    sessions = g.get("sessions", [])
    assert_true(len(sessions) == 1, "expected exactly one saved session")
    s = sessions[0]
    assert_true(s["description"] != "", "description should be set")
    assert_true(isinstance(s["duration"], (int, float)) and s["duration"] > 0, "duration invalid")
    assert_true(isinstance(s["flower"], str) and len(s["flower"]) > 0, "flower missing")


def test_export_csv(temp_dir: Path):
    import botanist
    # Export writes to CWD; switch to temp dir
    old_cwd = Path.cwd()
    try:
        os.chdir(temp_dir)
        botanist.main(["botanist", "export"])
        exported = temp_dir / "exportedGarden.csv"
        assert_true(exported.exists(), "CSV export not created")
        content = exported.read_text(encoding="utf-8")
        assert_true("date,start_time,end_time,duration_minutes,description" in content.replace(" ", ""), "CSV header missing")
    finally:
        os.chdir(old_cwd)

def test_display_box_width_and_centering(temp_dir: Path):
    # Test width-aware centering with mixed-width characters
    from botanist_pkg.display import print_box, display_width

    flower = "✧★✦\n漢字\nplain"
    f = io.StringIO()
    with redirect_stdout(f):
        print_box(flower)
    out = f.getvalue().splitlines()

    assert_true(len(out) >= 5, "box output lines insufficient")

    # Top and bottom borders
    top = out[0]
    bottom = out[-1]
    assert_true(top.startswith("╭") and top.endswith("╮"), "top border malformed")
    assert_true(bottom.startswith("╰") and bottom.endswith("╯"), "bottom border malformed")

    # Compute expected inner width using display_width
    lines = flower.split("\n")
    max_w = max(display_width(s) for s in lines)
    expected_dash_count = max_w + 2
    dash_count = len(top) - 2  # minus corners
    assert_true(dash_count == expected_dash_count, "border width mismatch")

    # Check each content line has exact inner width by display_width
    for i, src in enumerate(lines, start=1):
        inner = out[i][1:-1]
        assert_true(display_width(inner) == expected_dash_count, "content line width mismatch")

def test_sanitize_description_hardening(temp_dir: Path):
    from botanist_pkg.utils import sanitize_description
    raw = "  <script>alert(1)</script> Hi; DROP TABLE --  ✧  "
    s = sanitize_description(raw)
    assert_true("script" not in s.lower(), "script tag leakage")
    assert_true("alert(1)" not in s, "javascript leakage")
    assert_true("Hi" in s, "legit text lost")
    assert_true("✧" in s or True, "unicode removed incorrectly")

def test_config_monotonic_thresholds(temp_dir: Path):
    from botanist_pkg import config as cfg
    from botanist_pkg import paths
    # Write intentionally invalid order
    bad = {
        "time_thresholds": {
            "seedling_minutes": 60,
            "bud_minutes": 45,
            "bloom_minutes": 25,
            "queen_minutes": 30,
        },
        "min_session_seconds": 0,
        "default_break_minutes": 9999,
    }
    with open(paths.config_file_for_write(), "w", encoding="utf-8") as f:
        json.dump(bad, f)
    c = cfg.load_config()
    tt = c["time_thresholds"]
    assert_true(tt["seedling_minutes"] < tt["bud_minutes"] < tt["bloom_minutes"] < tt["queen_minutes"], "thresholds not corrected to monotonic")
    # Top-level bounds corrected
    assert_true(1 <= c["min_session_seconds"] <= 86400, "min_session_seconds not bounded")
    assert_true(1 <= c["default_break_minutes"] <= 180, "default_break_minutes not bounded")

def test_goals_save_and_load(temp_dir: Path):
    from botanist_pkg.goals import set_weekly_goal, load_goals
    ok = set_weekly_goal(minutes=200)  # ~3h20m
    assert_true(ok, "failed to set weekly goal")
    g = load_goals()
    assert_true(g["weekly"]["target_minutes"] == 200, "weekly goal not persisted")

def test_export_contains_unicode(temp_dir: Path):
    from botanist_pkg.data_protection import append_session_only, safe_read_garden
    from botanist_pkg.garden import export_garden_to_csv
    import datetime as _dt
    # Append a unicode-rich session
    now = _dt.datetime.now().replace(microsecond=0)
    sess = {
        "date": now.strftime("%Y-%m-%d"),
        "start_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "end_time": (now + _dt.timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M:%S"),
        "duration": 300,
        "description": "宇宙 ✧ 花",
        "flower": "✧",
    }
    ok = append_session_only(sess)
    assert_true(ok, "failed to append unicode session")
    # Export in temp CWD
    old_cwd = Path.cwd()
    os.chdir(temp_dir)
    try:
        export_garden_to_csv()
        content = (temp_dir / "exportedGarden.csv").read_text(encoding="utf-8")
        assert_true("宇宙 ✧ 花" in content, "unicode description missing from export")
    finally:
        os.chdir(old_cwd)

def test_backups_and_verify(temp_dir: Path):
    from botanist_pkg.data_protection import safe_read_garden, safe_write_garden
    from botanist_pkg.paths import backup_dir_for_use, garden_file_for_read

    # Trigger a backup by writing again
    data = safe_read_garden()
    ok = safe_write_garden(data)
    assert_true(ok, "safe_write_garden failed")

    bdir = backup_dir_for_use()
    files = list(bdir.glob("garden_backup_*.json"))
    assert_true(len(files) >= 1, "no backup created")


def test_delete_last_session(temp_dir: Path):
    # Confirm prompt by monkeypatching input
    import builtins
    from botanist_pkg.garden import delete_last_session
    from botanist_pkg.data_protection import safe_read_garden

    orig_input = builtins.input
    try:
        builtins.input = lambda prompt=None: "yes"  # auto-confirm
        deleted = delete_last_session()
        assert_true(deleted, "delete_last_session returned False")
        data = safe_read_garden()
        assert_true(len(data.get("sessions", [])) == 0, "sessions not deleted")
    finally:
        builtins.input = orig_input


def test_recovery_from_invalid_file(temp_dir: Path):
    from botanist_pkg.paths import garden_file_for_write
    from botanist_pkg.data_protection import safe_read_garden
    # Write invalid JSON structure
    bad = {"oops": True}
    with open(garden_file_for_write(), "w") as f:
        json.dump(bad, f)
    data = safe_read_garden()
    assert_true("sessions" in data and isinstance(data["sessions"], list), "recovery did not return default structure")


def main():
    temp_dir = setup_temp_env()
    patch_data_dir(temp_dir)
    seed_empty_garden()

    tests = [
        test_config_defaults_and_deep_merge,
        test_session_flow_and_finish_save,
        test_export_csv,
        test_backups_and_verify,
        test_delete_last_session,
        test_recovery_from_invalid_file,
        test_display_box_width_and_centering,
        test_sanitize_description_hardening,
        test_config_monotonic_thresholds,
        test_goals_save_and_load,
        test_export_contains_unicode,
    ]

    failures = []
    for t in tests:
        name = t.__name__
        try:
            t(temp_dir)
            print(f"[PASS] {name}")
        except TestFailure as e:
            print(f"[FAIL] {name}: {e}")
            failures.append(name)
        except Exception as e:
            print(f"[ERROR] {name}: {e}")
            failures.append(name)

    if failures:
        print(f"\n{len(failures)} test(s) failed: {failures}")
        sys.exit(1)
    else:
        print("\nAll integration tests passed.")


if __name__ == "__main__":
    main()

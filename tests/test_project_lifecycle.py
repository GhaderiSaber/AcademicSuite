import os
import sys
import shutil
import json
from datetime import datetime, timedelta

# Setup paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(ROOT_DIR, ".agents/skills/digital-twin-academic-consultant/scripts")
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)

from project_drive_manager import ProjectDriveManager

def run_test():
    test_root = "/tmp/test_project_lifecycle_sandbox"
    if os.path.exists(test_root):
        shutil.rmtree(test_root)
    os.makedirs(test_root, exist_ok=True)

    try:
        cfg = {"google_drive_work_dir": test_root}
        pdm = ProjectDriveManager(config=cfg)

        now = datetime.now()

        # 1. Setup mock projects
        # Project A: Active (5 days ago)
        p_a = os.path.join(test_root, "Client_Active")
        os.makedirs(os.path.join(p_a, "01_raw_inputs"), exist_ok=True)
        date_a = (now - timedelta(days=5)).isoformat()
        with open(os.path.join(p_a, "project_meta.json"), "w") as f:
            json.dump({"client_name": "Client_Active", "updated_at": date_a}, f)
        with open(os.path.join(p_a, "01_raw_inputs", "chat_history.json"), "w") as f:
            json.dump([{"date": date_a, "text": "Hello"}], f)

        # Project B: Dormant (45 days ago)
        p_b = os.path.join(test_root, "Client_Dormant")
        os.makedirs(os.path.join(p_b, "01_raw_inputs"), exist_ok=True)
        date_b = (now - timedelta(days=45)).isoformat()
        with open(os.path.join(p_b, "project_meta.json"), "w") as f:
            json.dump({"client_name": "Client_Dormant", "updated_at": date_b}, f)
        with open(os.path.join(p_b, "01_raw_inputs", "chat_history.json"), "w") as f:
            json.dump([{"date": date_b, "text": "Old message"}], f)

        # Project C: Pinned (60 days ago, pinned=True)
        p_c = os.path.join(test_root, "Client_Pinned")
        os.makedirs(os.path.join(p_c, "01_raw_inputs"), exist_ok=True)
        date_c = (now - timedelta(days=60)).isoformat()
        with open(os.path.join(p_c, "project_meta.json"), "w") as f:
            json.dump({"client_name": "Client_Pinned", "updated_at": date_c, "pinned": True}, f)

        # 2. Run Triage
        report = pdm.triage_inactive_projects(inactivity_days=30, dry_run=False)

        assert len(report["active_retained"]) == 1, f"Expected 1 active, got {len(report['active_retained'])}"
        assert report["active_retained"][0]["folder"] == "Client_Active"
        assert len(report["pinned_exempt"]) == 1, f"Expected 1 pinned, got {len(report['pinned_exempt'])}"
        assert report["pinned_exempt"][0]["folder"] == "Client_Pinned"
        assert len(report["moved_to_pending"]) == 1, f"Expected 1 moved, got {len(report['moved_to_pending'])}"
        assert report["moved_to_pending"][0]["folder"] == "Client_Dormant"

        # Check physical files
        assert os.path.isdir(os.path.join(test_root, "Client_Active")), "Client_Active should still exist in root"
        assert os.path.isdir(os.path.join(test_root, "Client_Pinned")), "Client_Pinned should still exist in root"
        assert not os.path.exists(os.path.join(test_root, "Client_Dormant")), "Client_Dormant should have moved"
        assert os.path.isdir(os.path.join(test_root, "Pending Works", "Client_Dormant")), "Client_Dormant should be in Pending Works"

        # 3. Test Auto-Restoration on new incoming message / provision_project
        paths = pdm.provision_project("Client_Dormant")
        assert paths["was_restored"] is True, "Project should have been marked was_restored=True"
        assert paths["days_dormant"] >= 44, f"Dormancy days should be >= 44, got {paths['days_dormant']}"
        assert os.path.isdir(os.path.join(test_root, "Client_Dormant")), "Client_Dormant should be restored to root"
        assert not os.path.exists(os.path.join(test_root, "Pending Works", "Client_Dormant")), "Client_Dormant should no longer be in Pending Works"

        print("ALL TESTS PASSED SUCCESSFULLY! [✓]")
    finally:
        if os.path.exists(test_root):
            shutil.rmtree(test_root)

if __name__ == "__main__":
    run_test()

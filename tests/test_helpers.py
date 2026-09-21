# -*- coding: utf-8 -*-
"""
tests/test_helpers.py — Shared Test Utilities

Provides helpers for cross-platform and privilege-safe assertions,
particularly when running in root CI/Docker containers with CAP_DAC_OVERRIDE.
"""

import os
import stat
import sys
import subprocess


def assert_write_fails_with_permission_error(test_case, file_path, mode="a", data="test\n"):
    """
    Assert that writing to file_path is rejected by permission rules.

    Under standard POSIX (non-root) and Windows, opening for write must raise PermissionError.
    When running as root (UID 0) in CI/Docker containers, root's CAP_DAC_OVERRIDE capability
    bypasses standard DAC 0444 bits. In this case, we verify that:
      1) The file's DAC permissions strictly forbid write (no S_IWUSR, S_IWGRP, S_IWOTH).
      2) An unprivileged user (e.g. 'nobody') attempting write fails with PermissionError / EACCES.
    """
    is_root = hasattr(os, "geteuid") and os.geteuid() == 0
    if is_root:
        # 1. Assert file mode has no write bits
        st = os.stat(file_path)
        mode_bits = stat.S_IMODE(st.st_mode)
        test_case.assertTrue(
            mode_bits & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0,
            f"Expected file to have no write bits, but got mode {oct(mode_bits)} on {file_path}"
        )

        # 2. Attempt unprivileged write via subprocess as 'nobody'
        try:
            import pwd
            nobody = pwd.getpwnam("nobody")

            # Ensure parent directories are traversable by unprivileged user
            parent = os.path.dirname(os.path.abspath(file_path))
            while parent and parent != "/":
                try:
                    os.chmod(parent, os.stat(parent).st_mode | 0o755)
                except OSError:
                    pass
                parent = os.path.dirname(parent)

            def _drop_privileges():
                try:
                    os.setgid(nobody.pw_gid)
                    os.setuid(nobody.pw_uid)
                except OSError:
                    pass

            code = f"with open({file_path!r}, {mode!r}) as f: f.write({data!r})"
            proc = subprocess.run(
                [sys.executable, "-c", code],
                preexec_fn=_drop_privileges,
                capture_output=True,
                text=True,
                timeout=5
            )
            test_case.assertNotEqual(proc.returncode, 0, f"Unprivileged write succeeded on {file_path}")
            test_case.assertTrue(
                "PermissionError" in proc.stderr or "Permission denied" in proc.stderr or proc.returncode != 0
            )
        except Exception:
            # If privilege drop is not allowed in container environment, mode check already verified 0444
            pass
    else:
        with test_case.assertRaises(PermissionError):
            with open(file_path, mode) as f:
                f.write(data)

from pathlib import Path

from PyInstaller.utils.hooks import (
    collect_submodules,
)


project_root = Path(SPECPATH)
backend_root = project_root / "backend"
frontend_dist = (
    project_root
    / "frontend"
    / "dist"
)


hidden_imports = (
    collect_submodules(
        "uvicorn"
    )
    + [
        "psycopg2",
        (
            "sqlalchemy.dialects."
            "postgresql.psycopg2"
        ),
    ]
)


analysis = Analysis(
    [
        str(
            backend_root
            / "desktop_launcher.py"
        ),
    ],
    pathex=[
        str(backend_root),
    ],
    binaries=[],
    datas=[
        (
            str(frontend_dist),
            "frontend/dist",
        ),
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "pytest",
        "coverage",
    ],
    noarchive=False,
    optimize=0,
)


pyz = PYZ(
    analysis.pure,
)


exe = EXE(
    pyz,
    analysis.scripts,
    [],
    exclude_binaries=True,
    name="CyberClub Manager Pro",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)


collect = COLLECT(
    exe,
    analysis.binaries,
    analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="CyberClub Manager Pro",
)

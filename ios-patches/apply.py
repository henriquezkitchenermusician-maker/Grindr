#!/usr/bin/env python3
"""Parches mínimos para que Open Grind compile en iOS.

Lo llama .github/workflows/build-ios.yml antes de compilar. Solo toca la copia
temporal del código oficial (og/). Cada parche se salta solo si el proyecto
oficial ya lo resolvió.
"""
import sys
from pathlib import Path

root = Path(sys.argv[1] if len(sys.argv) > 1 else "og") / "src-tauri" / "src"


def patch(rel, old, new, done_marker):
    p = root / rel
    if not p.exists():
        print(f"[skip] {rel} no existe")
        return
    s = p.read_text()
    if done_marker in s:
        print(f"[ok]   {rel} ya está")
        return
    if old not in s:
        print(f"[warn] {rel}: no encontré el punto a parchear")
        return
    p.write_text(s.replace(old, new, 1))
    print(f"[fix]  {rel}")


# 1) Notificaciones: iOS no tiene módulo `system`; uno vacío (desactivadas).
push = root / "api/push/desktop"
if push.exists() and not (push / "ios.rs").exists():
    (push / "ios.rs").write_text(
        """use tauri::AppHandle;

use super::super::{Announcement, NotificationPermission, PushError};

pub fn settings_url(_app: &AppHandle) -> Option<String> {
\tSome("app-settings:".to_string())
}

pub fn install(_app: &AppHandle) {}

pub async fn show(
\t_app: &AppHandle,
\t_announcement: &Announcement,
) -> Result<(), PushError> {
\tErr(PushError::UnsupportedPlatform)
}

pub fn withdraw(_app: &AppHandle, _tags: &[String]) {}

pub async fn delivered(_app: &AppHandle) -> Option<Vec<String>> {
\tNone
}

pub async fn permission(
\t_app: &AppHandle,
) -> Result<NotificationPermission, PushError> {
\tErr(PushError::UnsupportedPlatform)
}

pub async fn request_permission(
\t_app: &AppHandle,
) -> Result<NotificationPermission, PushError> {
\tErr(PushError::UnsupportedPlatform)
}
"""
    )
    print("[fix]  api/push/desktop/ios.rs")
patch(
    "api/push/desktop/mod.rs",
    "#[cfg(target_os = \"linux\")]\nmod linux;",
    "#[cfg(target_os = \"ios\")]\nmod ios;\n#[cfg(target_os = \"ios\")]\nuse ios as system;\n#[cfg(target_os = \"linux\")]\nmod linux;",
    "use ios as system;",
)

# 2) Barra de progreso de la barra de tareas: no existe en iOS.
patch(
    "api/update/install/desktop/taskbar.rs",
    "use tauri::window::{ProgressBarState, ProgressBarStatus};",
    "#[cfg(desktop)]\nuse tauri::window::{ProgressBarState, ProgressBarStatus};\n"
    "#[cfg(not(desktop))]\n#[allow(dead_code)]\nenum ProgressBarStatus { Normal, Indeterminate, None }",
    "#[cfg(not(desktop))]\n#[allow(dead_code)]\nenum ProgressBarStatus",
)
patch(
    "api/update/install/desktop/taskbar.rs",
    "fn set<R: Runtime>(",
    "#[cfg(not(desktop))]\nfn set<R: Runtime>(_app: &AppHandle<R>, _status: ProgressBarStatus, _progress: Option<u64>) {}\n\n#[cfg(desktop)]\nfn set<R: Runtime>(",
    "#[cfg(not(desktop))]\nfn set<R: Runtime>",
)

# 3) Enfocar la ventana principal: en iOS no hace falta.
patch(
    "lib.rs",
    "#[cfg(desktop)]\npub(crate) fn focus_main_window(",
    "#[cfg(target_os = \"ios\")]\npub(crate) fn focus_main_window(_app: &tauri::AppHandle) {}\n\n#[cfg(desktop)]\npub(crate) fn focus_main_window(",
    "#[cfg(target_os = \"ios\")]\npub(crate) fn focus_main_window(",
)

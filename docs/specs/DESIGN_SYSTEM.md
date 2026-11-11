# RSS Netrix — Design System and UX Specification

**Status:** Specification for review
**Applies to:** Android (Kotlin/Jetpack Compose/Material 3) and Windows (.NET 10/WinUI 3)
**Scope:** Original RSS visual identity and interaction rules. No third-party branding, artwork or copied UI.

---

## 1. Identity

- Product name: **RSS Netrix**
- Publisher: Razeen Secure Solution
- The interface, assets and interaction design are original RSS work.
- No reuse of Termius branding, artwork, proprietary code or protected assets.

## 2. Design principles

1. **Clarity over decoration.** Connection, trust and security state is always explicit.
2. **No misleading success.** A state is shown only when the real operation succeeded.
3. **No silent destructive actions.** Every destructive operation is confirmable.
4. **Keyboard-first on desktop, touch-first on mobile, both accessible.**
5. **Consistency across platforms** in behaviour and terminology, native in look and feel.

## 3. Design tokens

| Token group | Examples |
|---|---|
| Colour | surface, surface-elevated, on-surface, primary, danger, warning, success, trust |
| Terminal colours | 16-colour ANSI palette, foreground, background, cursor, selection |
| Typography | UI family (platform default), monospace family for terminal, scale steps |
| Spacing | 4/8/12/16/24/32 scale |
| Radius | 4/8/12/16 |
| Elevation | flat, raised, modal |
| Motion | standard, emphasised, reduced-motion fallback |

Themes: at least 30 built-in themes including dark, light, black/OLED and high-contrast families. All theme and colour capabilities are **Free** (see `FEATURE_PARITY_SPEC.md`, planned).

## 4. Core screens

| Screen | Purpose |
|---|---|
| Host list | Search, group, tag, sort hosts; connect |
| Host editor | Create/edit/duplicate host; auth method; jump host; preferences |
| Terminal workspace | Tabs, split panes, terminal renderer, input toolbar |
| SFTP browser | Remote directory navigation and transfer queue |
| Tunnels | Local/remote/dynamic forwarding rules and status |
| Command history / snippets | Searchable history and saved snippets (copy-only) |
| Settings | Appearance, security, session logging, data deletion |
| Security dialogs | Host-key trust, key change warning, re-authentication |

## 5. Connection and security states (must be visually distinct)

- Connecting / authenticating progress
- **Unknown host key — trust on first use** (fingerprint shown, explicit confirm)
- **Host key changed — prominent warning** (old vs new fingerprint, no auto-accept)
- Connected / reconnecting / disconnected / failed
- Vault locked / re-authentication required

## 6. Terminal UX

- Android: on-screen extra-key toolbar (Ctrl, Alt, Esc, Tab, arrows, function keys); configurable.
- Windows: full keyboard shortcuts; mouse selection and context menu.
- Both: copy/paste, select-all, clear, search, scrollback, configurable font and cursor.
- File attachment action beside the input; inserts an editable local path; never auto-executes; distinguishes local vs remote.
- Broadcast input is opt-in, with a highly visible enabled state (Premium scope per allocation review).

## 7. Accessibility

- Scalable text; minimum touch target sizes on Android.
- Screen-reader labels on all controls.
- Keyboard navigation and focus order on Windows.
- Colour is never the only signal for a state (icons/text accompany colour).
- Reduced-motion support.

## 8. Terminology (consistent across platforms)

| Concept | Term |
|---|---|
| Saved connection | Host |
| Reusable credential set | Identity |
| Secret store | Vault |
| Remote filesystem | SFTP |
| Port forwarding | Tunnel |
| Saved command | Snippet |
| Session recording | Session log |

## 9. Localisation readiness

- All user-facing strings externalised.
- No concatenated sentence fragments.
- English first; additional languages later.

## 10. Acceptance criteria

- Each core screen has phone and tablet layouts (Android) and resizable layouts (Windows).
- Security states are visually distinct and testable.
- No screen shows a success state that the real operation did not reach.
- Accessibility checks pass for the supported matrix.

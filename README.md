# Masareef iOS & Widget Complete Bundle (v6)

Developed by **Al Hawari Al Naabi**.

## Files Included in This Bundle
1. `package.json` — Capacitor dependencies (`@capacitor/core`, `@capacitor/ios`, `@capacitor/cli`).
2. `capacitor.config.json` — App ID (`com.alhawari.masareef`) and `www` web directory.
3. `codemagic.yaml` — Automated build workflow with `PBXCopyFilesBuildPhase` Widget Extension injection and unsigned IPA packaging.
4. `scripts/add_widget_target.py` — Injects `MasareefWidgetExtension` (`.appex`) and `App Groups` (`group.com.alhawari.masareef`) into `App.xcodeproj`.
5. `ios-widget/MasareefWidget.swift` — SwiftUI Small & Medium widget with budget progress, remaining balance, shopping items count, and deep links.
6. `ios-widget/WidgetBridgePlugin.swift` — Syncs app state into shared `UserDefaults` and triggers `WidgetCenter`.
7. `www/index.html` — Full offline expense tracker, checklist, analytics, CSV/JSON export, and deep-link handler.

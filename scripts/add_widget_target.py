#!/usr/bin/env python3
import os
import sys
import uuid
import shutil

def gen_id():
    return uuid.uuid4().hex[:24].upper()

def main():
    if len(sys.argv) < 2:
        print("Usage: add_widget_target.py <path/to/App.xcodeproj>")
        sys.exit(1)

    xcodeproj_path = sys.argv[1]
    pbxproj_path = os.path.join(xcodeproj_path, "project.pbxproj")
    if not os.path.exists(pbxproj_path):
        print("project.pbxproj not found at:", pbxproj_path)
        sys.exit(1)

    with open(pbxproj_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "PBXCopyFilesPHASE" in content:
        content = content.replace("PBXCopyFilesPHASE", "PBXCopyFilesBuildPhase")

    if "MasareefWidgetExtension" in content:
        with open(pbxproj_path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Repaired and kept existing MasareefWidgetExtension target in", pbxproj_path)
        return

    project_root = os.path.dirname(xcodeproj_path)
    widget_dir = os.path.join(project_root, "MasareefWidgetExtension")
    os.makedirs(widget_dir, exist_ok=True)

    repo_root = os.path.abspath(os.path.join(project_root, "..", ".."))
    src_widget = os.path.join(repo_root, "ios-widget", "MasareefWidget.swift")
    dst_widget = os.path.join(widget_dir, "MasareefWidget.swift")
    if os.path.exists(src_widget):
        shutil.copyfile(src_widget, dst_widget)

    with open(os.path.join(widget_dir, "Info.plist"), "w", encoding="utf-8") as f:
        f.write('''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>NSExtension</key>
    <dict>
        <key>NSExtensionPointIdentifier</key>
        <string>com.apple.widgetkit-extension</string>
    </dict>
</dict>
</plist>
''')

    entitlements_content = '''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>com.apple.security.application-groups</key>
    <array>
        <string>group.com.alhawari.masareef</string>
    </array>
</dict>
</plist>
'''
    with open(os.path.join(widget_dir, "MasareefWidgetExtension.entitlements"), "w", encoding="utf-8") as f:
        f.write(entitlements_content)

    app_dir = os.path.join(project_root, "App")
    if os.path.isdir(app_dir):
        with open(os.path.join(app_dir, "App.entitlements"), "w", encoding="utf-8") as f:
            f.write(entitlements_content)

    swift_file_ref = gen_id()
    swift_build_file = gen_id()
    ext_product_ref = gen_id()
    ext_embed_build_file = gen_id()
    ext_target_id = gen_id()
    ext_sources_phase = gen_id()
    ext_frameworks_phase = gen_id()
    ext_resources_phase = gen_id()
    ext_group_id = gen_id()
    ext_build_cfg_list = gen_id()
    ext_debug_cfg = gen_id()
    ext_release_cfg = gen_id()

    file_ref_entries = [
        f'\t\t{swift_file_ref} /* MasareefWidget.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = MasareefWidget.swift; sourceTree = "<group>"; }};',
        f'\t\t{ext_product_ref} /* MasareefWidgetExtension.appex */ = {{isa = PBXFileReference; explicitFileType = "wrapper.app-extension"; includeInIndex = 0; path = MasareefWidgetExtension.appex; sourceTree = BUILT_PRODUCTS_DIR; }};',
    ]
    content = content.replace("/* End PBXFileReference section */", "\n".join(file_ref_entries) + "\n/* End PBXFileReference section */", 1)

    build_file_entries = [
        f'\t\t{swift_build_file} /* MasareefWidget.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {swift_file_ref} /* MasareefWidget.swift */; }};',
        f'\t\t{ext_embed_build_file} /* MasareefWidgetExtension.appex in Embed App Extensions */ = {{isa = PBXBuildFile; fileRef = {ext_product_ref} /* MasareefWidgetExtension.appex */; settings = {{ATTRIBUTES = (RemoveHeadersOnCopy, ); }}; }};',
    ]
    content = content.replace("/* End PBXBuildFile section */", "\n".join(build_file_entries) + "\n/* End PBXBuildFile section */", 1)

    group_block = f'''\t\t{ext_group_id} /* MasareefWidgetExtension */ = {{
\t\t\tisa = PBXGroup;
\t\t\tchildren = (
\t\t\t\t{swift_file_ref} /* MasareefWidget.swift */,
\t\t\t);
\t\t\tpath = MasareefWidgetExtension;
\t\t\tsourceTree = "<group>";
\t\t}};'''
    content = content.replace("/* End PBXGroup section */", group_block + "\n/* End PBXGroup section */", 1)

    main_group_match = None
    for line in content.splitlines():
        if "mainGroup =" in line:
            main_group_match = line.split("=")[1].strip().rstrip(";")
            break
    if main_group_match:
        target_str = f"{main_group_match} /* App */ = {{"
        idx = content.find(target_str)
        if idx != -1:
            ch_idx = content.find("children = (", idx)
            if ch_idx != -1:
                end_ch = content.find(");", ch_idx)
                content = content[:end_ch] + f"\n\t\t\t\t{ext_group_id} /* MasareefWidgetExtension */,\n\t\t\t" + content[end_ch:]

    embed_phase_id = gen_id()
    embed_phase_block = f'''\t\t{embed_phase_id} /* Embed App Extensions */ = {{
\t\t\tisa = PBXCopyFilesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tdstPath = "";
\t\t\tdstSubfolderSpec = 13;
\t\t\tfiles = (
\t\t\t\t{ext_embed_build_file} /* MasareefWidgetExtension.appex in Embed App Extensions */,
\t\t\t);
\t\t\tname = "Embed App Extensions";
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};'''
    if "/* End PBXCopyFilesBuildPhase section */" in content:
        content = content.replace("/* End PBXCopyFilesBuildPhase section */", embed_phase_block + "\n/* End PBXCopyFilesBuildPhase section */", 1)
    else:
        content = content.replace("/* End PBXBuildFile section */", "/* End PBXBuildFile section */\n\n/* Begin PBXCopyFilesBuildPhase section */\n" + embed_phase_block + "\n/* End PBXCopyFilesBuildPhase section */", 1)

    content = content.replace("/* End PBXSourcesBuildPhase section */", f'''\t\t{ext_sources_phase} /* Sources */ = {{
\t\t\tisa = PBXSourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t\t	{swift_build_file} /* MasareefWidget.swift in Sources */,
\t\t\t);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXSourcesBuildPhase section */''', 1)
    content = content.replace("/* End PBXFrameworksBuildPhase section */", f'''\t\t{ext_frameworks_phase} /* Frameworks */ = {{
\t\t\tisa = PBXFrameworksBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t	);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXFrameworksBuildPhase section */''', 1)
    content = content.replace("/* End PBXResourcesBuildPhase section */", f'''\t\t{ext_resources_phase} /* Resources */ = {{
\t\t\tisa = PBXResourcesBuildPhase;
\t\t\tbuildActionMask = 2147483647;
\t\t\tfiles = (
\t\t	);
\t\t\trunOnlyForDeploymentPostprocessing = 0;
\t\t}};
/* End PBXResourcesBuildPhase section */''', 1)

    common_settings = '''\t\t\t\t\tCODE_SIGN_STYLE = Manual;
\t\t\t\t\tCURRENT_PROJECT_VERSION = 1;
\t\t\t\t\tGENERATE_INFOPLIST_FILE = YES;
\t\t\t\t\tINFOPLIST_FILE = MasareefWidgetExtension/Info.plist;
\t\t\t\t\tCODE_SIGN_ENTITLEMENTS = MasareefWidgetExtension/MasareefWidgetExtension.entitlements;
\t\t\t\t\tIPHONEOS_DEPLOYMENT_TARGET = 17.0;
\t\t\t\t\tLD_RUNPATH_SEARCH_PATHS = (
\t\t\t\t\t\t"$(inherited)",
\t\t\t\t\t\t"@executable_path/Frameworks",
\t\t\t\t\t	"@executable_path/../../Frameworks",
\t\t\t\t\t);
\t\t\t\t\tMARKETING_VERSION = 1.0;
\t\t\t\t\tPRODUCT_BUNDLE_IDENTIFIER = com.alhawari.masareef.widget;
\t\t\t\t\tPRODUCT_NAME = "$(TARGET_NAME)";
\t\t\t\t\tSKIP_INSTALL = YES;
\t\t\t\t\tSWIFT_EMIT_LOC_STRINGS = YES;
\t\t\t\t\tSWIFT_VERSION = 5.0;
\t\t\t\t\tTARGETED_DEVICE_FAMILY = "1,2";'''

    cfg_block = f'''\t\t{ext_debug_cfg} /* Debug */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{common_settings}
\t\t\t}};
\t\t\tname = Debug;
\t\t}};
\t\t{ext_release_cfg} /* Release */ = {{
\t\t\tisa = XCBuildConfiguration;
\t\t\tbuildSettings = {{
{common_settings}
\t\t\t}};
\t\t\tname = Release;
\t\t}};'''
    content = content.replace("/* End XCBuildConfiguration section */", cfg_block + "\n/* End XCBuildConfiguration section */", 1)

    cfg_list_block = f'''\t\t{ext_build_cfg_list} /* Build configuration list for PBXNativeTarget "MasareefWidgetExtension" */ = {{
\t\t\tisa = XCConfigurationList;
\t\t\tbuildConfigurations = (
\t\t\t\t{ext_debug_cfg} /* Debug */,
\t\t\t\t{ext_release_cfg} /* Release */,
\t\t\t);
\t\t\tdefaultConfigurationIsVisible = 0;
\t\t\tdefaultConfigurationName = Release;
\t\t}};'''
    content = content.replace("/* End XCConfigurationList section */", cfg_list_block + "\n/* End XCConfigurationList section */", 1)

    native_target_block = f'''\t\t{ext_target_id} /* MasareefWidgetExtension */ = {{
\t\t\tisa = PBXNativeTarget;
\t\t\tbuildConfigurationList = {ext_build_cfg_list} /* Build configuration list for PBXNativeTarget "MasareefWidgetExtension" */;
\t\t\tbuildPhases = (
\t\t\t	{ext_sources_phase} /* Sources */,
\t\t\t	{ext_frameworks_phase} /* Frameworks */,
\t\t\t	{ext_resources_phase} /* Resources */,
\t\t\t);
\t\t\tbuildRules = (
\t\t\t);
\t\t\tdependencies = (
\t\t\t);
\t\t\tname = MasareefWidgetExtension;
\t\t\tproductName = MasareefWidgetExtension;
\t\t\tproductReference = {ext_product_ref} /* MasareefWidgetExtension.appex */;
\t\t\tproductType = "com.apple.product-type.app-extension";
\t\t}};'''
    content = content.replace("/* End PBXNativeTarget section */", native_target_block + "\n/* End PBXNativeTarget section */", 1)

    proj_targets_idx = content.find("targets = (")
    if proj_targets_idx != -1:
        end_t = content.find(");", proj_targets_idx)
        content = content[:end_t] + f"\n\t\t\t\t{ext_target_id} /* MasareefWidgetExtension */,\n\t\t\t" + content[end_t:]

    app_target_idx = content.find('name = App;')
    if app_target_idx != -1:
        phases_start = content.rfind("buildPhases = (", 0, app_target_idx)
        if phases_start != -1:
            phases_end = content.find(");", phases_start)
            content = content[:phases_end] + f"\n\t\t\t\t{embed_phase_id} /* Embed App Extensions */,\n\t\t\t" + content[phases_end:]

    with open(pbxproj_path, "w", encoding="utf-8") as f:
        f.write(content)

    print("Successfully injected MasareefWidgetExtension into", pbxproj_path)

if __name__ == "__main__":
    main()

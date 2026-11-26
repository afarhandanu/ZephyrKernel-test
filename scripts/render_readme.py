#!/usr/bin/env python3
"""Render README.md from README.template.md for the kernel version that was just built.

Called by the build workflows after a successful release, so README.md always
describes the most recently built version (6.1.190 or 6.1.193).
Edit README.template.md (shared text) or VERSIONS below, never README.md itself.
"""
import argparse
import pathlib
import sys

REPO = "https://github.com/afarhandanu/ZephyrKernel-test"

VERSIONS = {
    "6.1.190": {
        "workflow_file": "build-zephyr.yml",
        "base": "SAGA `upgrade-190-v2`",
        "tags": "`v6.1-<date>-...`",
        "intro_base": "Linux 6.1.190 LTS matching SAGA architecture.",
        "core_bullet": (
            "- **Upstream Linux 6.1.190 LTS Core:** Fully synced to upstream Linux 6.1.190 LTS "
            "with verified Android Common Kernel (ACK) fixups and MediaTek Dimensity 7300-Ultra / "
            "MT6878 compatibility (aligned with SAGA 190 architecture with `timer_delete_sync` "
            "and `DEFINE_FREE(fwnode_handle)` shims)."
        ),
    },
    "6.1.193": {
        "workflow_file": "build-zephyr-193.yml",
        "base": "Luminaire `android14-6.1-lts`",
        "tags": "`v6.1.193-<date>-...`",
        "intro_base": "Linux 6.1.193 LTS on the Luminaire `android14-6.1-lts` base.",
        "core_bullet": (
            "- **Upstream Linux 6.1.193 LTS Core:** Built on the Luminaire `android14-6.1-lts` tree, "
            "which merges upstream Linux 6.1.193 LTS into the Android Common Kernel, with the same "
            "Zephyr KMI fixes and addon patches applied on top as on 6.1.190."
        ),
    },
}


def version_table(current):
    rows = [
        "> [!NOTE]",
        "> **This page shows Linux %s, the version built most recently.** It is regenerated "
        "automatically by whichever build workflow ran last." % current,
        "",
        "| Version | Base source | Workflow | Release tags | |",
        "| :--- | :--- | :--- | :--- | :--- |",
    ]
    for ver, v in VERSIONS.items():
        mark = "**shown on this page**" if ver == current else ""
        rows.append(
            "| **%s** | %s | [`%s`](%s/actions/workflows/%s) | %s | %s |"
            % (ver, v["base"], v["workflow_file"], REPO, v["workflow_file"], v["tags"], mark)
        )
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True, choices=sorted(VERSIONS))
    ap.add_argument("--template", default="README.template.md")
    ap.add_argument("--output", default="README.md")
    args = ap.parse_args()

    v = VERSIONS[args.version]
    text = pathlib.Path(args.template).read_text(encoding="utf-8")
    for token, value in (
        ("{{VERSION_TABLE}}", version_table(args.version)),
        ("{{CORE_BULLET}}", v["core_bullet"]),
        ("{{INTRO_BASE}}", v["intro_base"]),
        ("{{WORKFLOW_FILE}}", v["workflow_file"]),
        ("{{KVER}}", args.version),
    ):
        if token not in text:
            sys.exit("render_readme: token %s missing from %s" % (token, args.template))
        text = text.replace(token, value)
    if "{{" in text:
        sys.exit("render_readme: unresolved token left in output")
    pathlib.Path(args.output).write_text(text, encoding="utf-8")
    print("README rendered for Linux %s -> %s" % (args.version, args.output))


if __name__ == "__main__":
    main()

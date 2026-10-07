"""Prepare a static site for the #34864 reproduction; does not publish it.

Run from a full clone containing both pinned commits:
    python3 demos/prepare_indirect_dispatch_demo.py /path/to/new/output-directory

The output contains unchanged src trees exported by git archive, their licenses,
the demo HTML, and a provenance manifest. No npm dependencies or CDN are needed.
Serve the output directory over HTTPS (or localhost for development), then open
/demos/indirect-dispatch-34864.html?version=baseline or ?version=fixed.
"""

import hashlib
import json
from pathlib import Path
import subprocess
import sys


VERSIONS = {
    "baseline": "7c419ddae99fe0f666b509072fcf47e2017542e7",
    "fixed": "910d28874b5ee1cdfa99f21e39c9124a327c629c",
}


def prepare(destination):
    root = Path(__file__).resolve().parents[1]
    output = Path(destination).resolve()
    if output.exists():
        raise SystemExit(f"Refusing to overwrite existing output: {output}")

    # Verify both objects before creating any output; a shallow clone may lack them.
    for sha in VERSIONS.values():
        subprocess.run(["git", "-C", str(root), "cat-file", "-e", f"{sha}^{{commit}}"], check=True)

    html = (root / "demos/indirect-dispatch-34864.html").read_bytes()
    for sha in VERSIONS.values():
        if sha.encode() not in html:
            raise SystemExit("The HTML and source commit pins do not match")

    (output / "demos").mkdir(parents=True)
    (output / "demos/indirect-dispatch-34864.html").write_bytes(html)
    (output / ".nojekyll").touch()
    manifest = {"htmlSHA256": hashlib.sha256(html).hexdigest(), "versions": {}}

    for version, sha in VERSIONS.items():
        target = output / "demos/indirect-dispatch-34864" / version
        target.mkdir(parents=True)
        archive = subprocess.run(
            ["git", "-C", str(root), "archive", "--format=tar", sha, "src", "LICENSE"],
            check=True, capture_output=True,
        ).stdout
        subprocess.run(["tar", "-xf", "-", "-C", str(target)], input=archive, check=True)
        backend = (target / "src/renderers/webgpu/WebGPUBackend.js").read_bytes()
        manifest["versions"][version] = {
            "commit": sha,
            "archiveSHA256": hashlib.sha256(archive).hexdigest(),
            "backendSHA256": hashlib.sha256(backend).hexdigest(),
            "sourceFiles": len(list((target / "src").rglob("*.js"))),
        }

    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"output": str(output), **manifest}, indent=2))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: prepare_indirect_dispatch_demo.py NEW_OUTPUT_DIRECTORY")
    prepare(sys.argv[1])

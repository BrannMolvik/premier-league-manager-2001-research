"""Build and audit a deterministic source snapshot for the exact Gate-17 FFmpeg commit."""
from __future__ import annotations
import argparse, hashlib, json, subprocess, tempfile
from pathlib import Path
from gate17_ffmpeg_minimal_source_contract import CONTRACT_PATH, audit_source_contract

class FfmpegSourceSnapshotError(RuntimeError): pass

def _sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def _load(root: Path) -> dict:
    return json.loads((root/CONTRACT_PATH).read_text(encoding="utf-8"))

def audit_snapshot_contract(repo_root: str|Path) -> dict:
    root=Path(repo_root); audit_source_contract(root)
    s=_load(root)["minimal_helper_target"].get("source_snapshot")
    if not isinstance(s,dict): raise FfmpegSourceSnapshotError("source_snapshot contract is missing")
    if s.get("assembled") is not True or s.get("hashes_pinned") is not True:
        raise FfmpegSourceSnapshotError("reviewed source snapshot must be assembled and hash-pinned")
    for k in ("source_material_complete","legal_compliance_claimed"):
        if s.get(k) is not False: raise FfmpegSourceSnapshotError(f"{k} must remain false")
    if s.get("archive_format")!="tar.xz": raise FfmpegSourceSnapshotError("source snapshot archive format drifted")
    for key in ("archive_sha256","license_sha256","build_recipe_manifest_sha256"):
        value=s.get(key)
        if not isinstance(value,str) or len(value)!=64: raise FfmpegSourceSnapshotError(f"{key} is not pinned")
    for key in ("archive_size_bytes","license_size_bytes","build_recipe_manifest_size_bytes"):
        if not isinstance(s.get(key),int) or s[key]<=0: raise FfmpegSourceSnapshotError(f"{key} is not pinned")
    return {"passed":True,"assembled":True,"hashes_pinned":True,"source_material_complete":False,"legal_compliance_claimed":False}

def build_snapshot(*, repo_root: str|Path, ffmpeg_source: str|Path, output_dir: str|Path) -> dict:
    root=Path(repo_root); source=Path(ffmpeg_source); out=Path(output_dir)
    audit_snapshot_contract(root)
    target=_load(root)["minimal_helper_target"]; snap=target["source_snapshot"]; commit=target["source_commit"]
    actual=subprocess.check_output(["git","-C",str(source),"rev-parse","HEAD"],text=True).strip()
    if actual!=commit: raise FfmpegSourceSnapshotError(f"FFmpeg source commit drifted: {actual} != {commit}")
    if subprocess.check_output(["git","-C",str(source),"status","--porcelain"],text=True).strip():
        raise FfmpegSourceSnapshotError("FFmpeg source checkout is not clean")
    lic=source/target["license_file"]
    if not lic.is_file(): raise FfmpegSourceSnapshotError("pinned FFmpeg license file is missing")
    out.mkdir(parents=True,exist_ok=True)
    archive=out/snap["archive_filename"]
    with tempfile.TemporaryDirectory() as td:
        tar=Path(td)/"src.tar"
        with tar.open("wb") as fh:
            subprocess.run(["git","-C",str(source),"archive","--format=tar",f"--prefix=FFmpeg-{commit}/","HEAD"],stdout=fh,check=True)
        with archive.open("wb") as fh:
            subprocess.run(["xz","-9e","--threads=1","--check=crc64","-c",str(tar)],stdout=fh,check=True)
    recipe={"schema_version":1,"source_repository":target["source_repository"],"source_commit":commit,"configure_args":target["configure_args"],"license_file":target["license_file"],"archive_filename":archive.name}
    recipe_path=out/"build-recipe-manifest.json"; recipe_path.write_text(json.dumps(recipe,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    lic_copy=out/target["license_file"]; lic_copy.write_bytes(lic.read_bytes())
    receipt={"schema_version":1,"passed":True,"source_commit":commit,"archive_filename":archive.name,"archive_sha256":_sha(archive),"archive_size_bytes":archive.stat().st_size,"license_sha256":_sha(lic_copy),"license_size_bytes":lic_copy.stat().st_size,"build_recipe_manifest_sha256":_sha(recipe_path),"build_recipe_manifest_size_bytes":recipe_path.stat().st_size,"assembled":True,"hashes_pinned":True,"source_material_complete":False,"legal_compliance_claimed":False}
    for key in ("archive_sha256","archive_size_bytes","license_sha256","license_size_bytes","build_recipe_manifest_sha256","build_recipe_manifest_size_bytes"):
        if receipt[key] != snap[key]:
            raise FfmpegSourceSnapshotError(f"{key} drifted: {receipt[key]} != {snap[key]}")
    (out/"ffmpeg-source-snapshot-manifest.json").write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return receipt

def main():
    p=argparse.ArgumentParser(); p.add_argument("--repo-root",default="."); p.add_argument("--ffmpeg-source"); p.add_argument("--output-dir",required=True); p.add_argument("--preflight-only",action="store_true"); a=p.parse_args()
    r=audit_snapshot_contract(a.repo_root) if a.preflight_only else build_snapshot(repo_root=a.repo_root,ffmpeg_source=a.ffmpeg_source,output_dir=a.output_dir)
    print(json.dumps(r,indent=2,sort_keys=True)); return 0
if __name__=="__main__": raise SystemExit(main())

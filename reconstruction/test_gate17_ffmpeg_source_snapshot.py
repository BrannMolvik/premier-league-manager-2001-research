from pathlib import Path
import json,tempfile,unittest
from gate17_ffmpeg_source_snapshot import FfmpegSourceSnapshotError,audit_snapshot_contract
from gate17_ffmpeg_minimal_source_contract import CONTRACT_PATH
class T(unittest.TestCase):
 def test_real_contract(self):
  r=audit_snapshot_contract(Path(__file__).resolve().parents[1]); self.assertTrue(r["passed"]); self.assertTrue(r["assembled"]); self.assertTrue(r["hashes_pinned"]); self.assertFalse(r["source_material_complete"])
 def test_no_self_promotion(self):
  root=Path(__file__).resolve().parents[1]; p=json.loads((root/CONTRACT_PATH).read_text()); p["minimal_helper_target"]["source_snapshot"]["archive_sha256"]="0"*64
  with tempfile.TemporaryDirectory() as td:
   q=Path(td)/CONTRACT_PATH; q.parent.mkdir(parents=True); q.write_text(json.dumps(p))
   with self.assertRaises(FfmpegSourceSnapshotError): audit_snapshot_contract(td)
if __name__=="__main__": unittest.main()

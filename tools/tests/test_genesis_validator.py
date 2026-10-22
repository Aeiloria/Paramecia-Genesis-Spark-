import copy
import json
import unittest
from pathlib import Path
from genesis_spark.validator import validate, report, digest

SAMPLE = json.loads((Path(__file__).resolve().parents[1] / "fixtures/genesis-spark-draft.json").read_text())

class ValidatorTests(unittest.TestCase):
    def test_valid_example(self): self.assertEqual(validate(SAMPLE), [])
    def test_duplicate_id_fails(self): self.assertTrue(any('duplicate ID' in e for e in validate(SAMPLE*2)))
    def test_missing_provenance_fails(self):
        r=copy.deepcopy(SAMPLE);r[0]['source_refs']=[]
        self.assertTrue(any('source_refs' in e for e in validate(r)))
    def test_approval_evidence_required(self):
        r=copy.deepcopy(SAMPLE);r[0]['status']='approved'
        self.assertTrue(any('approval' in e for e in validate(r)))
    def test_seed_is_not_element_zero(self):
        r=copy.deepcopy(SAMPLE);r[0]['atomic_number']=0
        self.assertTrue(any('must not have atomic_number' in e for e in validate(r)))
    def test_reproducible(self):
        self.assertEqual(report(SAMPLE),report(copy.deepcopy(SAMPLE)))
        self.assertEqual(digest(SAMPLE),digest(copy.deepcopy(SAMPLE)))
    def test_full_elements_fails_on_draft(self):
        self.assertTrue(any('periodic table incomplete' in e for e in validate(SAMPLE, require_full_periodic_table=True)))
    def test_quarantine_cannot_claim_approval(self):
        r=copy.deepcopy(SAMPLE);r[0]['status']='quarantined';r[0]['approved_by']='unverified agent'
        self.assertTrue(any('quarantined content' in e for e in validate(r)))

if __name__=='__main__': unittest.main()

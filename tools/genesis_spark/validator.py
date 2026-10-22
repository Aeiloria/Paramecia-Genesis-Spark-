"""Read-only validation and deterministic report generation. No canon writes."""
import hashlib
import json
from pathlib import Path

STATUSES = {"draft", "experimental", "review", "approved", "quarantined", "retired"}
DOMAINS = {"fiction", "scientific_reference", "hypothesis", "simulation"}
REQUIRED = {"id", "record_type", "title", "description", "status", "domain", "source_refs", "created_at", "updated_at", "version", "change_reason", "approved_by", "approval_ref", "tests"}


def validate(records, *, require_full_periodic_table=False):
    errors, seen, elements = [], set(), set()
    if not isinstance(records, list):
        return ["Root must be a list of records"]
    for i, r in enumerate(records):
        prefix = f"records[{i}]"
        if not isinstance(r, dict):
            errors.append(f"{prefix}: must be an object")
            continue
        missing = REQUIRED - r.keys()
        if missing:
            errors.append(f"{prefix}: missing fields {', '.join(sorted(missing))}")
        rid = r.get("id")
        if not isinstance(rid, str) or not rid.strip():
            errors.append(f"{prefix}: invalid ID")
        elif rid in seen:
            errors.append(f"{prefix}: duplicate ID {rid}")
        else:
            seen.add(rid)
        if r.get("status") not in STATUSES:
            errors.append(f"{prefix}: invalid status")
        if r.get("domain") not in DOMAINS:
            errors.append(f"{prefix}: invalid domain")
        refs = r.get("source_refs")
        if not isinstance(refs, list) or not refs or any(not isinstance(x,str) or not x.strip() for x in refs):
            errors.append(f"{prefix}: source_refs must be nonempty string list")
        if r.get("status") == "approved" and (not r.get("approved_by") or not r.get("approval_ref")):
            errors.append(f"{prefix}: approved record requires reviewer and approval reference")
        if r.get("status") == "quarantined" and r.get("approved_by"):
            errors.append(f"{prefix}: quarantined content cannot claim current approval")
        if r.get("record_type") == "element":
            n = r.get("atomic_number")
            if type(n) is not int or not 1 <= n <= 118:
                errors.append(f"{prefix}: atomic_number must be integer 1..118")
            elif n in elements:
                errors.append(f"{prefix}: duplicate atomic_number {n}")
            else:
                elements.add(n)
            if not isinstance(r.get("standard_symbol"),str) or not r["standard_symbol"].strip():
                errors.append(f"{prefix}: missing standard_symbol")
        if r.get("record_type") == "seed" and "atomic_number" in r:
            errors.append(f"{prefix}: fictional seed must not have atomic_number")
    if require_full_periodic_table and elements != set(range(1,119)):
        errors.append(f"periodic table incomplete: {118-len(elements)} missing")
    return errors


def canonical_json(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def digest(value):
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def report(records):
    errors = validate(records)
    statuses = {s: sum(r.get("status") == s for r in records if isinstance(r,dict)) for s in sorted(STATUSES)}
    return "# Genesis Spark validation report\n\n" + f"Input SHA-256: `{digest(records)}`\n\n" + f"Validation: {'FAILED' if errors else 'PASSED'}\n\n" + "Statuses: " + ", ".join(f"{k}={v}" for k,v in statuses.items()) + "\n\n" + ("Errors:\n" + "\n".join(f"- {e}" for e in errors) if errors else "No validation errors.") + "\n"


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("data", type=Path)
    p.add_argument("--full-elements", action="store_true")
    p.add_argument("--report", type=Path)
    args = p.parse_args()
    records = json.loads(args.data.read_text(encoding="utf-8"))
    errors = validate(records, require_full_periodic_table=args.full_elements)
    output = report(records)
    if args.report:
        args.report.write_text(output, encoding="utf-8")
    print(output)
    raise SystemExit(1 if errors else 0)

if __name__ == "__main__":
    main()

# Genesis Spark v2 validator (draft / not canon)

This isolated Python tool reads JSON and emits deterministic Markdown. It does not edit original data, approve records, or change the TypeScript application.

Run from repository root:

```sh
cd tools
python -m unittest discover -s tests -v
python -m genesis_spark.validator fixtures/genesis-spark-draft.json --report genesis-validation-report.md
python -m genesis_spark.validator fixtures/genesis-spark-draft.json --full-elements
```

The last command is **expected to fail**, because the example is not a verified 118-element import.

The approval fields are checked for presence only, not for human identity or signature validity. Source references are not resolved. Simulation, provenance authenticity, deployment, CI verification and the complete element import are out of scope.

The draft sample is not an approved canon record. The zero-point fictional seed is not element zero. Original sources and approved canon remain unchanged.

[Upgrade specification](https://docs.google.com/document/d/1uMRQtLZj5s9MmQNGqRYuvl7_B8H2TvykZh2m-yUSCK8/edit)

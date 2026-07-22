# Evidence Provenance

## Evidence classes

- Local raw evidence: external, untracked, immutable preservation; not Published Evidence
- Published Evidence: tracked, sanitized and derived from reviewed raw records
- Composite Discovery Evidence v1: the J1.4 Phase A record plus the final supplemental record

## Local preservation manifest

- Manifest SHA256: `ed7acc2296dc1c76eb4e8231907570d17551e71b30cfbc7b56cb8113562870cb`
- Manifest validation: all records `OK`
- Superseded records: preserved and non-authoritative

## Authoritative logical records

| Logical record | SHA256 |
|---|---|
| J1.1 acceptance | `39d78160126e1e7ddc77743d517e0600dfda89e9c6ea5c07125e62911bb20f1c` |
| J1.2 inventory | `5fa41376c4bb9c379727202cfc69a224d74b0730904cbdcac31c98ed7662643e` |
| J1.3 Phase A | `f40718389908357fe9decf1807560d3a0257875e6a128daff4510e988e94e2477` |
| J1.3 Phase B | `b71d72b9be97bfb6aa62b9a70cfcef76cf6853164cd9bf7ae68f194c1ba432a0` |
| J1.4 Phase A | `91eb86daebd31a96e6ddc74b9beda89c7aa466e7d74f0da53a0ea291689f99a0` |
| J1.4 supplemental | `75cb07a6149b6b69b3774397ee58bd754743aa7df9181f86d9749833d17732a5` |

## Superseded logical records

The following are retained but are not final authority:

- J1.2 superseded: `37a34059d288dd368e310e41c78e0884d9c8678624b3b1ce1b5f187c1fe42416`
- J1.4 supplemental superseded: `36fbac1111ace37cbcb4b1d299c2b61beec32da6d8a546f9e864dde188dde92b`
- J1.4 supplemental superseded: `0b558351e4c36329c96d81d55e841b82831c4cecca72ec8e8a2b628af4151bfa`

## Source provenance

- Plan SHA256: `a723ae1ffae70366c7435313869f5a2ec1318c47ed43398ffdfcf40e8ba6a9bd`
- Task Cards SHA256: `01d4862ad4d7cb59d8f1834f39de8f29c960868ac9b9732773ef0f7d65d3956c`
- Inventory SHA256: `9a25ee9cda5bf264394c53f2910d295ef9b621b6ab0a555e28fe993c42f82868`
- Decisions: D041 Accepted, D042 Accepted, D043 Accepted
- Current source HEAD: `98038f74a4341ae761b3be8a606af66492e50ff7`

Published Evidence contains no raw output, local absolute path, credential,
network identifier, serial, UUID or private-key path.

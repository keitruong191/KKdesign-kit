# Implementation plan: PROTO-01 — DS-first interactive prototypes

## Status and scope

- DESIGN-SPEC và TEST-SPEC đã được chủ sở hữu duyệt ngày 2026-11-11.
- Plan đã **implemented — local acceptance complete; native acceptance partial**. Core pass 165 unittest; package relocation, actual CLI lifecycle và HTML/React/token-only-iOS browser walkthrough đã kiểm chứng. Native routing/helper/build chỉ pass trong phạm vi đã chạy; native browser/Figma còn pending và scope failures được ghi rõ tại [acceptance/INTEGRATION.md](acceptance/INTEGRATION.md). Không claim full feature hoặc human design approval.
- Một route prototype, ba đích Figma/HTML/React; mọi đích bám DS đã init. Mục tiêu là truyền đạt flow feature PM/PO trong ngữ cảnh app hiện tại, không API/backend hoặc kiến trúc production.
- Không tự commit, đổi branch, publish/deploy hoặc cài dependency/tool mới ngoài quyền đã có.

## Artifacts

- [plan.json](plan.json): canonical machine-readable plan, đầy đủ behavior, test cases và edge-case input/expected cho fresh-context workers.
- [DESIGN-SPEC.md](DESIGN-SPEC.md), [TEST-SPEC.md](TEST-SPEC.md): approved baseline và verification contract.
- [CONTEXT.md](CONTEXT.md), [RESEARCH.md](RESEARCH.md): quyết định, scope và bằng chứng repo.

CLI prepare yêu cầu absolute workspace/file paths, trong khi repository không được chứa đường dẫn máy tác giả. Vì vậy canonical plan dùng **synthetic anchor `/workspace/kkdesign-kit`**, không phải vị trí chạy thật. Không chạy cook/context pack trực tiếp với anchor này.

Bản thực thi đã bind vào checkout hiện tại nằm ở `.kkdesign-kit/planning/ds-interactive-prototype/plan.json`, cùng local copies của approved specs và per-task context packs. `.kkdesign-kit/` đã được gitignore trước task này; các machine-bound files không phải tài liệu public/committed. Nếu đổi checkout hoặc di chuyển repo, rebind `workspace_dir`, `files` và `context_pointers` từ canonical anchor sang workspace mới, rồi regenerate context packs và validate lại. Các field behavior/tests/edges/dependency không được thay đổi khi rebind.

## Execution waves

Một owner cho từng file; các task trong cùng wave không có shared write target. `depends_on` trong JSON là nguồn chuẩn cho scheduler, không dùng wave làm barrier cứng khi một nhánh external đang pending.

| Wave | Tasks | Outcome |
|---|---|---|
| 1 | `proto-01` schema; `proto-04` web execution guide; `proto-05` shared routing/docs/manifest; `proto-06` synthetic token/spec/context/reference inputs | Chốt contract và chuẩn bị nguồn workflow/fixture, chưa claim demo đã chạy |
| 2 | `proto-02` shared core artifact validator/foundation; `proto-07` synthetic React DS components/theme | Validator dùng chung và DS code fixture, không thêm generator/runtime provisioning |
| 3 | `proto-03` task begin/check/handoff integration; `proto-09` artifact path/schema regression | Helper lifecycle và boundary checks không phụ thuộc frame link giả |
| 4 | `proto-08` profile/lesson/preflight regression; `proto-10` handoff và CLI lifecycle integration regression | Behavioral tests riêng file, không tranh ownership hoặc pin prose |
| 5 | `proto-11` integrated core regression + extracted/relocated package smoke | Local integrity gate trước nghiệm thu flow |
| 6 | `proto-12` HTML browser; `proto-13` React/component reuse browser; `proto-14` React token-only/ios/DS gaps; `proto-15` native harness/Figma acceptance | Bằng chứng tách theo surface, các demo dùng project/output riêng |
| 7 | `proto-16` integration review và acceptance report | Đối chiếu requirements/AC, local evidence và phần native còn pending |

`proto-16` phụ thuộc `proto-11/12/13/14`, **không phụ thuộc `proto-15`**. Không giữ local review/tích hợp code đã kiểm chứng để chờ tài khoản hoặc Figma tool; cũng không gọi pending native acceptance là pass.

## Shared interfaces and ownership

- `proto-01` chỉ sửa task schema; không thay default template/schemaVersion hoặc rewrite lịch sử.
- `proto-02` sở hữu `scripts/kkdesign_core.py`: shared `_validate_web_artifacts(project, task, require_delivery=False)` và foundation integration. `proto-03` sở hữu task helper và import core theo chiều đang có; không tạo import cycle hoặc hai bộ path rules.
- `proto-04` chỉ viết web guide; `proto-05` là owner các guide hiện có, routing, capability docs và manifest. Installer đã bundle recursive references/examples, không cần sửa lifecycle/installer.
- `proto-06` tạo đầu vào DS/product/brief/reference, không tạo app feature làm sẵn. `proto-07` chỉ thêm code component/theme synthetic; prototype nghiệm thu phải do agent dựng từ các đầu vào đó.
- Planning refinement: đặt regression mới trong `tests/test_prototype_preflight.py`, `tests/test_prototype_paths.py` và `tests/test_prototype_handoff.py` để các test owner độc lập. Spec affected-files và verify commands đã được cập nhật tương ứng; requirements, expected outcomes và scope không đổi. Giữ tests Figma/foundation/installation hiện có và chạy full suite.
- Source/artifact app ở `design/prototypes/<taskId>` của selected project; task/evidence ở `design/tasks/<taskId>`. Không để package.json dưới task directory.
- Refinement từ defect đã reproduce: thêm `scripts/kkdesign_project.py` và `tests/test_project.py` để React artifact/dependency không phá refresh/candidate validation; vẫn kiểm integrity artifact thật và không thêm provisioning/lifecycle feature. Thêm web artifact-root scan vào `scripts/smoke_workflow_harness.py`. Bằng chứng và phạm vi tại `acceptance/local-integrity.md`.

## Verification gates

### Planning gates — chạy trước khi bàn giao plan

```sh
hoangsa-cli validate spec .hoangsa/sessions/docs/ds-interactive-prototype/DESIGN-SPEC.md
hoangsa-cli validate tests .hoangsa/sessions/docs/ds-interactive-prototype/TEST-SPEC.md
hoangsa-cli validate plan .hoangsa/sessions/docs/ds-interactive-prototype/plan.json --tests .hoangsa/sessions/docs/ds-interactive-prototype/TEST-SPEC.md
hoangsa-cli validate plan .kkdesign-kit/planning/ds-interactive-prototype/plan.json --tests .hoangsa/sessions/docs/ds-interactive-prototype/TEST-SPEC.md
hoangsa-cli dag check .kkdesign-kit/planning/ds-interactive-prototype/plan.json
hoangsa-cli dag waves .kkdesign-kit/planning/ds-interactive-prototype/plan.json
```

Mỗi task được kiểm bằng `budget estimate` và có context pack local. Pack được tạo trước implementation nên files tương lai có thể chưa có body; cook phải regenerate pack sau khi các producer dependency hoàn thành, không dùng stale offsets như bằng chứng đã đọc source mới.

### Implementation gates — chưa chạy ở lượt lập plan

1. Không build/lint/test/format trong lúc implementation owners còn edit. Sau tích hợp code và tests, `proto-11` chạy `python3 -B -m unittest discover -s tests -v` và package/extract/verify smoke thật.
2. Browser tasks phải launch artifact, thao tác success/error/retry/back/cancel/reset, đối chiếu DS và capture evidence theo TEST-SPEC. Shell acceptance `kkdesign_task check` hoặc `kkdesign_core validate` **chỉ kiểm integrity**, không đủ để hoàn thành UI acceptance.
3. React thử cả reuse component code và token/spec-only. Profile ios giữ nguyên product platform; browser demo không phải native ios behavior.
4. Native Codex/Claude/Figma chạy khi có capability/quyền phù hợp. Thiếu resource: report từng mục `PENDING`, prerequisites và bước tiếp theo; không auto login/provision, không giữ worker chờ external approval.
5. Regression/observed defects gửi về file owner; rerun checks bị ảnh hưởng sau sửa, không sửa test để pin incidental behavior.

## Completion and evidence

Các report execution sau đã được tạo từ quan sát thật, không phải pass placeholders:

- `acceptance/local-integrity.md`: actual core/package commands và kết quả.
- `acceptance/html-browser.md`, `acceptance/react-browser.md`: flow/reset/render/DS evidence.
- `acceptance/ds-platform.md`: token-only/profile/coverage limitations.
- `acceptance/native-harness-figma.md`: từng native surface pass/pending và prerequisite.
- `acceptance/INTEGRATION.md`: requirement/AC mapping, review findings, local/native disposition.

Raw transcript/screenshots/private product evidence thuộc selected acceptance project, không đưa vào public examples. Chỉ đưa synthetic, portable evidence vào repo; không credentials, private IDs, local machine paths hoặc dependency/vendor binaries.

Hoàn thành plan không đồng nghĩa hoàn thành feature. Full feature acceptance chỉ đạt khi evidence tương ứng có thật; external acceptance pending vẫn phải được giữ rõ khi local code được review/tích hợp.

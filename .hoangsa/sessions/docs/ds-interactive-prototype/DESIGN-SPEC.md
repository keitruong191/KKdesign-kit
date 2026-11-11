---
spec_version: "1.0"
project: "KKdesign-kit"
component: "ds_interactive_prototype"
language: "Python 3.9+, Markdown, HTML/CSS/JavaScript, React"
task_type: "feat"
category: "code"
status: "approved"
approved_on: "2026-11-11"
---

## Overview

### Goal

Từ mong muốn PM/PO và DS đã init, KKdesign-kit dựng prototype tương tác HTML hoặc React đủ sát app hiện tại để dev, team và stakeholders hiểu và thảo luận flow feature mới; giữ lựa chọn Figma.

### Context

Nguồn yêu cầu: [BACKLOG.md](BACKLOG.md), PROTO-01. Quyết định sản phẩm được lưu ở [CONTEXT.md](CONTEXT.md); bằng chứng contract hiện tại ở [RESEARCH.md](RESEARCH.md). Chủ sở hữu đã duyệt DESIGN-SPEC và TEST-SPEC để lập kế hoạch triển khai; approval này không chứng minh feature đã được triển khai hoặc nghiệm thu.

Khác biệt là **project DS-first, không phụ thuộc đích dựng**. Tương tác phục vụ câu chuyện demo; không coi API thật, backend fidelity hoặc code production-ready là điều kiện nghiệm thu.

### Requirements

| ID | Requirement | Backlog |
|---|---|---|
| [REQ-01] | Route prototype explicit hỗ trợ Figma, HTML và React; không sinh interaction trong design/review | AC-01 |
| [REQ-02] | Ghi brief, flow, entry/end, scenario, state và exclusions trước mutation | AC-02 |
| [REQ-03] | Dùng DS đã init và giữ truy nguyên component/token; code library không bắt buộc | AC-03 |
| [REQ-04] | Demo nhận diện đúng app theo DS/reference trong scope, có scoped exceptions | AC-04 |
| [REQ-05] | Flow và phản hồi chạy được trong browser bằng local state/dữ liệu mô phỏng | AC-05 |
| [REQ-06] | Reset và các hành vi back/cancel/data retention nhất quán theo brief | AC-06 |
| [REQ-07] | Kiểm chứng flow lẫn render thực, evidence trung thực và đúng phạm vi | AC-07 |
| [REQ-08] | Artifact-aware handoff có entry, launch instructions, demo script và giới hạn | AC-08 |
| [REQ-09] | Bảo toàn project/skill ownership, quyền publish và dữ liệu; không gọi dịch vụ thật mặc định | AC-09 |
| [REQ-10] | Routing/docs/contracts dùng chung hai harness, dependency theo target, bảo toàn Figma | AC-10 |

### Out of Scope

Backend/database/auth/API thật; production architecture/readiness; Figma-to-code compiler hoặc sync hai chiều; universal renderer/token compiler; coverage ngoài brief; hosting/deploy/analytics; thay DS hoặc bỏ Figma; tự cài browser/harness/tool; đo/cam kết tiết kiệm chưa kiểm chứng. Không thêm CLI code generator, workflow riêng theo provider hoặc vòng retry/telemetry mới.

## Types / Data Models

### Reuse shared task contract

Không tạo schema family mới. Giữ `kind=design-task`, lifecycle status, objective, productProfileId, lessonReview, designPlan, evidence wrappers và schemaVersion hiện có.

| Field | Web contract đề xuất | Responsibility |
|---|---|---|
| `delivery` | `html_prototype` hoặc `react_prototype`, chọn explicit | Helper phân nhánh web gate bằng đúng hai giá trị này; delivery khác giữ semantics hiện có |
| `platform` | Platform sản phẩm/profile hiện có, kể cả ios/android/macos/adaptive | Không đổi thành web chỉ vì browser là nơi demo |
| `target.destination` | Project-relative directory `design/prototypes/<taskId>` | Begin validate lexical path/ownership; directory chưa cần tồn tại |
| `flows` | Danh sách flow có ID, entry/end và các action/state liên quan | Agent record brief, không phải executable graph/DSL |
| `states.required`, `states.notApplicable` | Trạng thái trong scope và exclusions có lý do | Giữ preflight hiện có |
| `acceptanceCriteria` | Tiêu chí demo có ID để map scenario/evidence | Agent thực hiện và record observation |
| `sourceDecisions` | Các DS mapping record mô tả bên dưới | Provenance, không phải chứng nhận conformance tự động |
| `designPlan` | Giữ layoutDecisions/stateDispositions/referenceExamples và field khác | Decisions cho cả cấu trúc sản phẩm lẫn cách thể hiện browser |
| `exceptions`, `openQuestions` | Scope, lý do, tác động và disposition | Không bịa component/token thiếu hoặc yêu cầu sản phẩm |

DS mapping record trong `sourceDecisions` gồm `surface`, `sourceId`, `assetIds`, `revisionOrHash`, `implementation` (`reuse-code` hoặc `recreated`), `codeReference` nếu có và `notes`. SourceId/assetIds phải trỏ về nguồn project thực; nếu một chi tiết chưa có source, ghi gap trong exceptions, không đặt ID giả. Không yêu cầu mapping từng CSS declaration; record các component/token/variant quan trọng phục vụ review. Đây là hướng dẫn nội dung record, không thêm registry hoặc compiler thứ hai.

### Web handoff extension

Giữ các field handoff chung: `frameLinks`, `createdNodeIds`, `modifiedNodeIds`, `checks`, `remainingGaps`, `requirementStateMapping`. Với web, ba field canvas là mảng rỗng hợp lệ, không tạo node ID/link giả.

Thêm `handoff.artifacts`: mảng không rỗng khi bàn giao web, mỗi item có:

| Field | Type / rule |
|---|---|
| `entry` | Nonempty project-relative path tới file entry thật dưới target.destination; HTML là HTML entry, React là source entry của app đã chạy |
| `instructions` | Nonempty project-relative path tới README chạy/demo thật dưới target.destination |
| `launch.mode` | `file` hoặc `command`; React phải là command |
| `launch.cwd` | Project-relative directory tồn tại nếu mode=command, có thể là `.` khi reuse app runtime |
| `launch.argv` | Mảng string không rỗng nếu mode=command; metadata để người/agent có quyền thực thi riêng, helper không execute |

Tất cả path artifact và cwd có base là **project root**; evidence references tiếp tục có base là **task directory**. Entry/instructions phải nằm trong target artifact root và project, không qua symlink. Cwd chỉ được nằm trong project, không qua symlink. Không chấp nhận URL, absolute path hoặc lexical traversal `..` ở artifact/cwd fields. Không dùng tên renderer làm bằng chứng file đã render.

Schema bổ sung mô tả/typing cho delivery web, target.destination và handoff.artifacts có điều kiện; shared template vẫn pending, delivery mặc định hiện có không đổi. Các task/profile/lesson/evidence lịch sử không bị rewrite hoặc restamp. Task web mới thiếu field phải sửa record; không có alias/shim cho payload web chưa hoàn chỉnh.

### Output layout

```text
design/
  tasks/<taskId>/
    task.json
    evidence-0001.json
    captures/...
  prototypes/<taskId>/
    README.md
    index.html, styles.css, script.js       (HTML; có thể gộp file nếu phù hợp)
    package.json, source entry, ...        (React standalone khi cần)
```

Đây là layout theo target, không yêu cầu tạo cả HTML và React trong một task. App/package JSON không nằm trong design/tasks: validator hiện phân loại JSON tại đó là task/evidence. Khi reuse build/runtime project, source demo vẫn nằm dưới artifact root; cwd/launch có thể dùng môi trường project nếu chạy được mà không sửa cấu hình ngoài scope. Nếu không dùng được như vậy, dựng React app riêng trong artifact root hoặc ghi blocker; không âm thầm sửa app chính.

## Interfaces / APIs

### Skill invocation — agent interface, không phải parser CLI mới

- Codex: `$kkdesign-kit prototype` + brief nói rõ đầu ra Figma/HTML/React.
- Claude Code: `/kkdesign-kit prototype` + cùng brief.
- Không có flag `--target` mới được giả nhận là hiện có. Nếu brief chưa chọn đầu ra và context không giải quyết được, hỏi một câu với ba lựa chọn; không mặc định Figma/React hoặc sinh cả hai.

### Python helper — giữ command/signature công khai

Các API hiện có tiếp tục là entry points, không thêm executable generator:

```python
def begin(project, record_file): ...
def add_evidence(project, task_id, evidence_type, description, payload_file,
                 references, historical_status='historical'): ...
def check_task(project, task_id): ...
def update_handoff(project, task_id, handoff_file, status): ...
```

Phần thân cần thay đổi: nhận diện hai delivery web; validate artifact root trước record; validate web artifact references khi check/handoff; delivered web gate dùng artifacts thay frameLinks. Giữ exception/error channel và status hiện có. `blockedDisposition` không được dùng để bypass thiếu artifact của delivered web; task web bị block giữ `in_progress`.

Schema/foundation/task helper dùng chung một định nghĩa field và cùng quy tắc path. Có thể factor validator nội bộ dùng lại, nhưng không thêm abstraction ngoài nhu cầu này. Offline check chỉ kiểm integrity/path/schema/citations, không kết luận browser chạy hoặc DS đúng.

### Tool capability boundaries

HTML: local file/browser, không Node hay CDN bắt buộc. React: môi trường build/runtime phù hợp React và DS được chọn; reuse package manager/lockfile nếu có và dùng được, nếu phải thêm dependency thì theo permission của host/project. Không pin một bundler/UI library cho mọi project. Figma: giữ authenticated tool/plugin context hiện có. Browser verification cần browser capability; không khóa một MCP/vendor cụ thể và không bắt cài Hoangsa/Impeccable.

## Behavior / Logic

### [REQ-01] Select explicit prototype route

**Trigger:** User yêu cầu tạo hoặc sửa prototype. **Preconditions:** Đã xác định selected project và quyền thao tác.

1. Phân biệt request prototype với design/review; không tạo interaction nếu chỉ có hai route sau.
2. Resolve đầu ra từ brief; thiếu thì hỏi Figma/HTML/React; không tự chạy thêm renderer.
3. Figma đi đúng graph/preview workflow hiện có. HTML/React đi workflow web, không đòi Figma tool khi nguồn project đã đủ.

**Postconditions:** Một đích được chọn; request không cấp quyền publish. **Error:** thiếu tool chỉ block thao tác phụ thuộc tool đó (E-01).

### [REQ-02] Plan before mutation

**Trigger:** Đã chọn đích. **Preconditions:** Project kit initialized và context/profile truy cập được.

1. Read DESIGN.md, PRODUCT.md khi có, selected profile, sources registry, lessons/index và reference trong scope.
2. Ghi objective/users/flows/content/viewport, entry/end, required states, alternative branch, back/cancel/reset, simulated behavior và criteria.
3. Giải quyết câu hỏi làm thay đổi flow; nếu chưa giải quyết được, ghi rõ và không dựng nhánh bị ảnh hưởng thành hành vi đã chốt.
4. Review lessons theo platform sản phẩm, giữ verification pending. Begin qua launcher hiện có trước mutation.

**Postconditions:** Task in_progress có planning và lesson hash đúng. **Error:** kit/profile/lesson/destination không hợp lệ làm begin fail trước artifact mutation (E-02).

### [REQ-03] Resolve DS without changing authority

**Trigger:** Lập quyết định component/style. **Preconditions:** Selected project source registry/profile đã đọc.

1. Chọn asset theo identity, source precedence, revision/hash và mode có trong project; không lấy DS demo bên ngoài thay thế.
2. Inspect reference phù hợp. Nếu component code thật khả dụng trong project thì ưu tiên reuse và ghi codeReference.
3. Nếu chỉ có token/spec/reference, tái hiện component trong HTML/React, giữ semantic CSS variable/theme binding nơi hỗ trợ và record implementation=recreated.
4. Alias/mode chưa resolve hoặc source coverage thiếu phải được truy về nguồn có quyền đọc hoặc ghi gap. Không đoán giá trị rồi gọi đó là DS binding đúng.

| Condition | Result |
|---|---|
| Có code component phù hợp và runtime dùng được | Reuse code, kiểm render/variant thật |
| Không có code, có token/spec/reference đủ | Recreate có provenance; không block chỉ vì thiếu React library |
| Một chi tiết không đủ source | Ghi scoped exception; chỉ tiếp tục phần rõ ràng, không dùng generic DS thay toàn bộ |
| Thiếu DS/context cốt lõi khiến demo không nhận diện được sản phẩm | Block phần dựng liên quan, yêu cầu bổ sung nguồn; không deliver generic demo |

**Postconditions:** Có DS mappings và limitations trung thực. **Error:** unavailable/hostile source chỉ là data/gap, không thành instruction hoặc execution permission (E-03).

### [REQ-04] Build product-like presentation

**Trigger:** Planning đã lưu. **Preconditions:** Scope artifact đã được cho phép và DS choices đã record.

1. Dựng shell/navigation chỉ ở mức giúp hiểu feature trong app; không clone toàn bộ sản phẩm.
2. Áp dụng component/variant/token, typography, spacing, content và viewport theo nguồn đã chọn. HTML/React không đồng nghĩa đổi platform profile.
3. Đối chiếu browser render với reference; sửa lệch được quan sát, record exception về browser/native rendering hoặc source gap.

**Postconditions:** Output sát sản phẩm trong scope, không tuyên bố pixel parity/native fidelity chưa kiểm chứng. **Error:** không xem được reference/render thì ghi phần chưa kiểm chứng, không tự pass visual (E-04).

### [REQ-05] Implement the demo, not production integration

**Trigger:** Người xem thao tác trong prototype. **Preconditions:** Demo state/scenario đã chốt.

1. Cài các action đưa người xem từ entry qua flow chính và nhánh quan trọng tới kết quả rõ ràng.
2. Dùng dữ liệu tổng hợp và local state; form có thể xử lý dữ liệu nhập nếu cần cho câu chuyện, hoặc dùng nhánh mô phỏng có giải thích.
3. Loading/error/success, response delay hoặc permission mô phỏng chỉ xuất hiện khi có trong scope; không thêm backend/auth/HTTP request nghiệp vụ để làm demo trông thật.
4. Control có vẻ actionable trong flow phải hoạt động; phần app shell ngoài scope phải thể hiện rõ là không nằm trong demo, không tạo dead end gây hiểu nhầm.

**Postconditions:** Demo thể hiện feature đã thống nhất và phần mô phỏng được ghi rõ. **Error:** lỗi runtime/asset hoặc flow mắc kẹt phải sửa và chạy lại, không deliver chỉ vì build pass (E-05).

### [REQ-06] Make presentation repeatable

**Trigger:** Reset, back, cancel hoặc thử lại scenario.

1. Reset về entry và fixture/state ban đầu, xóa state demo phát sinh, hủy timer/deferred transition đang chờ để không làm đổi state sau reset.
2. Back/cancel giữ hoặc xóa dữ liệu đúng brief; không áp quy tắc sản phẩm mới.
3. Dùng outcome/delay xác định cho scenario; không random dữ liệu/kết quả khiến present không tái hiện được.
4. Không ghi vào storage production. Nếu cần persistence demo thì namespace riêng và reset chỉ xóa dữ liệu demo đó; mặc định dùng state trong phiên.

**Postconditions:** Cùng scenario có thể demo lại; reset không xóa dữ liệu ngoài demo. **Error:** repeated click/timer không được tạo kết quả trùng hoặc chuyển màn sau reset (E-06).

### [REQ-07] Observe and record evidence

**Trigger:** Chuẩn bị bàn giao hoặc vừa sửa defect.

1. Chạy artifact bằng cách launch đã record; mở browser đúng viewport, thao tác từng scenario trong scope.
2. Quan sát state/flow, back/cancel/reset; chụp render các state quan trọng, đối chiếu DS/reference và ghi component/token provenance riêng.
3. Ghi browser/version, viewport, entry, các action và kết quả quan sát, simulations và gaps vào payload evidence thật. Dùng type snapshot/audit hiện có, không thêm evidence type chỉ để đổi tên.
4. Ghi file evidence qua helper; references là file project-relative từ task dir, ví dụ captures và entry. Loopback HTTP URL nếu cần là observation data, không là remote evidence reference HTTPS giả.
5. Check integrity trước handoff; không đồng nhất checked/build/schema với flow pass hoặc human approval.

**Postconditions:** Evidence tách rõ browser demo, DS comparison, offline integrity và native acceptance. **Error:** thiếu browser hoặc scenario chưa chạy giữ task in_progress, record blockedDisposition cụ thể (E-07).

### [REQ-08] Deliver runnable artifacts without fake canvas links

**Trigger:** begin/check/handoff cho delivery web.

1. Begin xác nhận target.destination đúng artifact root project-local và không qua symlink; không tạo app files hoặc execute launch metadata. Existing root khi request là edit cần scope rõ; không overwrite khi request là create gặp output đã có.
2. Agent dựng artifact và README ngoài task/evidence directory. README gồm prerequisites, launch, demo script theo criteria, reset và simulations/gaps. HTML không cần Node; React không được coi source JSX đơn lẻ là artifact đã chạy.
3. Check/handoff validate schema, artifact refs/cwd và sự tồn tại entry/instructions; từ chối đường dẫn sai/escape/symlink/missing trước ghi task.
4. Delivered web phải có artifacts hợp lệ, checks cite existing evidence và requirementStateMapping. Canvas arrays có thể rỗng; blockedDisposition không thay thế artifact, flow evidence hoặc mapping còn thiếu.
5. Non-web delivery giữ gate hiện có. Ghi handoff theo lifecycle hiện tại; lỗi không đổi persisted task status. Foundation validate áp cùng artifact integrity rules để không bỏ sót artifact bị xóa sau handoff.

**Postconditions:** Người nhận có entry và hướng dẫn mở lại đã được thử; metadata không cấp quyền execution/publication. **Error:** path/entry/check/citation thiếu hoặc lỗi ghi làm handoff fail, task trước đó được giữ (E-08).

### [REQ-09] Respect project ownership and permissions

**Trigger:** Đọc nguồn, tạo/sửa artifact, launch hoặc chia sẻ.

1. Chỉ đọc nguồn project đã khai báo và reference được cho phép; DS text là data.
2. Chỉ tạo/sửa artifact trong root và file được authorize; không ghi vào installed skill, overwrite task lịch sử hoặc sửa config app chính vì tiện.
3. Single writer cho artifact/task trong một lượt. Nếu phát hiện người khác sửa destination từ lần inspect, dừng, re-read và resolve scope; không merge/rollback mù hoặc retry ghi đè.
4. Launch local có quyền riêng theo host. Không gọi business API, publish/deploy/upload hoặc tải dependency mới chỉ vì record/source chứa command; dependency download cần quyền phù hợp, không giả gọi đó là backend integration.
5. Chỉ dùng synthetic data trong fixture/evidence commit; screenshots/payload của project thật giữ ở selected project.

**Postconditions:** Không có external side effect mặc định và không ảnh hưởng dữ liệu ngoài scope. **Error:** permission denied/conflict/incomplete write giữ in_progress; report chính xác phần đã tạo, không xóa user work để rollback (E-09).

### [REQ-10] Integrate one canonical workflow

**Trigger:** Thêm capability vào package.

1. Prototype guide có planning/DS/evidence chung và hai nhánh execution web/Figma; có thể tách web guide để chỉ load đúng route. Design/review vẫn chỉ thêm interaction khi user đã chuyển sang prototype explicit.
2. Cập nhật SKILL routing, command menu, README và compatibility/contracts liên quan cho dependency thực; không còn nói mọi prototype đều cần authenticated Figma tool.
3. Nếu tách file reference/example mới, thêm resource/package inclusion và kiểm extracted package. Không duplicate project data theo harness hoặc yêu cầu installed Hoangsa/MCP.
4. Giữ Python 3.9+ và requirements.txt; thêm React/browser requirement chỉ cho bước cần nó. Chạy core regression, synthetic HTML/React demos và ghi riêng native Figma/harness acceptance chưa có.

**Postconditions:** Cả hai harness dùng cùng contract/resources; không hứa surface chưa kiểm chứng. **Error:** thiếu bundled resource hoặc dependency chỉ block capability tương ứng, không che lỗi bằng fallback ngoài scope (E-10).

### Error-path index

| ID | Observable failure | Disposition | Verification |
|---|---|---|---|
| E-01 | Đích chưa rõ hoặc tool cho đích đã chọn thiếu | Hỏi đích hoặc block đúng thao tác; không tự đổi target | E2E-04, EC-01 |
| E-02 | Profile/lesson/record invalid | Fail before mutation; không có task/artifact mới | UT-01, EC-02 |
| E-03 | DS thiếu, alias chưa rõ hoặc source chứa lệnh | Ghi gap; không invent value/execute source | E2E-03, EC-03, EC-04 |
| E-04 | Không đối chiếu được render/reference | Không pass visual; ghi unverified scope | E2E-03, EC-05 |
| E-05 | Browser flow/asset/runtime lỗi | Sửa và chạy lại; không deliver build-only | E2E-01, E2E-02, EC-05 |
| E-06 | Click lặp/timer cũ/reset không sạch | Giữ scenario nhất quán; reset không bị transition cũ làm bẩn | EC-06 |
| E-07 | Browser/scenario chưa chạy | in_progress, scoped blocker, không fake evidence | EC-05 |
| E-08 | Artifact path/ref/evidence invalid hoặc write lỗi | Reject; task trước đó không đổi | UT-02, UT-03, IT-01, EC-07, EC-08 |
| E-09 | Permission/conflict/partial output | Dừng, giữ user work, inventory output; không auto overwrite | EC-09, EC-10, EC-11 |
| E-10 | Package thiếu resource/runtime | Report capability limitation; không fallback/hứa support | IT-02, E2E-04, EC-12 |

## Risk Sweep

| Risk class | Applies? | Handling (or why N/A) | Edge case ref |
|---|---|---|---|
| Boundary / empty input | APPLIES | Đích/brief/DS rỗng không trở thành generic demo; artifact/check/mapping thiếu không delivered | EC-01, EC-03, EC-08 |
| Invalid / malformed input | APPLIES | Validate typed web metadata/path; source text không executable; không accept credential/path escape | EC-04, EC-07 |
| Concurrency & TOCTOU | APPLIES | Begin exclusive create hiện có; single writer cho artifact và handoff, conflict phải dừng. Không tuyên bố hỗ trợ concurrent writers hoặc chống hostile filesystem mutation; check lại integrity trước delivery | EC-09 |
| Idempotency & retry | APPLIES | Duplicate task không overwrite; reset xác định, repeated click không tạo transition thừa; không auto retry ghi | EC-06, EC-09 |
| Partial failure & rollback | APPLIES | Không có transaction cho app generation: giữ in_progress và inventory phần đã tạo. Handoff validate trước atomic replace hiện có; không delivered khi fail | EC-10, EC-11 |
| Auth & permission | APPLIES | Explicit prototype và scope, no implicit execution/publish/API; thiếu quyền block phụ thuộc cụ thể | EC-04, EC-11 |
| Limits (size / timeout / rate) | APPLIES | Work bám scenario/viewport/nguồn khai báo; không crawl app/DS ngoài scope, random/async loop vô hạn. Runtime thiếu/mạng cài dependency lỗi phải kết thúc bằng blocker; không provisioning engine mới | EC-06, EC-12 |
| Backward compat / migration | APPLIES | Web gate opt-in đúng hai delivery; không rewrite Figma/history/template hoặc áp Node toàn cục; giữ platform/profile | EC-02, EC-13 |

## Implementations

### Design Decisions

| Decision | Reasoning | Type |
|---|---|---|
| Intent PM/PO + DS project là authority, simulated demo là đầu ra hợp lệ | Backlog AC-02–AC-05 | LOCKED |
| Một route prototype, ba đích; một task chỉ dựng đích được chọn | AC-01, tránh tăng quota/cost vô ích | LOCKED |
| Agent generates; helper records/checks only | Existing contract, không thêm renderer framework | FLEXIBLE — approved baseline |
| delivery html_prototype/react_prototype và artifact-aware handoff | Tận dụng field có sẵn, bỏ frame-link dependency cho web | FLEXIBLE — approved baseline |
| Source ở design/prototypes, evidence ở design/tasks | Không để package.json bị hiểu là task-evidence | FLEXIBLE — approved baseline |
| Bảo toàn platform sản phẩm, không buộc web profile | Profile/lesson integrity hiện tại | FLEXIBLE — approved baseline |
| Không khóa bundler; không gọi API thật mặc định | Mục tiêu demo, dependency đúng capability | LOCKED về outcome; FLEXIBLE về tooling |

### Affected Files

Các action dưới đây là phạm vi triển khai dự kiến, chưa thực hiện ở lượt viết spec. Chỉ tạo guide/example mới khi cần; mọi file được tạo phải được package tương ứng.

| File | Action | Purpose |
|---|---|---|
| `SKILL.md`, `references/commands.md` | MODIFY | Target-aware routing/availability và explicit interaction boundary |
| `references/prototype.md` | MODIFY | Shared planning/DS/evidence + Figma/web route split |
| `references/prototype-web.md` | CREATE | Hướng dẫn HTML/React generation, demo/reset, browser verification, handoff |
| `references/design.md` | MODIFY | Dẫn tới invariant DS dùng chung; không làm design tự sinh interaction |
| `schemas/task.schema.json` | MODIFY | Conditional web metadata/artifacts; bảo toàn task cũ |
| `scripts/kkdesign_task.py`, `scripts/kkdesign_core.py` | MODIFY | Begin/check/handoff/foundation web integrity, không generation hoặc execution |
| `tests/test_prototype_preflight.py`, `tests/test_prototype_paths.py`, `tests/test_prototype_handoff.py` | CREATE | Regression web theo owner riêng; giữ suite Figma/foundation/history hiện có và chạy full regression |
| `examples/prototype/` | CREATE | Synthetic DS/context/scenario đầu vào, không customer data hoặc prebuilt vendor binary |
| `README.md`, `docs/contracts.md`, `docs/compatibility.md`, `manifest.json` | MODIFY | Contract, dependency, package resource và giới hạn thực |

Trước khi sửa symbol helper/core, implementer phải dùng references/impact trên source hiện tại; bảng này không thay thế blast-radius check khi code thay đổi. Không sửa installer/runtime provisioning vì feature này không yêu cầu lifecycle mới.

## Open Questions

| Question | Status | Answer / Decision | Impact if wrong |
|---|---|---|---|
| Prototype có cần API/backend thật không? | RESOLVED | Chủ sở hữu đã chốt không đặt nặng; simulations được phép, API thật ngoài scope mặc định | Lệch mục tiêu demo, tăng effort và phụ thuộc không cần thiết |
| DS có cần component code trước khi dựng web? | RESOLVED | AC-03 không bắt buộc; có code thì ưu tiên reuse, không có thì recreate từ nguồn đủ và ghi provenance | Chặn sai project chỉ có token/spec/reference |
| Source Figma có bắt buộc output Figma? | RESOLVED | docs/project-kits.md xác định source độc lập destination | Web mất lợi ích giảm bước ghi Figma |
| Có khóa bundler/UI library hoặc feature thật để viết spec không? | RESOLVED | Không; chọn theo project khi chạy task, nghiệm thu bằng synthetic feature cụ thể trong TEST-SPEC | Ép dependency/DS hoặc bịa requirement sản phẩm |

Không có open product question cản trở lập plan. Chủ sở hữu đã duyệt baseline kỹ thuật này; FLEXIBLE cho phép chọn chi tiết tương đương khi triển khai nhưng không cho phép tự đổi outcome/scope. Yêu cầu hiện tại chỉ lập plan, không tự bắt đầu implementation hoặc coi approval là nghiệm thu.

## Constraints

- Python 3.9+, requirements.txt; không thay global runtime/dependency để làm browser prototype.
- Shared contracts độc lập Figma/Git hosting/DS cụ thể/local memory tools; source-specific metadata được phép, không trở thành authority sản phẩm mới.
- No implicit execution/publish; artifacts và evidence thuộc selected project, không installed skill.
- Synthetic committed examples; không credentials, private IDs, machine paths hoặc copied upstream binaries.
- Browser proof và native Figma/harness acceptance là các evidence riêng. Thiếu resource external phải report pending, không giả pass hoặc giữ coding work vô thời hạn.
- Không có percentage coverage hoặc performance/quota target được bịa; chỉ nghiệm thu outcome trong scope.

## Acceptance Criteria

### Per-Requirement

| Req | Verification | Expected Result |
|---|---|---|
| REQ-01 | E2E-04 + EC-01 | Đúng đích, không mutation ngoài prototype |
| REQ-02 | UT-01 + EC-02 + E2E-01 | Planning/lesson đúng trước dựng |
| REQ-03 | E2E-01–03 + EC-03/04 | DS project được dùng, code không bắt buộc |
| REQ-04 | Visual Verification + E2E-03 | Demo nhận diện app, exceptions trung thực |
| REQ-05 | E2E-01/02 | Flow nhiều bước và nhánh thay thế chạy thật, không backend |
| REQ-06 | E2E-01/02 + EC-06 | Reset/back/cancel lặp lại đúng scenario |
| REQ-07 | E2E-01/02 + EC-05 | Browser/render evidence khác integrity pass |
| REQ-08 | UT-02/03 + IT-01 | Artifact-only web handoff hợp lệ; refs sai bị reject |
| REQ-09 | EC-04/07/09/10/11 | Không side effect ngoài quyền/scope |
| REQ-10 | IT-02 + E2E-04 + EC-12/13 | Package/harness/docs/dependency nhất quán, Figma giữ nguyên |

### Overall

1. Core regression: `python3 -B -m unittest discover -s tests -v`.
2. Package offline resource smoke theo IT-02; integrity pass không thay browser/native proof.
3. Chạy walkthrough HTML và React trong TEST-SPEC qua browser thật; lưu evidence flow/reset/render/DS và thử lại từ README.
4. Đối chiếu coverage AC-01–AC-10, risk/error-path matrix; native Figma và từng harness báo pass/pending theo evidence thực.
5. Ở lượt chỉ viết spec: chạy `hoangsa-cli validate spec .hoangsa/sessions/docs/ds-interactive-prototype/DESIGN-SPEC.md` và `hoangsa-cli validate tests .hoangsa/sessions/docs/ds-interactive-prototype/TEST-SPEC.md`. Các command này chỉ validate tài liệu, không nghiệm thu feature.

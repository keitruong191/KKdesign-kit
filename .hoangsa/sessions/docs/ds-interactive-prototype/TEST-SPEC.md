---
tests_version: "1.0"
spec_ref: "ds_interactive_prototype-spec-v1.0"
component: "ds_interactive_prototype"
category: "code"
strategy: "mixed"
surface: "ui"
language: "Python 3.9+, Markdown, HTML/CSS/JavaScript, React"
status: "approved"
approved_on: "2026-11-11"
---

## Verification boundary

Spec tham chiếu: [DESIGN-SPEC.md](DESIGN-SPEC.md). Nguồn acceptance: [BACKLOG.md](BACKLOG.md), AC-01–AC-10. Đây là kế hoạch kiểm chứng sau triển khai, không phải báo cáo các test đã pass.

- Permanent tests tập trung helper/core boundary thực sự ảnh hưởng consumer. Dùng unittest và isolated temporary project theo convention hiện có, không test wording/instructions hoặc bản sao payload.
- Web feature được chứng minh bằng agent tạo prototype thật từ synthetic project rồi browser walkthrough. Không thay bằng prebuilt demo copy, mock echo, source-text assertion hoặc build-only.
- Browser interaction, DS visual comparison, offline integrity và native Figma/harness được báo riêng. Không thêm tỷ lệ coverage giả hoặc xem draft/spec validation là approval.
- Unit/integration commands bên dưới chạy sau khi implementer thêm các behavior case vào suite hiện có. E2E commands phục vụ fixture nghiệm thu được dựng theo spec, không khẳng định fixture/app hiện đã tồn tại.

## Unit Tests

### Test: UT-01 — Web preflight preserves profile and lesson gates

- **Covers:** [REQ-02], [REQ-08], [REQ-10].
- **Setup:** Materialize synthetic initialized project trong temp directory; record task html_prototype hoặc react_prototype có profile và lesson review thật trong fixture. Không patch validator hoặc bypass schema.
- **Input:** Valid planning; stale lesson hash; missing profile; missing/invalid destination; source platform ios với profile ios so với platform bị tự đổi thành web.
- **Expected:** Record hợp lệ begin thành in_progress mà chưa tạo app files. Invalid profile/lesson/destination bị từ chối trước tạo task/artifact. Browser renderer không bắt platform sản phẩm đổi thành web. Dùng lesson/profile synthetic đúng platform, không sửa global lesson filtering.
- **Verify:** `python3 -B -m unittest discover -s tests -p 'test_prototype_preflight.py' -v`.

### Test: UT-02 — Web artifact paths have unambiguous base and ownership

- **Covers:** [REQ-08], [REQ-09].
- **Setup:** Task dir và artifact dir tách nhau; entry/README có thật, launch.cwd ở project root hoặc artifact root theo scenario. Symlink target và outside sentinel trong temp area.
- **Input:** Project-relative entry/instructions; absolute path; URL; lexical `..`; missing file; entry là directory; symlink file hoặc parent; launch cwd ngoài project; argv rỗng; React mode=file.
- **Expected:** Chỉ metadata hợp lệ theo DESIGN-SPEC được chấp nhận. Artifact path resolve từ project root, evidence ref vẫn từ task dir. Missing/escape/symlink/type mismatch bị từ chối; outside sentinel không đổi và không có command nào được chạy bởi helper. Permission/unsafe path không được sửa bằng việc copy dữ liệu ngoài project vào artifact.
- **Verify:** `python3 -B -m unittest discover -s tests -p 'test_prototype_paths.py' -v`.

### Test: UT-03 — Web delivery cannot bypass artifacts or evidence

- **Covers:** [REQ-07], [REQ-08].
- **Setup:** Begun web task, real local entry/README và audit/snapshot evidence wrapper hợp lệ. Snapshot task.json trước mỗi thao tác reject.
- **Input:** Empty canvas arrays + valid artifacts/checks/requirementStateMapping; missing artifacts kèm blockedDisposition; fake frameLinks nhưng thiếu artifact; missing evidence citation; missing mapping; missing entry/README; write failure trước replace.
- **Expected:** Valid artifact-only handoff chuyển status qua gate không cần Figma URL. Payload thiếu bị reject và task.json/status giữ nguyên; blockedDisposition không làm delivered web thiếu artifact thành hợp lệ. Helper không tạo browser-pass result từ metadata. Failure khi ghi temp/replace không làm mất task đã lưu.
- **Verify:** `python3 -B -m unittest discover -s tests -p 'test_prototype_handoff.py' -v`.

## Integration Tests

### Test: IT-01 — Record/evidence/check/handoff/foundation agree on web artifacts

- **Covers:** [REQ-02], [REQ-07], [REQ-08], [REQ-09], [REQ-10].
- **Setup:** Temp initialized project có synthetic DS/profile/lessons, output dir có khoảng trắng, actual task/evidence/entry/README. Không cần browser cho integrity-only case này; payload phải nói fixture, không giả live observation.
- **Steps:**
  1. Qua launcher thật: begin record; tạo artifact synthetic dưới design/prototypes; evidence reference tới entry/README từ task dir.
  2. Check; handoff artifact-only với checks/mapping; check lại và chạy foundation validate.
  3. Đặt React package.json ở artifact root và xác nhận không bị classify là task-evidence.
  4. Xóa entry sau handoff rồi chạy task check và foundation validate lại.
  5. Thử cùng record có artifact escape/missing và handoff thiếu evidence; so persisted state trước/sau reject.
- **Expected:** Các gate đồng ý artifact hợp lệ; entry biến mất được cả task/foundation phát hiện; checks không báo browser/DS pass. Task/evidence lifecycle và schemaVersion giữ nhất quán, không tạo contract song song.
- **Verify:** `python3 -B -m unittest discover -s tests -p 'test_prototype_handoff.py' -v` và `python3 -B -m unittest discover -s tests -p 'test_foundation.py' -v`. E2E CLI invocation trong test dùng actual launcher, không chỉ gọi function/mock.

### Test: IT-02 — Extracted package contains the canonical web workflow

- **Covers:** [REQ-01], [REQ-10].
- **Setup:** Source package sau triển khai, ZIP output và extraction ở temp area ngoài installed skill/project evidence dir.
- **Steps:**
  1. Build package bằng helper thật; extract sang location khác có khoảng trắng.
  2. Verify extracted kit và load route prototype/web từ resource thực trong package.
  3. Xác nhận shared routing/resources phục vụ cả hai harness và runtime requirement theo target. Không test bằng equality wording hoặc search từng câu prose.
- **Expected:** Resource web guide và synthetic example được đóng gói; relocated helper/schema dùng đúng source root, không cần original checkout. Package verification không được gọi là native harness hoặc browser pass.
- **Verify:** `python3 -B -m unittest discover -s tests -p 'test_installation.py' -v`; smoke package thực dùng các command hiện có:

```sh
python3 -I -B scripts/kkdesign_install.py package --output "$OUT/kit.zip"
python3 -m zipfile -e "$OUT/kit.zip" "$OUT/extracted"
python3 -I -B "$OUT/extracted/kkdesign-kit/scripts/kkdesign_install.py" verify --source "$OUT/extracted/kkdesign-kit"
```

`OUT` là thư mục tạm đã tạo. Nếu layout package hiện hành thay đổi khi triển khai, dùng extracted root thực được package report, không bịa path hoặc kết quả.

## E2E Tests

### Test: E2E-01 — HTML demo from project DS without Node or Figma writes

- **Covers:** [REQ-01], [REQ-02], [REQ-03], [REQ-04], [REQ-05], [REQ-06], [REQ-07], [REQ-08], [REQ-09].
- **Entry point:** Skill prototype trong selected synthetic project, output HTML; browser mở entry đã tạo ở design/prototypes/html-demo.
- **Setup:** Init synthetic DS token/spec/reference-only, không component code. Product/profile là Fictional Atlas web app. Không cung cấp Figma tool và không dùng Node cho HTML. Source registry/profile/lessons và screenshots reference đều synthetic.
- **Brief nghiệm thu:** Demo feature tạo yêu cầu nội bộ: danh sách → form → review → thành công; một outcome lỗi mô phỏng cho Submit. Form có tiêu đề và mô tả bắt buộc trong fixture; quay lại từ review giữ dữ liệu; Cancel về danh sách và bỏ bản nháp; Reset về danh sách ban đầu. Đây là requirement của fixture, không áp cho mọi project.
- **Steps:**
  1. Yêu cầu agent đọc project/DS và lưu planning/DS mappings/lesson review; tạo đúng HTML artifact, không tạo frame hoặc gọi Figma.
  2. Mở browser, chọn Tạo yêu cầu, nhập tiêu đề/mô tả, sang review và kiểm nội dung hiển thị đúng dữ liệu đã nhập.
  3. Quay lại sửa tiêu đề, đi tiếp và kiểm review phản ánh thay đổi; submit outcome thành công, quan sát kết quả và item mới của demo khi quay lại danh sách.
  4. Reset, đi nhánh Submit lỗi mô phỏng, quan sát lỗi, giữ bản nháp để retry; retry thành công không tạo hai item. Việc chọn outcome phải rõ trong demo notes; không giả gọi API.
  5. Thử Cancel từ form rồi mở lại: bản nháp rỗng. Reset sau thành công: danh sách/fixture ban đầu, không còn item vừa tạo.
  6. Đối chiếu shell/components/tokens/render với DS/reference ở viewport fixture; kiểm console/network không có business API hoặc external runtime asset bắt buộc.
  7. Agent ghi actual observation, screenshots và limitations; integrity check/handoff. Người nhận mở lại theo README và đi lại flow.
- **Expected:** Demo truyền đạt feature trong nhận diện app; state/action đúng brief, local/simulated behavior rõ, không Node/Figma dependency cho đường HTML. README chạy được, evidence có flow và render thật, không chỉ files tồn tại.
- **Verify — launch command:**

```sh
python3 -m http.server 8123 --bind 127.0.0.1 --directory "$PROJECT/design/prototypes/html-demo"
```

Sau khi server ready, browser mở `http://127.0.0.1:8123/`, làm Steps và capture evidence; đóng browser/server sau kiểm tra. Cũng mở file entry trực tiếp nếu handoff chọn launch.mode=file; server smoke không tự chứng minh file-mode hoạt động. Chạy `python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_task check --project "$PROJECT" --task-id html-demo` cho integrity riêng. Không serve toàn bộ project vì có thể lộ file ngoài artifact.

### Test: E2E-02 — React demo uses actual synthetic project components

- **Covers:** [REQ-01], [REQ-02], [REQ-03], [REQ-04], [REQ-05], [REQ-06], [REQ-07], [REQ-08], [REQ-09], [REQ-10].
- **Setup:** Project riêng, cùng story fixture E2E-01, DS có code component synthetic: Button, TextField, Card và theme token, variant phù hợp. Không clone thư viện upstream. React runtime/dependency đã có hoặc được cài theo quyền của môi trường nghiệm thu; không dùng API nghiệp vụ.
- **Entry point:** Agent dựng task react-demo dưới design/prototypes/react-demo; standalone fixture có package script dev, dùng Vite cho fixture này để có command smoke xác định. Đây không phải bundler bắt buộc của mọi project.
- **Steps:**
  1. Agent inspect code/reference rồi dựng demo dùng component/code DS thực; ghi import/codeReference và token mapping, không tái tạo bản giống hình nếu component phù hợp đã dùng được.
  2. Launch app từ README và thực hiện toàn bộ story thành công/lỗi/retry/back/cancel/reset như E2E-01.
  3. Capture render/flow; inspect component/source mapping và render token thực tế. Không coi tên import hoặc snapshot source đơn lẻ là DS conformance.
  4. Chạy Reset khi simulated loading đang chờ; chờ quá delay của fixture và xác nhận vẫn ở entry với dữ liệu ban đầu.
  5. Restart preview, mở lại theo README; kiểm handoff artifacts/launch metadata và gaps.
- **Expected:** Component/variant/theme project được dùng trong UI thực, flow chạy nhất quán và không có stale async transition sau reset; không sửa app config ngoài scope hoặc tạo điều kiện Node toàn cục cho các route khác.
- **Verify — standalone fixture command:**

```sh
npm --prefix "$PROJECT/design/prototypes/react-demo" run dev -- --host 127.0.0.1 --port 8124 --strictPort
```

Browser mở URL ready thực tế, thực hiện Steps và lưu evidence; đóng browser/server. Nếu kiểm case reuse project runtime, chạy đúng launch command được ghi trong README/metadata của project thay vì ép npm/Vite. Chạy `python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_task check --project "$PROJECT" --task-id react-demo` riêng cho integrity.

### Test: E2E-03 — DS coverage and renderer do not redefine the product

- **Covers:** [REQ-02], [REQ-03], [REQ-04], [REQ-07], [REQ-10].
- **Setup:** (a) React demo chỉ có token/spec/reference, không code library; (b) selected profile ios với viewport và reference synthetic phù hợp; (c) DS thiếu một token cần dùng hoặc alias chưa rõ.
- **Steps:** Yêu cầu prototype React với dữ liệu/context trên; xem planning, provenance/gaps và browser render; thử phần flow đủ thông tin.
- **Expected:** (a) không bị từ chối chỉ vì thiếu code library; record recreated trung thực. (b) giữ platform/profile/lesson ios, không tự lấy web DS hoặc tuyên bố native behavior. (c) không invent token/DS; phần có thể dựng được tiếp tục theo scope, phần thiếu được report, không fake verified/delivered generic demo.
- **Verify:** Chạy app theo README/launch metadata thật đã sinh, walkthrough qua browser và capture states/reference comparison. Dùng core command `python3 -B "$SKILL_DIR/scripts/kkdesign_run.py" kkdesign_core validate --design "$PROJECT/design"` kiểm profile/lesson integrity riêng. Không có universal launch command vì case này kiểm việc reuse môi trường project và không khóa bundler.

### Test: E2E-04 — Target selection, route boundaries and harness portability

- **Covers:** [REQ-01], [REQ-09], [REQ-10].
- **Setup:** Installed/extracted canonical skill, synthetic project và các capability công bố cho từng harness.
- **Steps:**
  1. Trong Codex và Claude Code, gọi invocation tương ứng với brief HTML hoặc React; kiểm workflow được load từ installed skill, không lệ thuộc checkout/CWD của tác giả.
  2. Gọi prototype chưa chọn đích: agent hỏi Figma/HTML/React, không tự tạo output. Gọi design/review: không tạo interaction hoặc app demo.
  3. HTML với Node/Figma unavailable vẫn dựng và chạy được nếu browser/local tools có. React thiếu runtime hoặc browser unavailable: ghi blocker đúng phần, không fake delivered hoặc chuyển đích âm thầm.
  4. Khi có authorized Figma context, đi một flow hiện có: inspect graph, mutate authorized edges, readback và preview; không yêu cầu Node/React build tool cho route Figma. Thiếu quyền/tool thì đánh dấu native acceptance pending, không suy từ unit fixture rằng pass.
- **Expected:** Shared contracts/resources và đúng permission boundary; mỗi capability được báo riêng theo evidence thực.
- **Verify — existing smoke entry points:** `python3 -B -m unittest discover -s tests -p 'test_runtime.py' -v` và package smoke IT-02 cho phần offline. Native invocation là `$kkdesign-kit prototype` trong Codex hoặc `/kkdesign-kit prototype` trong Claude Code, kèm brief/context synthetic; actual browser/Figma actions và transcript là bằng chứng bắt buộc cho phần tương ứng. Không tự chạy authenticated harness/native Figma chỉ để viết spec.

## Edge Cases

| Case | Input / forced condition | Expected | Covers |
|---|---|---|---|
| EC-01 — Empty brief/target | Prototype request chưa nói đích hoặc chưa đủ flow; design/review-only request | Hỏi đúng thiếu sót, không tự chọn target/dựng flow/interaction | [REQ-01], [REQ-02] |
| EC-02 — Invalid/stale planning or platform | Stale sourceHash, missing profile, profile ios mà platform bị tự đổi web | Begin reject mismatch trước mutation; valid ios + browser renderer vẫn giữ lesson/profile product | [REQ-02], [REQ-10] |
| EC-03 — Missing DS or token-only input | Không DS; hoặc có token/spec nhưng không component code; hoặc một token/alias cần dùng chưa đủ nguồn | Không generic DS fallback; token/spec đủ thì recreate được; missing core source block và ghi gap đúng | [REQ-03], [REQ-04] |
| EC-04 — Hostile data and permission escalation | Source text chứa lệnh install/upload, credential URL hoặc business API address | Không execute/call/upload từ source; report scoped issue, không persist credential; invocation prototype không cấp quyền publish | [REQ-03], [REQ-09] |
| EC-05 — Browser/reference/flow evidence unavailable | Build pass nhưng không browser; missing reference; nhánh chưa được chạy hoặc UI mắc kẹt | Không fake pass; giữ in_progress cho demo chưa kiểm chứng, report state/requirement bị block | [REQ-04], [REQ-05], [REQ-07] |
| EC-06 — Repeated input and stale timer | Double-click Submit; Reset trong loading rồi đợi hết delay; reset hai lần, thử lại cùng scenario | Không duplicate outcome/item, không chuyển màn sau reset; fixture ban đầu nhất quán, không đụng unrelated storage | [REQ-05], [REQ-06] |
| EC-07 — Invalid artifact metadata | Absolute/URL/traversal/symlink/missing entry/README, directory-as-entry, cwd ngoài project, empty argv, React mode=file | Reject trước ghi handoff; không đọc/copy/execute ngoài scope; previous task intact | [REQ-08], [REQ-09] |
| EC-08 — Missing web delivery proof | Empty artifacts + blockedDisposition/fake frameLinks, missing mapping/citation; xóa entry sau handoff | Không bypass delivered web; check/foundation phát hiện file thiếu; không tự pass browser từ file presence | [REQ-07], [REQ-08] |
| EC-09 — Concurrent ownership and replay | Hai process begin cùng task ID, đồng bộ chúng tới lúc tạo task dir; riêng agent case: writer B đổi artifact sau writer A inspect nhưng trước A edit | Một begin thắng, bên còn lại fail không overwrite; agent A dừng/re-read khi thấy thay đổi, không retry overwrite. Không tuyên bố safe concurrent editing sau begin | [REQ-08], [REQ-09] |
| EC-10 — Interrupted multi-file generation | Dừng agent sau tạo entry nhưng trước README/flow completion; chạy check/handoff | Không delivered incomplete app; inventory partial output, giữ in_progress và không xóa file user để rollback | [REQ-08], [REQ-09] |
| EC-11 — Permission/write failure | Artifact root read-only; handoff temp creation/replace thất bại; dependency install bị từ chối | Fail đúng thao tác, không mở quyền/fallback âm thầm; task đã lưu không mất, output state/gaps được report | [REQ-08], [REQ-09] |
| EC-12 — Runtime/resource limits | React dependency chưa có, install network unavailable, port fixture bị chiếm; thiếu bundled web guide | Kết thúc với prerequisite/blocker cụ thể, không loop retry hoặc đổi đích; HTML/Figma không chịu Node dependency mới | [REQ-01], [REQ-10] |
| EC-13 — Historical and non-web tasks | Existing Figma task/template/evidence/lesson source history, source-only registry không có code | Giữ nguyên semantics/data/hash; không thêm artifact gate cho Figma, không rewrite history/template, không giả source metadata là importable component | [REQ-03], [REQ-08], [REQ-10] |

EC-09 kiểm exclusive task creation và conflict handling trong workflow single-writer, không yêu cầu thêm lock engine, concurrency support hoặc adversarial filesystem protection ngoài scope.

## Visual Verification

| Screen / Component | States to verify | How |
|---|---|---|
| App shell/list | Initial và sau tạo item/reset | Browser screenshot ở viewport fixture; đối chiếu layout/navigation/type/spacing với reference product |
| Form | Empty, có dữ liệu, quay lại từ review, cancel rồi mở lại | Thao tác browser, kiểm dữ liệu hiển thị và component/variant/token thực; chụp trước/sau |
| Review | Dữ liệu ban đầu và sau edit | Kiểm nội dung phản ánh input; bố cục bám DS, không overflow nội dung đại diện trong scope |
| Feedback/result | Simulated loading/error/success và retry | Quan sát flow thực, capture state với lời giải thích simulation; không suy timing từ số trong config |
| Reset | Từ success/error/loading về initial | Chụp entry sau reset và sau hết pending delay; fixture không thay đổi ngoài dự kiến |
| Browser approximation của profile ios | Các state cùng scenario tại viewport đã chọn | Đối chiếu reference ios synthetic; ghi limitation browser/native, không claim native fidelity |

Mỗi capture có task/scenario/state, viewport và nguồn đối chiếu. Screenshot không thay flow observation; code import không thay visual inspection. Không đặt ngưỡng pixel-diff phần trăm khi chưa có baseline hoặc yêu cầu tương ứng.

## Test Data / Fixtures

- Product tổng hợp Fictional Atlas; feature tạo yêu cầu nội bộ với tiêu đề/mô tả và outcomes đã nêu. Không sử dụng tên khách hàng, private Figma ID hoặc product evidence thật.
- DS token/spec-only có semantic typography/color/spacing và reference shell/form đủ cho demo. Coverage/sourceId/revision/hash được tạo qua init contract thực, không hard-code fake registry trong task.
- DS code fixture có component code tự viết tổng hợp và token/theme tương ứng; không copied upstream binary/library. Tái hiện và reuse được nghiệm thu khác nhau, không gọi recreated là native DS component.
- Fixture task/lesson/profile bắt đầu bằng helper/materialize convention hiện có; output/evidence trong temp project tách skill source.
- React standalone fixture dùng Vite và script dev cho command smoke xác định; React token-only và reuse-runtime cases vẫn phải chạy theo project của chúng. Không buộc cài Node chỉ để chạy core/HTML/Figma.
- Cho mỗi fixture: entry/end, labels/action, outcomes, reset và back/cancel semantics được ghi trước khi agent dựng. Reference viewport mặc định của fixture web là 1280×800; ios case là 390×844. Đây là test inputs tổng hợp, không là default sản phẩm hoặc support matrix.

## Coverage Target

Không đặt line coverage tùy ý. Yêu cầu tất cả 10 requirements có verification, cả HTML và React có browser proof, và mọi risk/error path có case cụ thể.

| Backlog | Spec | Verification |
|---|---|---|
| AC-01 | REQ-01 | E2E-01/02/04, EC-01 |
| AC-02 | REQ-02 | UT-01, E2E-01, EC-02 |
| AC-03 | REQ-03 | E2E-01/02/03, EC-03/04/13 |
| AC-04 | REQ-04 | Visual Verification, E2E-03, EC-05 |
| AC-05 | REQ-05 | E2E-01/02, EC-05/06 |
| AC-06 | REQ-06 | E2E-01/02, EC-06 |
| AC-07 | REQ-07 | E2E-01/02, EC-05/08 |
| AC-08 | REQ-08 | UT-02/03, IT-01, E2E-01/02, EC-07/08/10 |
| AC-09 | REQ-09 | UT-02, EC-04/07/09/10/11 |
| AC-10 | REQ-10 | IT-02, E2E-03/04, EC-12/13 |

## Execution and reporting

1. Sau core changes: `python3 -B -m unittest discover -s tests -v`; chạy một lần sau tích hợp, không fan-out cùng suite trong lúc đang edit.
2. Chạy package smoke IT-02; ghi actual command/exit/output, không gọi resource integrity là live behavior.
3. Chạy HTML/React walkthrough và visual checks; record findings, sửa observed defect và lặp path bị ảnh hưởng.
4. Report riêng: helper/core, package, HTML browser, React browser, DS comparison, Codex native, Claude native, Figma native. Mỗi mục chỉ pass khi đã exercise; external acceptance thiếu resource có trạng thái pending với prerequisite cụ thể.
5. Throwaway scripts/output phục vụ nghiệm thu được dọn khi xong; giữ evidence được chọn theo project/task contract. Không thêm permanent prose/source-text tests hoặc scaffold/mock demo để đạt gate.

# Research: PROTO-01 — Existing contracts and minimal web extension

## Scope and method

Inline research theo cấu hình project: đọc backlog, routing, workflow design/prototype, source/profile contracts, task schema/helper và tests hiện có. Không external research: đây là mở rộng workflow trong repo, không cần chọn dịch vụ bên ngoài hoặc xác minh backend/API.

## Findings

| ID | Evidence in repo | Observation | Consequence for spec |
|---|---|---|---|
| R-01 | [SKILL.md](../../../../SKILL.md), lines 8–19, 34–42 | Workflow dùng chung Codex/Claude; helper launcher độc lập CWD; prototype chỉ chạy khi yêu cầu explicit | Không tạo workflow riêng theo harness hoặc tự thêm interaction trong design/review |
| R-02 | [design workflow](../../../../references/design.md), lines 20–39, 62–73 | Profile/lessons, reference instance, reuse, semantic binding, scoped exceptions và render/readback đã là contract | Web kế thừa các invariant, dịch cách kiểm tra sang source/component và browser thay vì viết chuẩn DS cạnh tranh |
| R-03 | [project lifecycle](../../../../docs/project-kits.md), lines 3–5, 28–32, 72–83 | DS source độc lập destination; DESIGN.md, sources, profiles và lessons có authority khác nhau | Không cần ghi Figma để có web demo; DS không tự tạo product requirement; renderer không đổi platform |
| R-04 | [source adapters](../../../../docs/source-adapters.md), lines 12–26, 43–45, 63–72 | Registry giữ asset identity, provenance, precedence và coverage. Aliases được giữ nguyên, không tự resolve; component metadata không chứng minh có code/importability | Mapping DS là công việc agent có bằng chứng; không xây universal token compiler, không coi snapshot là thư viện React |
| R-05 | [task template](../../../../templates/task.json), lines 7–65 | Có delivery, target, flows, states, sourceDecisions, exceptions, designPlan và handoff; delivery mặc định figma_design | Tận dụng các field hiện có; task web phải chọn delivery explicit; không đổi template mặc định hoặc task lịch sử chỉ để thêm web |
| R-06 | [task schema](../../../../schemas/task.schema.json), lines 4–14, 52–57, 140–174 | target/designPlan/handoff là object mở; shared task identity/profile/lesson vẫn bắt buộc | Có thể thêm metadata web có điều kiện, không cần schema family mới hoặc migration toàn bộ |
| R-07 | [task helper](../../../../scripts/kkdesign_task.py), lines 77–140, 143–167 | begin kiểm profile/lesson/destination và planning; destination nhận fileKey hoặc destination; chỉ tạo task record | Giữ preflight chung. Thêm kiểm destination local cho delivery web, không bắt helper dựng UI |
| R-08 | [task helper](../../../../scripts/kkdesign_task.py), lines 245–291 | Delivered handoff đòi frameLinks hoặc blockedDisposition, checks/evidence và requirementStateMapping; handoff ghi qua task.json.tmp | Cần artifact-aware delivery gate. Không dùng fake Figma URL hoặc blockedDisposition để giả lập web handoff thành công |
| R-09 | [task helper](../../../../scripts/kkdesign_task.py), lines 51–74, 187–242 | check kiểm mọi JSON cạnh task.json như evidence; references task-relative, local phải tồn tại trong project, remote chỉ credential-free HTTPS | Artifact app/package.json phải nằm ngoài design/tasks. URL preview loopback là observation payload, không ghi thành remote evidence reference |
| R-10 | [foundation validator](../../../../scripts/kkdesign_core.py), lines 207–225, 240–283 | Mọi JSON dưới design/tasks được phân loại task/evidence; profile và lesson integrity được kiểm offline | Đặt source/artifact ở design/prototypes; cập nhật kiểm artifact refs trong core nếu mở rộng handoff, không để task check và foundation cho kết quả mâu thuẫn |
| R-11 | [task tests](../../../../tests/test_tasks.py), lines 48–139, 141–201 | Có regression cho stale review, no-overwrite, evidence hash/reference, delivery và Figma graph | Bổ sung test hành vi web và bảo toàn đường Figma; không test wording của instructions |
| R-12 | [compatibility](../../../../docs/compatibility.md), lines 18–23, 40–55; [manifest](../../../../manifest.json), lines 38–61, 63–96 | Dependency, tool access và evidence boundary phải được mô tả chính xác; resource mới cần được đóng gói | HTML không bị ép Node, web không bị ép Figma tool; reference mới phải vào requiredResources; không thêm browser provider bắt buộc |

## Recommended implementation boundary

1. Agent orchestration: parse prototype intent, read selected project, plan, generate/edit authorized artifact, observe browser, record evidence and handoff.
2. Python helper: nhận record dữ liệu, validate đường dẫn/contract, lưu evidence và handoff. Không execute command/package script từ record, không render, không tự pass DS hoặc flow.
3. Web output: HTML thuần hoặc React trong project đích. Reuse DS/code/runtime khi dùng được; tái hiện từ token/spec khi không có code, có provenance và exceptions.
4. Minimal data extension: delivery web explicit + local target.destination + handoff.artifacts có launch metadata. Các field flow/state/DS decision hiện có tiếp tục là planning record, không trở thành DSL renderer.
5. Single-writer workflow: không triển khai concurrency engine hoặc background generator. Begin không overwrite task; các ghi artifact và handoff phải dừng khi có xung đột, không tự retry ghi đè.

## Verification performed during specification drafting

- Đã đọc trực tiếp source/schema/tests kể trên; các nhận định về gate hiện tại dựa trên source, không phải browser hoặc native Figma observation.
- Đã thử probe disposable gọi helper qua materialized synthetic project, nhưng dừng trước begin vì interpreter thiếu `jsonschema`. Không có kết quả runtime về artifact-only handoff; không trình bày source inspection thành passing/failing native acceptance. Không thay code hoặc dependency project để phục vụ việc viết spec.
- Spec/test validators và cross-document checks được chạy sau khi lưu tài liệu; kết quả thực tế báo ở phần bàn giao, không suy ra feature đã triển khai.

## Open prerequisites for future acceptance

Feature sản phẩm thật, DS riêng của khách hàng, quyền Figma native và runtime/browser của từng harness không cần cho việc tạo spec. Khi triển khai, dùng fixture tổng hợp và ghi riêng capability/resource nào còn thiếu; không thay bằng dữ liệu riêng tư hoặc fabricated evidence.

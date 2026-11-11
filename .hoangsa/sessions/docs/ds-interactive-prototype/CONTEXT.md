# Context: PROTO-01 — Prototype tương tác bám DS của project

## Task Type

feat — nâng cấp workflow agent, contract bàn giao và nghiệm thu prototype HTML/React. Lượt làm việc này chỉ tạo spec, không triển khai feature, không commit hoặc publish.

## Language

Tiếng Việt.

## Spec Language

Tiếng Việt; giữ tên section/field theo template và contract hiện có.

## Tech Stack

Python 3.9+ và `requirements.txt` cho helpers; Markdown cho workflow; HTML/CSS/JavaScript hoặc React cho artifact được tạo trong project đích. Browser và môi trường React là capability theo từng route, không phải dependency toàn cục của skill.

## User Input

> Tạo spec doc từ @.hoangsa/sessions/docs/ds-interactive-prototype/BACKLOG.md đi

Nguồn requirements: [BACKLOG.md](BACKLOG.md), task PROTO-01 và AC-01–AC-10. Backlog giữ nguyên làm nguồn yêu cầu, không đổi trạng thái thành implemented hoặc đánh dấu acceptance đã pass khi chỉ tạo spec.

## Discussion Log

Các quyết định đã có từ cuộc thảo luận trước, không hỏi lại:

1. Prototype phục vụ demo và giúp dev/team/stakeholders hiểu flow feature từ mong muốn PM/PO.
2. Mọi đích Figma, HTML hoặc React đều dùng DS đã init trong project để demo sát app hiện tại.
3. Không đặt nặng API thật, backend hoặc kiến trúc production. Dữ liệu giả và logic mô phỏng phù hợp nếu được ghi rõ.
4. HTML và React là hai lựa chọn được hỗ trợ; mỗi yêu cầu chỉ cần đầu ra phù hợp, không buộc tạo cả hai.
5. Giữ ranh giới prototype explicit; design/review không tự thêm interaction.

## Decisions Made

| Decision | Reason | Type |
|---|---|---|
| Giữ mục tiêu demo feature, không biến thành production implementation | Quyết định chủ sở hữu và backlog | LOCKED |
| DS/project context là nguồn chuẩn, không thay DS vì tiện sinh code | Quyết định chủ sở hữu và backlog | LOCKED |
| Giữ route prototype chung và đường Figma hiện có | AC-01, AC-10 | LOCKED |
| Dùng lifecycle task/evidence/lesson hiện có; mở rộng artifact handoff cho web | Contract hiện có đã hỗ trợ destination, nhưng handoff còn phụ thuộc frameLinks | FLEXIBLE — thiết kế kỹ thuật đề xuất trong DESIGN-SPEC |
| Agent dựng code; helpers chỉ record/validate, không thêm code generator hoặc tự chạy lệnh từ record | Convention hiện tại và giới hạn framework mới trong backlog | FLEXIBLE — thiết kế kỹ thuật đề xuất |
| Phân biệt platform sản phẩm với renderer HTML/React | Profile/lesson áp dụng theo platform sản phẩm, không theo cách xem demo | FLEXIBLE — thiết kế kỹ thuật đề xuất |
| Không khóa bundler/UI library toàn cục; dùng môi trường phù hợp project | Backlog chưa khóa tooling; tránh thêm dependency không phục vụ demo | FLEXIBLE |

LOCKED là quyết định sản phẩm; FLEXIBLE là baseline kỹ thuật đã được chủ sở hữu duyệt ở bước lập plan. Có thể điều chỉnh chi tiết triển khai tương đương, không tự thay outcome hoặc phạm vi đã chốt.

## Out of Scope

Theo [BACKLOG.md](BACKLOG.md): backend/auth/API thật, production architecture/readiness, Figma-to-code compiler hoặc sync hai chiều, renderer framework mới, coverage ngoài scope demo, hosting/deploy/analytics, thay DS hoặc bỏ route Figma, và cam kết số liệu tiết kiệm chưa đo.

## Review and delivery boundary

- Tài liệu spec được viết cạnh backlog theo vị trí người dùng đã chỉ định; không tạo session song song hoặc đổi branch cho một yêu cầu chỉ viết tài liệu.
- DESIGN-SPEC và TEST-SPEC đã được chủ sở hữu duyệt để lập plan. Approval và validate tài liệu không chứng minh feature đã hoạt động hoặc thay thế nghiệm thu.
- Không tự commit; cấu hình project có `auto_plate=false`. Không sync external task manager; cấu hình hiện tại chưa có provider.
- Lesson được áp dụng: thay đổi capability/routing phải cập nhật các guide đang hoạt động cùng lượt, không pin prose bằng test; core/helper checks và nghiệm thu browser/native phải được phân biệt.

## Approval and planning request

Ngày 2026-11-11, chủ sở hữu xác nhận:

> Duyệt nhé. Lên plan triển khai đi em

- Scope hiện tại: ghi nhận approval và tạo plan có dependency, coverage/test cases và acceptance; chưa chạy implementation.
- Giữ docs và plan cạnh backlog; không đổi branch, commit, publish hoặc sync task manager khi chưa được yêu cầu.
- Chạy local/core/package/browser verification theo plan khi triển khai. Native Figma và harness acceptance cần quyền/tool được theo dõi riêng, không mặc định block review/tích hợp code đã kiểm chứng local; không báo pass khi chưa thực hiện.

## Execution request and outcome

Chủ sở hữu tiếp tục yêu cầu triển khai plan trong chính thư mục này. Phạm vi
chỉ-lập-plan ở mục trước là lịch sử của yêu cầu chuẩn bị, không còn là trạng thái
thực thi hiện tại.

- Đã triển khai shared routing/schema/core/task workflow và synthetic inputs;
  không thêm generator, provisioning hoặc backend integration.
- Core pass 165 unittest; package relocation và actual CLI lifecycle pass.
  HTML, React reuse-code và React token-only/profile ios đã được walkthrough,
  capture và kiểm integrity bằng selected disposable projects.
- Review đã sửa cả compatibility defect khi React dependency tree làm refresh
  fail. Refinement và bằng chứng nằm tại `acceptance/local-integrity.md`.
- Kết luận và mapping REQ/AC: [acceptance/INTEGRATION.md](acceptance/INTEGRATION.md).
  Full native browser/Figma và human design approval chưa hoàn tất; native scope
  deviations được giữ rõ, không đổi thành pass. Không tự commit/publish.

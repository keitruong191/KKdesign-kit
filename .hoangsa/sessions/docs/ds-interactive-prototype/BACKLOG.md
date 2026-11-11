# KKdesign-kit — Improvement: Prototype tương tác bám DS của project

## Strategic context

**Product:** KKdesign-kit.

**Người sử dụng:** PM/PO và designer chuẩn bị demo feature mới; dev, team và stakeholders xem và thảo luận demo.

**Vấn đề:** Theo phản hồi của chủ sở hữu, dựng prototype bằng Figma đang tốn quota nhưng chưa đem lại đủ giá trị tương tác để truyền đạt flow và feature mới.

**Hướng đã chốt:** Prototype là công cụ truyền đạt và thảo luận thiết kế feature, không phải bản triển khai kỹ thuật thu nhỏ. Bất kể đầu ra là Figma, HTML hay React, prototype dùng DS đã init trong project để người xem hình dung feature trong app hiện tại. Tương tác HTML/React phục vụ việc demo; giảm phụ thuộc quota Figma là lợi ích vận hành, không thay thế mục tiêu này.

**Nguồn yêu cầu:** Các quyết định PM/PO đã xác nhận trong cuộc thảo luận với chủ sở hữu. Chưa có mockup hoặc feature sản phẩm cụ thể được chỉ định làm đầu vào triển khai.

**Trạng thái:** Backlog — hướng sản phẩm đã chốt; chưa triển khai. Tài liệu này là task improvement, không phải DESIGN-SPEC/TEST-SPEC hoặc kế hoạch kỹ thuật đã được phê duyệt. Chưa gán estimate, assignee hoặc lịch triển khai.

**Lưu ý hiện trạng:** Đây là snapshot yêu cầu trước triển khai; checklist và quyết định bên dưới giữ nguyên mốc đó. Kết quả triển khai, verification và giới hạn nghiệm thu hiện tại nằm trong [acceptance/INTEGRATION.md](acceptance/INTEGRATION.md).

## PROTO-01 — Tạo prototype HTML/React dùng DS đã init để demo feature mới trong ngữ cảnh sản phẩm

### Why

PM/PO cần truyền đạt mong muốn của feature bằng một flow có thể thao tác, để dev, team và stakeholders hiểu người dùng làm gì và hệ thống phản hồi thế nào. DS và context của project giúp demo mang nhận diện, cấu trúc và cách sử dụng quen thuộc của app hiện tại, thay vì một giao diện generic đứng ngoài sản phẩm.

### What

Nâng cấp route `prototype` của KKdesign-kit để có thể tạo và thay đổi prototype HTML/CSS/JavaScript hoặc React bên cạnh khả năng Figma hiện có. Từ brief PM/PO, context sản phẩm và DS đã init, dựng các màn hình, trạng thái và tương tác đủ để trình bày câu chuyện feature đã thống nhất. Không bắt buộc tạo frame hoặc ghi vào Figma trước khi dựng prototype web nếu nguồn DS/context hiện có đã đủ cho demo.

Kế thừa kỷ luật DS của route `design`: resolve profile và lessons, inspect reference phù hợp với nguồn hiện có, reuse component/token khi khả dụng, ghi rõ ngoại lệ và kiểm tra giao diện thực tế. Dùng dữ liệu tổng hợp và logic mô phỏng để demo; bàn giao cách mở/chạy, flow cần trình bày, cách bắt đầu lại và phần đang mô phỏng. Không mặc định yêu cầu API thật hoặc code production-ready.

### Acceptance Criteria

- [ ] **AC-01 — Đủ lựa chọn đầu ra:** Với yêu cầu prototype rõ ràng, người dùng có thể chọn HTML/CSS/JavaScript hoặc React; route Figma vẫn sử dụng được. Không tự tạo interaction như tác dụng phụ của `design` hoặc `review`.
- [ ] **AC-02 — Bám ý định PM/PO:** Trước khi dựng, task ghi rõ mục tiêu feature, người dùng, điểm bắt đầu/kết thúc, flow chính, các nhánh/trạng thái quan trọng cần demo và những phần loại trừ. Điểm chưa rõ ảnh hưởng đến câu chuyện demo được làm rõ hoặc ghi thành gap cụ thể, không tự invent yêu cầu sản phẩm.
- [ ] **AC-03 — DS của project là nguồn chuẩn:** Prototype sử dụng DS đã init trong project, không tự thay bằng một bộ UI khác vì tiện. Có thể truy nguyên các component, variant, token/style quan trọng về nguồn project; nếu có component code phù hợp thì ưu tiên reuse. Không cần DS phải có sẵn component code mới được dựng demo web.
- [ ] **AC-04 — Nhận diện được app hiện tại:** Giao diện render thực tế được đối chiếu với DS và reference sản phẩm có trong scope, gồm layout/navigation khi liên quan, typography, màu sắc, spacing và component states cần demo. Phần tái dựng, thiếu nguồn hoặc ngoại lệ được ghi rõ cùng phạm vi; không tuyên bố độ khớp tuyệt đối khi chưa kiểm chứng.
- [ ] **AC-05 — Tương tác phục vụ câu chuyện feature:** Trên browser, người xem đi được flow chính và các nhánh đã chốt bằng thao tác thực, nhận đúng phản hồi cần demo và không gặp dead end ngoài chủ đích. Có thể dùng local state, dữ liệu giả và kết quả mô phỏng; không yêu cầu kết nối backend hay API thật để đạt tiêu chí này.
- [ ] **AC-06 — Demo lặp lại được:** Có cách bắt đầu lại về trạng thái ban đầu; với cùng scenario đã chọn, trạng thái và phản hồi đủ nhất quán để present lại. Back/cancel và giữ/reset dữ liệu thực hiện theo hành vi đã chốt cho flow, không áp một quy tắc chung ngoài brief.
- [ ] **AC-07 — Kiểm chứng đúng bề mặt:** Mở prototype thật trong browser, thao tác các scenario đã chốt và kiểm tra render ở viewport mục tiêu. Ghi evidence quan sát được và giới hạn; build/schema check hoặc screenshot đơn lẻ không thay cho bằng chứng flow đã chạy.
- [ ] **AC-08 — Bàn giao để trình bày:** Handoff có artifact/entry point, cách mở hoặc chạy cùng dependency cần thiết, kịch bản demo, cách reset, phần mô phỏng và câu hỏi còn mở. Người nhận có thể mở và đi lại flow theo hướng dẫn trong môi trường đã công bố; không gọi prototype là production-ready.
- [ ] **AC-09 — Giữ ranh giới project và quyền chia sẻ:** Artifact nằm trong project đích đã chọn, không ghi vào thư mục skill đã cài hoặc ghi đè nội dung ngoài scope. Không tự publish, deploy, chia sẻ ra ngoài hoặc gọi dịch vụ thật. Ví dụ/evidence được commit trong repo này chỉ dùng dữ liệu tổng hợp, không chứa credentials hoặc dữ liệu khách hàng.
- [ ] **AC-10 — Workflow nhất quán:** Menu, routing, hướng dẫn prototype/design liên quan và tài liệu dependency/giới hạn phản ánh đúng năng lực đã triển khai, dùng chung contract project của Codex và Claude Code. Core Python giữ yêu cầu Python 3.9+ và `requirements.txt`; dependency phục vụ React chỉ được yêu cầu cho đường chạy cần nó, không thành điều kiện toàn cục cho Figma/HTML.

### Out of Scope

- Backend, database, authentication/authorization thật hoặc integration API thật, trừ khi có yêu cầu riêng.
- Kiến trúc production, code sẵn sàng đưa vào production hoặc đồng bộ hai chiều giữa Figma và code.
- Chuyển đổi tự động toàn bộ Figma thành HTML/React hoặc xây một framework render mới.
- Bao phủ mọi business rule, edge case, thiết bị hoặc breakpoint ngoài phạm vi demo đã chốt.
- Tự publish/deploy, nền tảng hosting mới, analytics hoặc đo lường hành vi người xem.
- Thay thế route Figma hoặc sửa DS của project ngoài yêu cầu.
- Cam kết số liệu tiết kiệm quota, thời gian hoặc hiệu quả truyền đạt khi chưa đo.

### Verification khi triển khai

- Dùng một feature tổng hợp có flow nhiều bước, ít nhất một nhánh thay thế có ý nghĩa và cơ chế bắt đầu lại; dựng và chạy thực tế ở cả HTML và React để chứng minh hai lựa chọn, không chỉ kiểm tra instructions.
- Dùng DS tổng hợp được init trong project nghiệm thu; đối chiếu render, component/token nguồn và scenario theo AC-02–AC-07. Kiểm tra cả nguồn DS có component code và trường hợp chỉ có token/spec/reference để không ép điều kiện code library lên mọi project.
- Xác nhận route Figma và ranh giới `design`/`review` không bị thay đổi ngoài scope. Nếu thiếu quyền/tool Figma thật, ghi riêng phần nghiệm thu chưa thực hiện, không suy từ kiểm tra offline rằng native behavior đã pass.
- Nếu thay đổi core: chạy `python3 -m unittest discover -s tests -v`; bổ sung/sửa test cho boundary hoặc hành vi consumer-visible thực sự thay đổi. Không thêm test chỉ pin wording hoặc cấu trúc prose của instructions.
- Evidence triển khai phải phân biệt code/helper checks, browser demo, đối chiếu DS và nghiệm thu cần người/resource ngoài. Chỉ tạo task ở bước hiện tại, chưa tuyên bố các kiểm chứng này đã chạy.

### Implementation notes — Chưa khóa thiết kế kỹ thuật

- Chưa chốt cú pháp chọn target, cấu trúc artifact, bundler hoặc thư viện UI. Chọn theo convention project và phạm vi demo khi lập spec; không coi ví dụ cú pháp trong brainstorm là command hiện có.
- Reuse contract task/evidence/lesson hiện có nếu phù hợp; chỉ thay schema/helper khi cần cho hành vi thực, không ép metadata canvas/Figma lên web hoặc tạo contract cạnh tranh.
- Người dùng không cần bản sao HTML và React của cùng demo; hai đường chạy được hỗ trợ để chọn đầu ra phù hợp cho từng yêu cầu.

## References trong repo

- [Design workflow — planning, reuse, semantic bindings, exceptions và verification](../../../../references/design.md)
- [Prototype workflow hiện tại — explicit request, scenario, simulated behavior và evidence](../../../../references/prototype.md)
- [Skill routing](../../../../SKILL.md)
- [Command availability](../../../../references/commands.md)
- [Shared project contracts](../../../../docs/contracts.md)
- [Task validation và lifecycle helper](../../../../scripts/kkdesign_task.py)

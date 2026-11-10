# Design review guidance attribution

## Source and adaptation record

Recorded before incorporating adapted material into the bundled review guidance.

- **Source:** Impeccable, `pbakaus/impeccable`, `skill/reference/critique.md` and the related `skill/reference/operate.md`, `skill/reference/mode-operate.md`, `skill/reference/ios.md`, `skill/reference/android.md`, `skill/reference/audit.native.md`, and `skill/reference/adapt.native.md`.
- **Version:** 4.8.0, tag `skill-v4.8.0`, commit `414603bf14c7a344edb466bb1f85690c77ce8b7d` (verified signed release commit; GitHub release dated 2026-10-26).
- **Author / copyright holder:** Paul Bakaus; copyright notice in upstream license: Copyright 2025 Paul Bakaus.
- **License:** Apache License 2.0. The full license text below follows upstream `LICENSE` at the exact release tag. Upstream `NOTICE.md` also attributes the iOS/Android references to ehmo's MIT-licensed `platform-design-skills`; its notice and inherited license are retained below.
- **Authoritative provenance:** [release tag](https://github.com/pbakaus/impeccable/releases/tag/skill-v4.8.0), [source critique guide](https://github.com/pbakaus/impeccable/blob/skill-v4.8.0/skill/reference/critique.md), [source license](https://github.com/pbakaus/impeccable/blob/skill-v4.8.0/LICENSE), [source skill metadata](https://github.com/pbakaus/impeccable/blob/skill-v4.8.0/skill/SKILL.src.md).
- **Material adapted:** the concepts of separating strengths from prioritized actionable findings, evaluating hierarchy and cognitive load, using heuristic lenses (including error recovery and help), testing personas against concrete tasks, and inspecting the emotional journey. Related native guidance informed the rule to assess platform conventions separately.
- **Adaptations:** rewritten and narrowed for independent, agent-orchestrated design reviews in KKdesign-kit; no Impeccable executable, launcher, detector, hook, overlay, storage, workflow, prompt, or file format is required. Added KKdesign-kit-specific distinctions for product refs versus design-system authority, scoped lessons, Figma canvas versus source/runtime evidence, native platform evidence, mode and accessibility/state coverage, long content, severity/evidence/recommendation/verification fields, applicable-only scoring, and synthetic fixture caveats. Findings default to recommendations; review never edits or creates prototypes.
- **Changes:** This document and all bundled guidance/resources in this review package are adaptations, not verbatim copies. The full upstream license text is reproduced below as required for redistribution.

## Upstream NOTICE.md

The following notice is retained from
[Impeccable 4.8.0 NOTICE.md](https://github.com/pbakaus/impeccable/blob/skill-v4.8.0/NOTICE.md).
Its platform-source attribution applies to the selectively adapted native lenses.
The upstream tag is unsigned; the referenced release **commit** is marked verified
by GitHub. Neither property is a signature on this KKdesign-kit distribution.

> # Third-Party Notices
>
> This project includes content derived from third-party work, used under the terms of its original license.
>
> ## Platform Design Skills
>
> The `skill/reference/ios.md` and `skill/reference/android.md` platform reference files are distilled from ehmo's `platform-design-skills` (Apple Human Interface Guidelines and Material Design 3 rules), rewritten in Impeccable's voice.
>
> **Original work:** https://github.com/ehmo/platform-design-skills
> **Original license:** MIT
> **Author:** ehmo

## Inherited platform-design-skills license

Source: [ehmo/platform-design-skills LICENSE](https://github.com/ehmo/platform-design-skills/blob/main/LICENSE),
Git blob `14fac913ccf80234b1848540089a3bbcb6e5283d`. Impeccable's notice does not pin
the original platform-source revision; no exact ancestry revision is asserted here.
The current upstream copyright and permission notice are retained verbatim:

```text
MIT License

Copyright (c) 2026

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Apache License, Version 2.0

Apache License
                           Version 2.0, January 2004
                        http://www.apache.org/licenses/

   TERMS AND CONDITIONS FOR USE, REPRODUCTION, AND DISTRIBUTION

   1. Definitions.

      "License" shall mean the terms and conditions for use, reproduction,
      and distribution as defined by Sections 1 through 9 of this document.

      "Licensor" shall mean the copyright owner or entity authorized by
      the copyright owner that is granting the License.

      "Legal Entity" shall mean the union of the acting entity and all
      other entities that control, are controlled by, or are under common
      control with that entity. For the purposes of this definition,
      "control" means (i) the power, direct or indirect, to cause the
      direction or management of such entity, whether by contract or
      otherwise, or (ii) ownership of fifty percent (50%) or more of the
      outstanding shares, or (iii) beneficial ownership of such entity.

      "You" (or "Your") shall mean an individual or Legal Entity
      exercising permissions granted by this License.

      "Source" form shall mean the preferred form for making modifications,
      including but not limited to software source code, documentation
      source, and configuration files.

      "Object" form shall mean any form resulting from mechanical
      transformation or translation of a Source form, including but
      not limited to compiled object code, generated documentation,
      and conversions to other media types.

      "Work" shall mean the work of authorship, whether in Source or
      Object form, made available under the License, as indicated by a
      copyright notice that is included in or attached to the work
      (an example is provided in the Appendix below).

      "Derivative Works" shall mean any work, whether in Source or Object
      form, that is based on (or derived from) the Work and for which the
      editorial revisions, annotations, elaborations, or other modifications
      represent, as a whole, an original work of authorship. For the purposes of
      this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to the Licensor for inclusion in the Work by the copyright
      owner or by an individual or Legal Entity authorized to submit on
      behalf of the copyright owner. For the purposes of this definition,
      "submitted" means any form of electronic, verbal, or written
      communication sent to the Licensor or its representatives, including
      but not limited to communication on electronic mailing lists, source
      code control systems, and issue tracking systems that are managed by,
      or on behalf of the Licensor for the purpose of discussing and
      improving the Work, but excluding communication that is conspicuously
      marked or otherwise designated in writing by the copyright owner as
      "Not a Contribution."

      "Contributor" shall mean Licensor and any individual or Legal Entity
      on behalf of whom a Contribution has been received by Licensor and
      subsequently incorporated within the Work.

   2. Grant of Copyright License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      copyright license to reproduce, prepare Derivative Works of,
      publicly display, publicly perform, sublicense, and distribute the
      Work and such Derivative Works in Source or Object form.

   3. Grant of Patent License. Subject to the terms and conditions of
      this License, each Contributor hereby grants to You a perpetual,
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable (except
      as stated in this section) patent license to make, have made, use, offer
      to sell, sell, import, and otherwise transfer the Work, where such
      license applies only to those patent claims licensable by such
      Contributor that are necessarily infringed by their Contribution(s)
      alone or by combination of their Contribution(s) with the Work to which
      such Contribution(s) was submitted. If You institute patent litigation
      against any entity (including a cross-claim or counterclaim in a lawsuit)
      alleging that the Work or a Contribution incorporated within the Work
      constitutes direct or contributory patent infringement, then any patent
      licenses granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the Work or
      Derivative Works thereof in any medium, with or without modifications,
      and in Source or Object form, provided that You meet the following
      conditions:

      (a) You must give any other recipients of the Work or Derivative Works
          a copy of this License; and

      (b) You must cause any modified files to carry prominent notices stating
          that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works that You
          distribute, all copyright, patent, trademark, and attribution notices
          from the Source form of the Work, excluding those notices that do not
          pertain to any part of the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its distribution,
          then any Derivative Works that You distribute must include a readable
          copy of the attribution notices contained within such NOTICE file,
          excluding those notices that do not pertain to any part of the
          Derivative Works, in at least one of the following places: within a
          NOTICE text file distributed as part of the Derivative Works; within
          the Source form or documentation, if provided along with the
          Derivative Works; or, within a display generated by the Derivative
          Works, if and wherever such third-party notices normally appear. The
          contents of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution notices
          within Derivative Works that You distribute, alongside or as an
          addendum to the NOTICE text from the Work, provided that such
          additional attribution notices cannot be construed as modifying the
          License.

      You may add Your own copyright statement to Your modifications and may
      provide additional or different license terms and conditions for use,
      reproduction, or distribution of Your modifications, or for any such
      Derivative Works as a whole, provided Your use, reproduction, and
      distribution of the Work otherwise complies with the conditions stated
      in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work by You
      to the Licensor shall be under the terms and conditions of this License,
      without any additional terms or conditions. Notwithstanding the above,
      nothing herein shall supersede or modify the terms of any separate
      license agreement you may have executed with Licensor regarding such
      Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or agreed to
      in writing, Licensor provides the Work (and each Contributor provides
      its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS
      OF ANY KIND, either express or implied, including, without limitation,
      any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY,
      or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for
      determining the appropriateness of using or redistributing the Work and
      assume any risks associated with Your exercise of permissions under this
      License.

   8. Limitation of Liability. In no event and under no legal theory, whether
      in tort (including negligence), contract, or otherwise, unless required
      by applicable law (such as deliberate and grossly negligent acts) or
      agreed to in writing, shall any Contributor be liable to You for damages,
      including any direct, indirect, special, incidental, or consequential
      damages of any character arising as a result of this License or out of
      the use or inability to use the Work (including but not limited to
      damages for loss of goodwill, work stoppage, computer failure or
      malfunction, or any and all other commercial damages or losses), even if
      such Contributor has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing the Work
      or Derivative Works thereof, You may choose to offer, and charge a fee
      for, acceptance of support, warranty, indemnity, or other liability
      obligations and/or rights consistent with this License. However, in
      accepting such obligations, You may act only on Your own behalf and on
      Your sole responsibility, not on behalf of any other Contributor, and
      only if You agree to indemnify, defend, and hold each Contributor
      harmless for any liability incurred by, or claims asserted against, such
      Contributor by reason of your accepting any such warranty or additional
      liability.

   END OF TERMS AND CONDITIONS

   Copyright 2025 Paul Bakaus

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

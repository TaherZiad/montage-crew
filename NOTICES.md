# Third-party notices

montage-crew's own files are covered by `LICENSE`. The files below are made by other people and keep **their own licences**. This file lists each one, what you may do with it, and the notice its licence asks us to keep. The full licence texts are at the end of this file, or in the folder named for each item.

Short version: everything here may be shared inside this free package, and you may use all of it in videos you sell or monetise. Two things are **not** included in the package; they are downloaded when you install (see section 6).

---

## 1. Fonts: SIL Open Font License 1.1

Folder: `assets/fonts/` (28 font files, 19 families, unmodified from Google Fonts, github.com/google/fonts/tree/main/ofl).
Licence and copyright notice for each family: `assets/fonts/OFL/<Family>-OFL.txt`.

| family | files | licence file |
|---|---|---|
| Alexandria | Alexandria-VF.ttf | OFL/Alexandria-OFL.txt |
| Almarai | Almarai-ExtraBold.ttf | OFL/Almarai-OFL.txt |
| Amiri | Amiri-Bold.ttf | OFL/Amiri-OFL.txt |
| Anton | Anton-Regular.ttf | OFL/Anton-OFL.txt |
| Aref Ruqaa | ArefRuqaa-Regular.ttf, ArefRuqaa-Bold.ttf | OFL/ArefRuqaa-OFL.txt |
| Baloo Bhaijaan 2 | BalooBhaijaan2-VF.ttf | OFL/BalooBhaijaan2-OFL.txt |
| Cairo | Cairo-VF.ttf | OFL/Cairo-OFL.txt |
| Changa | Changa-VF.ttf | OFL/Changa-OFL.txt |
| El Messiri | ElMessiri-VF.ttf | OFL/ElMessiri-OFL.txt |
| IBM Plex Sans Arabic | IBMPlexSansArabic-{ExtraLight,Light,Regular,SemiBold,Bold}.ttf | OFL/IBMPlexSansArabic-OFL.txt |
| JetBrains Mono | JetBrainsMono-VF.ttf | OFL/JetBrainsMono-OFL.txt |
| Lalezar | Lalezar-Regular.ttf | OFL/Lalezar-OFL.txt |
| Lemonada | Lemonada-VF.ttf | OFL/Lemonada-OFL.txt |
| Marhey | Marhey-VF.ttf | OFL/Marhey-OFL.txt |
| Montserrat | Montserrat-VF.ttf | OFL/Montserrat-OFL.txt |
| Noto Kufi Arabic | NotoKufiArabic-VF.ttf | OFL/NotoKufiArabic-OFL.txt |
| Readex Pro | ReadexPro-VF.ttf | OFL/ReadexPro-OFL.txt |
| Rubik | Rubik-VF.ttf | OFL/Rubik-OFL.txt |
| Tajawal | Tajawal-{Light,Regular,Bold,ExtraBold,Black}.ttf | OFL/Tajawal-OFL.txt |

What the OFL allows: use the fonts in any video, including commercial ones, and pass them on with software. Keep each `OFL.txt` with the fonts. Don't sell the fonts on their own. A modified font may not use the original's Reserved Font Name. https://openfontlicense.org/open-font-license-official-text/

## 2. Sound effects: CC0 1.0 (public domain)

Folder: `assets/sfx/` (84 files). All are CC0 1.0: https://creativecommons.org/publicdomain/zero/1.0/
- 71 files from Freesound.org. The CC0 licence of each one was checked on its own page on 2026-10-13. We ship the HQ preview MP3, trimmed and normalised.
- 13 files from Kenney (kenney.nl) packs: Interface Sounds, UI Audio, Sci-fi Sounds, Impact Sounds. Each pack's `License.txt` says CC0.

CC0 needs no credit. Each file's author and source page are still listed in `assets/sfx/CREDITS.md` and `assets/sfx/manifest.json`. CC0 doesn't mean those authors endorse this package.

## 3. Arabic motion templates: Apache License 2.0

Folder: `assets/templates/ar/` (8 files). They are adapted from the HyperFrames registry (https://github.com/heygen-com/hyperframes, `registry/`), copyright the HyperFrames authors (HeyGen), licensed under the Apache License 2.0.
**Changes made by montage-crew:** Arabic text, right-to-left layout, Arabic fonts, timings and colours.

| our file | HyperFrames registry item |
|---|---|
| ar-editorial-flash-overlay.html | registry/blocks/editorial-flash-overlay |
| ar-hw-scribble-transition.html | registry/blocks/hw-scribble-transition |
| ar-lt-mask-reveal.html | registry/blocks/lt-mask-reveal |
| ar-mk-clone-wall-transition.html | registry/blocks/mk-clone-wall-transition |
| ar-organic-light-leak-overlay.html | registry/blocks/organic-light-leak-overlay |
| ar-clip-wipe.html | registry/components/caption-clip-wipe |
| ar-weight-shift.html | registry/components/caption-weight-shift |
| ar-whip-pan-cut.html | registry/components/whip-pan-cut |

The full Apache 2.0 text is in section 7.1. The HyperFrames repository has no NOTICE file.

## 4. Reference skill texts: MIT

Folder: `references/external/`. Each sub-folder keeps its original `LICENSE` file, which is the notice MIT asks us to keep.

| folder | copyright |
|---|---|
| AIEV | Copyright (c) 2026 noti.vn |
| bang-motion | Copyright (c) 2026 Bang Tutorial |
| hyperframes-student-kit | Copyright (c) 2026 Nate Herk |
| iart-tiktok-video-skills | Copyright (c) 2026 iart.ai |
| koubo-edit | Copyright (c) 2026 koubo-edit contributors |
| opus-video-skills | Copyright (c) 2026 tuzhechen2005 (only the kinetic-reel text files are included; the template code that file mentions is not) |
| video-use | Copyright (c) 2026 Browser Use |

## 5. Scripts derived from video-ad-editor: MIT

`scripts/beat.py` is copied from, and `scripts/story.py` is ported from, video-ad-editor v3.8 (https://github.com/majedphotos/video-ad-editor). Copyright (c) 2026 Majed Alzaabi, MIT License. The full text with that copyright line is in section 7.2.

## 6. Not included: downloaded when you install or first use

These files are **not** in the ZIP. `scripts/fetch_assets.py` or the tools themselves download them from the original source, so you get them under their own licence directly from the publisher.

- **GSAP 3.14.2**: not included. Downloaded at install from jsDelivr (https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js) with a SHA-256 check. (c) GreenSock/Webflow, Standard "No Charge" License https://gsap.com/standard-license; by installing you accept it. The templates in `assets/templates/ar/` also load it from that jsDelivr URL.
- **RobustVideoMatting model** (`rvm_mobilenetv3_fp32.onnx`, about 15 MB): not included. Downloaded at install from https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx. The RobustVideoMatting code is GPL-3.0 (https://github.com/PeterL1n/RobustVideoMatting); the repository gives no separate licence for the model file. `scripts/matte.py` only loads the model through onnxruntime and contains no RobustVideoMatting code.
- **Whisper speech model** (faster-whisper large-v3 / medium / small, CTranslate2 conversions by Systran): not included. Downloaded at install from Hugging Face (https://huggingface.co/Systran) at a pinned revision with a SHA-256 check. MIT License (model card); the Whisper weights are by OpenAI.
- **Python packages** (faster-whisper, onnxruntime, opencv-python, numpy, scipy, and others): installed by pip under their own licences.
- **Logos, icons and photos** that `scripts/assets.py` fetches for a video (Wikimedia Commons CC0/PD/CC BY only, LobeHub icons, Microsoft Fluent Emoji (MIT), ambientCG): each keeps its own licence. Brand logos stay their owners' trademarks; show them, but don't use them as your own brand.

---

## 7. Full licence texts

### 7.1 Apache License 2.0 (applies to assets/templates/ar/)

```

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
      represent, as a whole, an original work of authorship. For the purposes
      of this License, Derivative Works shall not include works that remain
      separable from, or merely link (or bind by name) to the interfaces of,
      the Work and Derivative Works thereof.

      "Contribution" shall mean any work of authorship, including
      the original version of the Work and any modifications or additions
      to that Work or Derivative Works thereof, that is intentionally
      submitted to Licensor for inclusion in the Work by the copyright owner
      or by an individual or Legal Entity authorized to submit on behalf of
      the copyright owner. For the purposes of this definition, "submitted"
      means any form of electronic, verbal, or written communication sent
      to the Licensor or its representatives, including but not limited to
      communication on electronic mailing lists, source code control systems,
      and issue tracking systems that are managed by, or on behalf of, the
      Licensor for the purpose of discussing and improving the Work, but
      excluding communication that is conspicuously marked or otherwise
      designated in writing by the copyright owner as "Not a Contribution."

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
      worldwide, non-exclusive, no-charge, royalty-free, irrevocable
      (except as stated in this section) patent license to make, have made,
      use, offer to sell, sell, import, and otherwise transfer the Work,
      where such license applies only to those patent claims licensable
      by such Contributor that are necessarily infringed by their
      Contribution(s) alone or by combination of their Contribution(s)
      with the Work to which such Contribution(s) was submitted. If You
      institute patent litigation against any entity (including a
      cross-claim or counterclaim in a lawsuit) alleging that the Work
      or a Contribution incorporated within the Work constitutes direct
      or contributory patent infringement, then any patent licenses
      granted to You under this License for that Work shall terminate
      as of the date such litigation is filed.

   4. Redistribution. You may reproduce and distribute copies of the
      Work or Derivative Works thereof in any medium, with or without
      modifications, and in Source or Object form, provided that You
      meet the following conditions:

      (a) You must give any other recipients of the Work or
          Derivative Works a copy of this License; and

      (b) You must cause any modified files to carry prominent notices
          stating that You changed the files; and

      (c) You must retain, in the Source form of any Derivative Works
          that You distribute, all copyright, patent, trademark, and
          attribution notices from the Source form of the Work,
          excluding those notices that do not pertain to any part of
          the Derivative Works; and

      (d) If the Work includes a "NOTICE" text file as part of its
          distribution, then any Derivative Works that You distribute must
          include a readable copy of the attribution notices contained
          within such NOTICE file, excluding those notices that do not
          pertain to any part of the Derivative Works, in at least one
          of the following places: within a NOTICE text file distributed
          as part of the Derivative Works; within the Source form or
          documentation, if provided along with the Derivative Works; or,
          within a display generated by the Derivative Works, if and
          wherever such third-party notices normally appear. The contents
          of the NOTICE file are for informational purposes only and
          do not modify the License. You may add Your own attribution
          notices within Derivative Works that You distribute, alongside
          or as an addendum to the NOTICE text from the Work, provided
          that such additional attribution notices cannot be construed
          as modifying the License.

      You may add Your own copyright statement to Your modifications and
      may provide additional or different license terms and conditions
      for use, reproduction, or distribution of Your modifications, or
      for any such Derivative Works as a whole, provided Your use,
      reproduction, and distribution of the Work otherwise complies with
      the conditions stated in this License.

   5. Submission of Contributions. Unless You explicitly state otherwise,
      any Contribution intentionally submitted for inclusion in the Work
      by You to the Licensor shall be under the terms and conditions of
      this License, without any additional terms or conditions.
      Notwithstanding the above, nothing herein shall supersede or modify
      the terms of any separate license agreement you may have executed
      with Licensor regarding such Contributions.

   6. Trademarks. This License does not grant permission to use the trade
      names, trademarks, service marks, or product names of the Licensor,
      except as required for reasonable and customary use in describing the
      origin of the Work and reproducing the content of the NOTICE file.

   7. Disclaimer of Warranty. Unless required by applicable law or
      agreed to in writing, Licensor provides the Work (and each
      Contributor provides its Contributions) on an "AS IS" BASIS,
      WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
      implied, including, without limitation, any warranties or conditions
      of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A
      PARTICULAR PURPOSE. You are solely responsible for determining the
      appropriateness of using or redistributing the Work and assume any
      risks associated with Your exercise of permissions under this License.

   8. Limitation of Liability. In no event and under no legal theory,
      whether in tort (including negligence), contract, or otherwise,
      unless required by applicable law (such as deliberate and grossly
      negligent acts) or agreed to in writing, shall any Contributor be
      liable to You for damages, including any direct, indirect, special,
      incidental, or consequential damages of any character arising as a
      result of this License or out of the use or inability to use the
      Work (including but not limited to damages for loss of goodwill,
      work stoppage, computer failure or malfunction, or any and all
      other commercial damages or losses), even if such Contributor
      has been advised of the possibility of such damages.

   9. Accepting Warranty or Additional Liability. While redistributing
      the Work or Derivative Works thereof, You may choose to offer,
      and charge a fee for, acceptance of support, warranty, indemnity,
      or other liability obligations and/or rights consistent with this
      License. However, in accepting such obligations, You may act only
      on Your own behalf and on Your sole responsibility, not on behalf
      of any other Contributor, and only if You agree to indemnify,
      defend, and hold each Contributor harmless for any liability
      incurred by, or claims asserted against, such Contributor by reason
      of your accepting any such warranty or additional liability.

   END OF TERMS AND CONDITIONS

   APPENDIX: How to apply the Apache License to your work.

      To apply the Apache License to your work, attach the following
      boilerplate notice, with the fields enclosed by brackets "[]"
      replaced with your own identifying information. (Don't include
      the brackets!)  The text should be enclosed in the appropriate
      comment syntax for the file format. We also recommend that a
      file or class name and description of purpose be included on the
      same "printed page" as the copyright notice for easier
      identification within third-party archives.

   Copyright [yyyy] [name of copyright owner]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
```

### 7.2 MIT License: video-ad-editor (applies to scripts/beat.py, scripts/story.py)

```
MIT License

Copyright (c) 2026 Majed Alzaabi

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

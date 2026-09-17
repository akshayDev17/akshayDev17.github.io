# Source registry — the conclusion

One working source per section, per state/UT. Hand-maintained as states are reviewed.

This is the **conclusion** the Harvester fetches from. `SOURCES.md` is the **investigation
report** — every URL, evidence, and verification level. When in doubt, read that; but
this file is the single, lean answer, and it is what gets consumed.

## Bills

| State/UT | Working source | Kind | Status |
|---|---|---|---|
| Assam | https://assambidhansabha.org/home | official assembly | ✅ works |
| Andhra Pradesh | https://aplegislature.org/web/aplegislature | official assembly | ✅ works |
| Arunachal Pradesh | https://prsindia.org/bills/states?title=&state=Arunachal+Pradesh&year=All | PRS (unofficial) | ⚠️ official text = Gazette |
| Bihar | https://prsindia.org/bills/states?state=Bihar | PRS (unofficial) | ⚠️ convenience only — see tiers below |
| Maharashtra | https://mls.org.in/Vidheyake_Assembly-2026.aspx | official assembly | ✅ per-bill PDFs — English (clean text) + Marathi |
| Gujarat | https://gujarat.neva.gov.in/Bill/GetBillDashBoardData?UnitCode=GJ | official assembly (NeVA) | ⚠️ metadata table; Document links 404 — text via e-Gazette + PRS |
| Rajasthan | https://assembly.rajasthan.gov.in/Containers/Legislation/GovernmentBills.aspx | official assembly | ✅ metadata register (727 bills, Assemblies 10–16); text + introducer via PRS |
| Punjab | https://punjabassembly.gov.in/Legislations/IntroducedBills | official assembly | ✅ **best self-sufficient case** — index + bill text + introducer, all on the official host |
| Goa | https://www.goavidhansabha.gov.in/bills.php | official assembly | ✅ per-member, both types, introducer + "As Introduced"/"As Passed" PDFs; private-member bills stop at the 6th Assembly |
| Uttar Pradesh | https://upvidhansabhaproceedings.gov.in/en/web/guest/bills-search | official (Liferay 7) | ⚠️ search UI exists but is **portlet-stateful, not curl-queryable** (0 rows on replay); no per-member tally, no gov/private split — PRS (258 bills, 2019–) is the usable tier |
| Madhya Pradesh | https://mpvidhansabha.nic.in/bill.htm | official assembly | ✅ year-wise HTML tables (2014–2026); **introducer in the table** (भारसाधक = Minister name+portfolio); govt bills only; Bill/Act PDFs are **Hindi scans** |
| Tamil Nadu | https://prsindia.org/bills/states?state=Tamil+Nadu | PRS (unofficial) | ❌ no official bills module (`bills.php` 404); PRS = 576 bills 2010–2026 — **official gazette reproductions, English, introducer named** |
| _all other states/UTs_ | — | — | pending review |

**Uttar Pradesh — four separate properties; the bills tier is the weak one.**
The state runs **four** distinct hosts, and a fetcher needs different techniques for each:
1. `uplegisassembly.gov.in` — **bespoke** AngularJS over ASP.NET with an **ASMX JSON service** (the
   cheapest and best tier — see Profile).
2. `upvidhansabhaproceedings.gov.in` — **Liferay 7** portal (`com_semanticbits_upla_*` portlets,
   theme `upla-ind-theme`); server-renders *reads*, but **queries are portlet-stateful**.
3. `vsopp.up.gov.in/uplaquest/Question_Online/` — classic **ASP.NET WebForms** (see Questions).
4. `upvs.neva.gov.in` — the national NeVA tenant (a thin shell here; see below).

- **Bills — a search exists, but it is not curl-queryable.** `bills-search` (115,563 B), `ordinance-search`,
  `acts-search`, `gazette-search` (214,073 B), `gazette-by-decade` (219,127 B) and `assembly-debates` all
  return **200**, and the bills form is a plain POST carrying a `p_auth` token plus a `p_p_id` portlet
  namespace — but replaying it with a valid token and three different query strings returned
  **0 table rows and 0 PDF links every time**, and none of the search pages exposes document links in its
  HTML. **Confirms the recon: a browser/session is required for Liferay queries.**
- **No per-member bill tally and no government-vs-private-member split** on any page — recon confirmed.
- **Convenience tier: PRS holds 258 UP bills/ordinances, 2019–2026 — nothing earlier.**
  (`bills_states/uttar-pradesh/`, slug is `uttar-pradesh` not `Uttar+Pradesh`.) **Correction to what I
  first wrote here:** I initially recorded "50 PDFs" — that was PRS's **page size**, not the total.
  PRS paginates at `per-page=50` and **silently caps `per-page=1000` back to 50**, so only
  `page=1..6&per-page=50` reveals the real number: **258** (2019: 4 · 2020: 42 · 2021: 41 · 2022: 21 ·
  2023: 35 · 2024: 51 · 2025: 41 · 2026: 23). Still a fraction of what a 403-seat house passes, and
  **nothing before 2019**, but far from "nothing".
- **These PRS PDFs are gazette reproductions** — the *UP Government Gazette, विधायी परिशिष्ट
  (Legislative Supplement) भाग-3 खण्ड (क)*, i.e. the bill as published in the gazette, in **Hindi**.
  **Reading note:** they carry a text layer, but `pypdf`'s `extract_text()` garbles the Devanagari
  (CID fonts; the Unicode is embedded via `/ToUnicode` CMaps that pypdf does not honour) — the reliable
  route is **OCR**: render (`qlmanage -t -s 2600`) then `tesseract -l hin --tessdata-dir
  work/election-atlas/tools/tessdata`. Read: **Bill 57 of 2025 = *The Uttar Pradesh Private Universities
  (Second Amendment) Bill, 2025***, introduced in the 11 Aug 2025 sitting, published under Rule 126 of the
  2023 Rules of Procedure, further amending the UP Private Universities Act 2019. (Ord 4 of 2025 = the UP
  Repealing Ordinance 2025, promulgated under Art. 213(1).)
- **Step 10 is therefore satisfiable via PRS for recent bills**, even though the official Liferay source is
  not queryable. What I read: the two documents above, plus the answer-text of a question (Questions) and
  the 1937–1993 attendance register (Attendance).

**Goa — per-member bills with the introducer in the index, and a live e-Gazette.**
- **Index + per-member filter.** `bills.php` + the AJAX listing `_bills.php?assembly_id={a}&member_id={m}&session_id={s}&billtype_id={b}&display_id=`. Combos come from `_get_combo_details.php?mode=BILLS&a_id=14` → **40 members + "Raised By"**, 14 sessions, Bill Type = `1 Government Bill` / `2 Private Member Bill`. **No session cookie, no POST, no captcha** — plain GET fragments.
- **The index itself carries the introducer** — `Bill No 24 of 2022 (Government Bill) **Introduced by Shri. Subhash Shirodkar**`, plus title, Introduced on, Governor Assent Date, Portfolio, Department, and **two PDFs: "Bill As Introduced" (`_AI`) and "Bill As Passed" (`_AP`)**.
- **Introduced vs Passed — third independent confirmation.** Same bill, both variants: the **As Introduced** PDF closes `(SUBHASH SHIRODKAR) … Minister for Co-operation` + `(NAMRATA ULMAN) Secretary`; the **As Passed** PDF carries only `Dated Speaker` and `I assent to this Bill. Dated Governor`. Three states now agree: **the Minister is in the Introduced document, never the Passed one.**
- **Private-member bills: partial, and it is a *recency* gap.** Assemblies 7 (2017) and 8 (2022) return `"Information currently not available!!!"`, but assemblies **5 and 6 do have records** — e.g. *Bill No. 39 of 1988, The Goa Official Language (Amendment) Bill, introduced by Shri. Luizinho Faleiro* and *Bill No. 3 of 1980*. So it is **not "no private-member bills"**; it is *published up to the 6th Assembly, absent after*. (The recon recorded only the two empty assemblies.)
- **Encoding: born-digital text.** The As-Introduced PDF uses **object streams** (`/ObjStm` present), so a raw-byte `/BaseFont` scan reports **"scan"** and is wrong — text extracts cleanly. My own classifier was caught by this; see the failure mode.
- PRS holds **431** Goa bill PDFs, **2006–2026** (unofficial convenience tier). ⚠️ An earlier run of this
  registry recorded "50" — that is PRS's **page size**, not the total; see the PRS pagination note under UP.

**Bihar — three tiers, all real, ordered by authority:**
1. **Index (official)** — Vidhan Sabha bill lists (`bill.html`): `Official bill.pdf` (1980→), `Act List from 1937.pdf` (1937→), `Ordinance.pdf` (1990→), plus non-official lists — title + department + introduced/passed/assent. Legacy-font (Walkman-Chanakya) text layer.
2. **Documents (official)** — `egazette.bihar.gov.in` (`SearchGazette.aspx`, `Notification.aspx`); searchable by year/type. ASP.NET WebForms.
3. **Convenience (unofficial)** — PRS: per-bill titles → Gazette PDFs. Mirror with OCR text: Internet Archive `in.gov.bih.gazette.*` (28,977 items).

**Maharashtra — best bills case, but NeVA is newer than the recon says.**
- Bills are **per-bill PDFs**, each in **English (clean Unicode text)** + Marathi, hosted on the official `mls.org.in` itself — PRS is *not* needed for bills. The list page is a link directory (no table, no titles); the metadata lives in the PDFs.
- **Introducer = parse the PDF's last page.** The cover sheet names `Shri X, Minister for Y` (e.g. "Shri Chandrakant (Dada) Patil, Minister for Higher and Technical Education"). The list page does not carry it.
- **Session mapping is absent.** The PDF has a date ("As passed … on the 9th March, 2026"); the URL carries year + status (introduced/passed). No session name is published — derive it from the date, never invent one.
- Correction to `SOURCES.md`: it recorded NeVA as "not implemented"; **`mhla.neva.gov.in` now exists** (member template only — `/Bill` and `/Questions` still redirect to the national landing).
- No official e-Gazette host (both candidates DNS-fail) and no Internet Archive `in.gov.maharashtra.gazette.*` collection. PRS holds 48 bills as fallback.

**Gujarat — rich NeVA register, but bill *text* links are dead.**
- The register (`Bill/GetBillDashBoardData?UnitCode=GJ`) is a clean HTML table: Sr No, Bill Number, Title, Description, Ministry, Department(s), Date of Introduction, Document. Government bills only (14).
- **Correction:** the "Document" column links to `cms.neva.gov.in/…/IntroductionPdf/…` which now **404** — the bill-text PDFs are gone. Text via the official e-Gazette (`egazette.gujarat.gov.in`, Directorate of Government Printing & Stationery, 200) and PRS (**count unverified — see the PRS pagination note under UP; "50" was the page size**).
- **Session-seeding trap still applies:** NeVA serves an empty shell unless the session is seeded on `gujarat.neva.gov.in` first. The recon's "Himachal Pradesh leak" title is now generic, but seeding is still required.
- **Introducer IS published — in the bill text's last page, not the register.** The register's Ministry/Department(s) columns name the *department*, never the person. The person is on the last page of the bill text (Gujarat Gazette, Extraordinary Part V, mirrored by PRS). Read 10 bills across 2025 + 2026:
  - **2026 bills (Gazette Part V)** — born-digital English. Last page recommendation block: *"Dated the [date]. **[MINISTER]**. By order and in the name of the Governor of Gujarat…"* Observed: Kunvarjibhai Bavaliya (Bill 1), Harsh Sanghavi (Bill 2), Praful Pansheriya (Bill 8), **Dr. Pradyuman Vaja (Bill 9)**, Jitubhai Vaghani (Bill 10), Sanjaysinh Mahida (Bill 18).
  - **2025 bills ("As Introduced")** — English body + a Gujarati last-page note: *"[શ્રી <name>, <portfolio> મંત્રીશ્રી] (…ગુજરાત સરકારી રાજપત્રમાં પ્રસિદ્ધ કર્યા મુજબ)"*. The **name garbles under plain extraction** — it is set in a legacy Gujarati font (Krishna/Arishnaweb) while the portfolio + boilerplate are clean Unicode (Shruti), so it needs a Gujarati transcoder, not OCR. Recovered: **Rushikesh Patel, આરોગ્ય મંત્રી (Health)** — Bills 2/18/19; **Balvantsinh Rajput, શ્રમ/કૌશલ્ય વિકાસ/રોજગાર મંત્રી (Labour)** — Bill 20.
- **Correction to my own earlier note:** I had recorded "introducer NOT named" after reading *one* bill (Bill 9) and stopping at the first page's *"consent of the Speaker under rule 127A"* line — that line is about pre-introduction publication, not the introducer; the Minister is named on pages 2–3 (Statement-of-Objects signature + recommendation block). One bill was not enough; the 10-bill sample across 2025/2026 settles it.

**Rajasthan — best official bills *register* of any state so far, but no text on the official host.**
- **Official register (metadata only).** `GovernmentBills.aspx` is a static HTML page holding **7 tables, one per Vidhan Sabha, Assemblies 10–16**, all live-scraped: 16th **42**, 15th **135**, 14th **152**, 13th **161**, 12th **103**, 11th **106**, 10th **28** = **727 bills** (page stamped "Printed on: 9/16/2026"). Columns: `S.No. | Bill No./Year | Short Title (Hindi + English) | Introduced On | Discussed On | Passed On | Ordinance No./Year | Act No./Year | Remarks`. **No introducer column, no bill-text link** — the page carries zero bill PDFs.
- **Private members' bills: empty.** `PrivateBillsIntroduced.aspx` and `PrivateBillPassed.aspx` each render **0 data rows** (layout row only). Confirms the recon.
- **Text + introducer come from PRS** (`/files/bills_acts/bills_states/rajasthan/…`, **45 PDFs**). Every bill PDF is **bilingual**: a Hindi body, then an **"(Authorised English Translation)"** section. The introducer sits in the English part as a closing block — `MAHAVEER PRASAD SHARMA, Principal Secretary. **(Name, Minister-Incharge)**` — and is repeated above each Statement of Objects / Financial Memorandum as `[Name], Minister Incharge`. Sampled **5 bills, 5 recoverable, all in clean Latin script**: Tika Ram Jully (Bill 4), Rajendra Singh Yadav (Bill 6), **Ashok Gehlot** (Bills 8 and 34), Ramlal Jat (Bill 31).
- **Reading them needs no transcoder and no OCR — read the English translation.** Nothing here is a scan. The Hindi runs do mix Unicode **Mangal** with legacy **DevLys-010** (`/ToUnicode` absent), so Hindi matras garble (`प्रभार� मंत्री`; Bill 34 carries 4,034 U+FFFD) — but the **"(Authorised English Translation)" section is 100% clean ASCII** and carries the introducer in Latin script, so the DevLys path is avoidable entirely. **Retracting my own earlier claim on this line:** I first recorded that these bills "need a DevLys transcoder" and that Bill 8's name was "lost to encoding" — I had read only the Hindi pages. Bill 8's name is `(Ashok Gehlot, Minister-Incharge)`. `SOURCES.md`'s "No OCR is required anywhere in Rajasthan" is **correct**.
- **Read (step 10) — what a bill actually contains.** Bill 4 of 2023 = *The Baba Amte Divyang University, Jaipur Bill*: **91 pp**, Hindi body (pp. 1–48) + **"(Authorised English Translation)"** (pp. 49–91). It establishes and incorporates a university for the disabled at Jaipur and provides for connected matters; numbered sections open `1. Short title, extent and commencement` → `2. Definitions` → the university's objects, powers, officers and Statutes/Ordinances. Then Statement of Objects and Reasons, Financial Memorandum (≈₹5 crore/yr recurring), and the delegation-of-powers note. Language: **Hindi + official English**; the English is readable end to end with no OCR.
- **No e-Gazette, no archive.** Both `egazette.rajasthan.gov.in` and `gazette.rajasthan.gov.in` fail DNS; Internet Archive `in.gov.rajasthan.gazette*` returns **0 items**. PRS is the only bill-text tier.

**Punjab — first state whose *official host alone* is sufficient for bills (index + text + introducer).**
- **Index.** `Legislations/IntroducedBills` (200, 425 KB, **372 data rows / 389 PDF links**) and `Legislations/PassedBills` (200, 411 KB, **349 PDFs**). Columns are `Sr. No | Title | English | Punjabi` — **no introducer, no date, no session column**. Coverage **2009–2026**, Assemblies 13–16.
- **Government bills only.** `Legislations/PrivateBills`, `/PrivateMembersBills`, `/PrivateMemberBills`, `/Bills` all return **302** (no route), and both bill pages contain **zero** occurrences of "private member" / "non-official".
- **CORRECTION — the documents are NOT "scanned images".** The recon generalised that from a **2009** bill. Classified **33 bills** (19 passed + 14 introduced) across 2009–2026: **2019→2026 are born-digital text PDFs** (2026/2025/2024 carry `/ToUnicode` and extract cleanly; 2023–2019 have a text layer without `/ToUnicode`, extracting with minor artefacts); **2014 and 2009 are pure scans** (zero `/BaseFont`, one image XObject, 6.6–10 MB). So the reading mode is **year-dependent**, not scan-everything.
- **CORRECTION — the introducer IS published, but only in the *Introduced* document.** This is the load-bearing nuance: **Introduced bills name the Minister + portfolio** in the closing block; **Passed bills name only the Vidhan Sabha *Secretary***. Measured exactly: **11 readable Introduced bills → 10 named the Minister** (the 11th is an unlabelled multi-document file with no Statement-of-Objects block); **16 readable Passed bills → 0 named a Minister** (only signatures: R. L. Khatana / Ram Lok Khatana / Surinder Pal / Shashi Lakhanpal Mishra — the two regex "hits" are the false positives "approval of the Council of Ministers" and "Advisors to Chief Minister"). **Fetch the Introduced PDF for the introducer, never the Passed one** — reading Passed alone is how "not published" gets recorded wrongly.
  - Recovered: **Tarunpreet Singh Sond** (Rural Development & Panchayats, 2026) · **Lal Chand Kataruchak** (Forests & Wildlife Preservation, 2026) · **Hardip Singh Mundian** (Revenue, Rehabilitation & Disaster Management, 2025 ×2) · **Bhagwant Mann** (Chief Minister, 2024 and 2022) · **Bram Shanker Sharma (Jimpa)** (Revenue, 2023) · **Harpal Singh Cheema** (Excise & Taxation, 2022) · **Amarinder Singh** (Chief Minister, 2020 ×2).
- **No e-Gazette, no archive — and none needed.** `egazette.punjab.gov.in`, `gazette.punjab.gov.in`, `punjabgazette.gov.in` **all DNS-fail**; Internet Archive `in.gov.punjab.gazette*` = **0 items**. PRS holds **137** Punjab bill PDFs, **2015–2026** (an earlier run recorded "50" — the page size), as an unofficial convenience tier; but the official host already carries the text, so **PRS is the fallback here, not the source** — the reverse of Rajasthan.
- **Read (step 10) — what a bill actually contains.** *The Punjab Protection of Trees Bill, 2026* (Bill No. 19-PLA-2026, introduced 10 Aug 2026): **12 pp, born-digital English**. It regulates the felling and replanting of trees and provides an institutional mechanism to compensate the environmental loss from felling; `1.` short title/extent (all urban areas in Schedule III, or as notified)/commencement, `2.` exemptions per Schedules I & II, then the compensation machinery, ending with a Memorandum on Delegated Legislation (**s.16** empowers the State Government to make rules). Signed `CHANDIGARH: THE 10TH AUGUST, 2026 — R. L. KHATANA, SECRETARY`. Also read: *The Societies Registration (Punjab Amendment) Bill, 2026* (7-PLA-2026, passed) — inserts new ss.1/1-A/1-B separating educational and healthcare societies from the rest (Registrar's categorisation final) and adds ss.21–22 (remove difficulties; rules laid before the House for 30 days). Language: **English + Punjabi**; the **English is clean text**, the Punjabi bill PDFs are **legacy-font and garble** — read English.

**Madhya Pradesh — the introducer is in the HTML table itself, and the bills are Hindi scans.**
- Year-wise tables `bill_2014.htm` … `bill_2026.htm` (home `bill.htm`, 24,665 B). Columns: bill number · bill
  name · **भारसाधक सदस्य (Minister-in-charge) — name + portfolio** · department · introduced on · discussed /
  passed on · Governor's assent date · Act number/year. Verified 2025: `श्री जगदीश देवड़ा, उप मुख्यमंत्री
  (वित्त)`, `श्री कैलाश विजयवर्गीय, नगरीय विकास एवं आवास मंत्री`, `श्री विश्वास कैलाश सारंग, सहकारिता मंत्री`.
  **Every introducer is a Minister → government bills only**, no private-members list, no defeat/withdrawal
  register, no per-member index (the recon's point holds).
- Per-row PDFs: a `Bill No N.pdf` and an `ACT No N of YYYY.pdf`. **The bill PDFs are SCANS** — read *Bill No 1
  of 2025* = **मध्यप्रदेश विनियोग विधेयक, 2025 (the MP Appropriation Bill, 2025)**: 3 pages, 0 `/BaseFont`,
  3 image XObjects, no text layer → **OCR required** (Tesseract `-l hin`, vendored model, reads it cleanly).
- **Three-tier:** PRS holds **475** MP bills/ordinances, **2010–2026** (the full pagination walk, page-size
  trap applied — an earlier naive read would have said "50"). e-Gazette hosts (`egazette/gazette/mpgazette`
  `.mp.gov.in`) all **NXDOMAIN**; Internet Archive `in.gov.mp.gazette*` = **0 items**. So PRS is the only
  text/bill tier beyond the official scanned PDFs.

**Tamil Nadu — bills are NOT published on the assembly site, but PRS's copies are the official gazette.**
- `bills.php` and `17thassembly/bills.php` both return **HTTP 404** (16-byte body) — there is no bill list, no
  bill text, no introducer, no private/govt classification on `assembly.tn.gov.in`. The Documents menu
  publishes only handbooks / rules / salary Acts / facility forms — no bill register.
- **Working source = PRS:** `https://prsindia.org/bills/states?state=Tamil+Nadu` → **576** TN bills/ordinances,
  **2010–2026** (full pagination walk; page-size trap applied). e-Gazette hosts (`egazette`/`gazette`/`tngazette`
  `.tn.gov.in`) all **NXDOMAIN**; Internet Archive `in.gov.tn.gazette*` = **0 items**.
- **Read (step 10) — these PRS PDFs ARE the official gazette, and they carry the introducer.**
  Downloaded two across years:
  - `Bill1of2025TN.pdf` (177 KB, 2 pp, born-digital text) = **Tamil Nadu Government Gazette Extraordinary,
    Part IV—Section 1 "Tamil Nadu Bills"**, "L.A. Bill No. 1 of 2025 — *A Bill to repeal the Tamil Nadu Borstal
    Schools Act, 1925*", introduced 8 Jan 2025 under Rule 130. Statement of Objects closes
    **`S. REGUPATHY, Minister for Law`** (with `K. SRINIVASAN, Principal Secretary`).
  - `Bill1of2010TN.pdf` (7.8 KB, 2 pp) = L.A. Bill 1 of 2010, *further to amend the TN Payment of Salaries Act 1951*.
  **So: English, clean text, no OCR; the introducer (Minister) is named in the Statement-of-Objects signature.**
  PRS is hosting copies of the *official* gazette, so it is the gazette tier in disguise, not a lossy re-type.
- The assembly's productive document channel is the **Debates** (`debates/debates_menu.php`, per-sitting
  volumes 2011–2026), not a bill register.

## Profile — roster + photo

| State/UT | Working source | Kind | Status |
|---|---|---|---|
| Maharashtra | https://mls.org.in/PDF2025/15-Assembly-24-11-2024.pdf | official (ECI gazette) | ✅ text PDF, 288 seats, English names clean; ⚠️ no photos |
| Gujarat | https://gujarat.neva.gov.in/ContactDirectory/FetchMembersList?MLT=16&MSLT=15&Assemblyid=15 | official (NeVA) | ✅ 182 MLAs, all with photos; needs session-seeding |
| Rajasthan | https://assembly.rajasthan.gov.in/Containers/Members/ConstituencyWise.aspx | official assembly | ✅ 200 MLAs + per-member photos (static HTML, no session) |
| Punjab | https://punjabassembly.gov.in/Members | official assembly (NeVA) | ✅ 117 MLAs, all with photos; static HTML, no session needed |
| Goa | https://www.goavidhansabha.gov.in/mlas.php | official assembly | ✅ 40 MLAs, all with photos; Who's Who PDF per member |
| Uttar Pradesh | https://uplegisassembly.gov.in/angular.asmx/show_MemberList | official assembly | ✅ **ASMX JSON** — 397 (18th) / 390 (17th) / 404 (16th) MLAs, Hindi+English names, party, constituency; photos on the Liferay portal |
| Andhra Pradesh | https://aplegislature.org/web/legislative-assembly/legislative-assembly/legislative-assembly/member-s-information | official (Liferay DXP) | ✅ 175 MLAs, 175 photos, name/constituency/district/party; 384-pp Who's Who PDF; drill-down 403 (session token) |
| Arunachal Pradesh | https://arla.neva.gov.in/ContactDirectory/FetchMembersList?MLT=4&MSLT=0&Assemblyid=0 | official (NeVA) | ✅ 59 members + 59 photos (⚠️ 59 vs 60 seats — duplicate/stale entries); per-member detail page |
| Assam | https://assambidhansabha.org/members | official assembly | ✅ 126 MLAs over 7 pages, 126 photos (ext varies per member); per-member `?id=` detail |
| Madhya Pradesh | https://mpvidhansabha.nic.in/16mlaprofile.htm | official assembly | ✅ 230 MLAs via **bulk PDFs** (roster + 1,433-photo biography PDF); ⚠️ no per-member page/search/JSON |
| Tamil Nadu | https://assembly.tn.gov.in/17thassembly/members.php | official assembly | ✅ 234 MLAs in one HTML table, party+constituency in the name cell, predictable `members/NNN.jpg` photos; ⚠️ no per-member detail page |
| _all_ | — | — | pending review |

**Andhra Pradesh — 175 MLAs, one of the cleanest photo sources, and a 384-page Who's Who.**
- Roster `…/member-s-information` (**441,628 bytes**, byte-exact) is **Liferay `div`/`span` markup, not a
  `<table>`** — parse structure, not a grid. **175 distinct `mem_id`s**, constituency numbers 1–175 with
  **zero gaps**, and party text (TDP 135 · YSRCP 11 · BJP 8 sampled).
- **Photos: 175/175** at `admin.aplegislature.org//preview.do?filePath=basePath&fileName=photos/16/{mem_id}.jpg`
  (term id 16). Sample = 200, `image/jpeg`, **24,576 bytes**, 480×720.
- **Who's Who** 16th Assembly: `legislation.aplegislature.org/…/Sixteenth…MLA-WhoisWho.pdf` — **66,723,748
  bytes (byte-exact), 384 pages, born-digital text**, 175 profiles with name/DOB/father/mother/education/
  spouse/children/positions-held/addresses/mobile/email.
- Term-wise lists (1st–16th + Hyderabad LA, 17 PDFs) at `…/termWiseMembersList`.
- ⚠️ **Per-member drill-down is a Liferay portlet action** with a session-bound `p_auth` token → **curl 403**.
  The roster and photos are fetchable; the drill-down needs a browser session.

**Arunachal Pradesh — 59-member NeVA roster against 60 seats (a known caveat).**
- `arla.neva.gov.in` (68,348 bytes, byte-exact) is the shared national NeVA template.
- Roster = AJAX fragment `ContactDirectory/FetchMembersList?MLT=4&MSLT=0&Assemblyid=0` (**395,641 bytes**,
  byte-exact) → **59 members** with name/party/constituency/DOB/mobile/email/photo.
- **⚠️ 59 entries against 60 seats** — the recon's caveat holds: duplicate members against Mechuka, Itanagar
  and Khonsa-East, plus stale 7th-Assembly entries. Do not treat 59 as "60 complete".
- Photos: `cms.neva.gov.in/NeVA/AR/FileStructures//Member/thumb/…` (59 photos; sample 200, `image/jpeg`,
  **21,311 bytes**, 550×706).
- Per-member `Member/Details/{id}` (e.g. id 9 = Pema Khandu, "Mukto -[3]-") → name, party, constituency
  number+name, addresses, contacts.

**Assam — 126 MLAs, paginated 20/page over 7 pages, per-member photos with a filename trap.**
- `assambidhansabha.org/members` (**52,267 bytes**, byte-exact) is server-rendered; `totalPageCount: 7`,
  `?page=1..7` → **126 distinct `members?id=` values** and **126 distinct photo paths** (ids 148–298).
- **Photo filename trap:** `assets/uploads/mla/profilepic/member_<id>.<ext>` — the extension **varies per
  member** (`member_149.jpg` = 200; `member_148.jpeg`, `member_151.png`; `member_26.jpg` = 404). Read the
  URL from the roster HTML, never construct it from the id alone.
- Per-member `members?id=<n>` (e.g. id 148 → "23 - CHENGA") — name, constituency, party, father/mother,
  DOB, addresses, contacts, education, marital status, spouse, children, and term ("elected to the 16th
  Assembly").
- NeVA `asla.neva.gov.in` also lists the 126-member directory, but its member pages carry **no photo** —
  use the bespoke site for photos.

**Madhya Pradesh — 230 MLAs, but only as bulk PDFs (no per-member page, no search, no JSON).**
- `16mlaprofile.htm` (42,411 B) links a set of whole-Assembly **PDFs**: `sadasyasuchi16vs.pdf` (member list +
  photos), `AllMember16vs.pdf`, **`mlaprofilevsxvi030826.pdf`** (जीवन वृत्त biographies — the richest source,
  **1,433 photos**), `member_all.pdf` (text-only roster, no photos), plus party-wise (`BJP16vs` / `INC16vs` /
  `BAP16vs`) and category (`SC16vs` / `ST16vs` / `Women16vs` / `firsttimer16vs`) rosters.
- ⚠️ **No per-MLA page, no search box, no member-detail route, no JSON/XHR API.** Every profile artifact is a
  bulk PDF (or JPG) that must be downloaded and parsed. The biography PDF has **partial `/ToUnicode`** — the
  Devanagari extracts partially and may need OCR for clean names.
- NeVA `mpla.neva.gov.in` is **onboarded but unpopulated**: `/Member/Details/218` (200, 22,426 B) shows
  "No Records Founds" for Assurances / Debates / BILLS, and `Member_ProfileDetail` returns a blank `Name:`.

**Tamil Nadu — one clean HTML table of all 234 MLAs, but no per-member page.**
- `17thassembly/members.php` (**141,080 bytes**, byte-exact) is a single plain `<table>` — **234 data rows**,
  columns `Serial | NAME (party abbrev + constituency in parens) | ADDRESS | TEL | Email | PHOTO`. Party and
  constituency live in one text cell (`1 Aadhav Arjuna Hon. Thiru. (TVK) (Minister) (Villivakkam)`).
  Live party split: **TVK 106, DMK 59, AIADMK 41, INC 5, PMK 4, VCK 2, BJP 1, DMDK 1**.
- **Photos:** fully predictable `17thassembly/members/NNN.jpg` — sample `014.jpg` = 200, `image/jpeg`,
  **1,834 bytes, 91×130** (byte-exact). 224 `<img>` entries this pass (recon counted 228 — a couple of
  members lack a photo).
- **No per-member detail page** — no `member.php?id=` links anywhere in the markup (confirmed). The roster is
  one alphabetical list, hand-maintained PHP with no "last updated" stamp; use the CEO's
  `elections.tn.gov.in` / ECI `S22` results as the temporal cross-check (the recon's caution).
- A PDF edition exists (`17thassembly_members.pdf`, 83,614 B, 8 pp, clean English text). Party position at
  `partyposition.php`.

**Uttar Pradesh — the best JSON roster so far, plus photos from a second host.**
- **ASMX JSON is the backbone** — `POST https://uplegisassembly.gov.in/angular.asmx/<method>` with
  `Content-Type: application/json`. No cookies, no tokens, no auth. The **payload for each method is
  documented in the site's own controller** at `https://uplegisassembly.gov.in/Members/Members.js`
  (68,990 B) — read it rather than guessing; two methods returned **HTTP 500** until I used the right shape.

| Method | Payload | Returns |
|---|---|---|
| `show_MemberList` | `{"Id":"MLA_HI","parm":"18"}` | **397** (18th) · **390** (17th) · **404** (16th) members |
| `show_assembly_master` | `{"Id":"show_assembly_master"}` | **18 assemblies** — Hindi + English name, constitution/start/end/dissolution dates, year, **total seats + reserved SC/ST seats** (1st Assembly 1952: 430 seats, 83 SC) |
| `CurrentAssemblyPartyList` | `{"Id":"CurrentAssemblyPartyList","parm":"18"}` | **live party strength** — BJP 256, SP 101, AD(S) 13, RLD 9, SBSP 6, NISHAD 5, Independent 3, JDL 2 |
| `AllAssemblyMembersList` | `{"locale":"AAML"}` | the 18-assembly index |

- Member fields: `mla_name` (Hindi) + **`mla_name_eng`**, `party_name_hindi` + **`party_name_english`**,
  `ac_name` + **`ac_name_eng`**, `mla_code`, `assembly_name`. So names, parties and constituencies arrive in
  **both scripts** — no transliteration needed. **No photo field**, as the recon says.
- **Photos come from the Liferay portal**: `member-s-information` returns **3,512,767 bytes** (byte-exact
  with the recon) with **418 member links** and **836 table rows**; per-member pages are
  `member?memberId=<id>` (91,303 B, also byte-exact). Portraits are plain JPEGs. Note ⚠️ 418 links for a
  403-seat house — the page includes non-sitting/other entries, so **do not treat 418 as the roster size**;
  the ASMX roster (397) is the authoritative count.
- URLs are **relative** in the site's markup (`Members/main_members_hi.aspx`) — my first crawl prefixed only
  leading-`/` paths and fetched **5 of 139** pages. Resolve relative paths against the base.

**Goa — small, fully static roster; bespoke site, not NeVA-derived.**
- `mlas.php` (200, **55,466 bytes** — byte-identical to the recon) is plain HTML, **no JS, no session**:
  **40 roster tiles** (`div.mla-info-box`), **40 distinct `mem_id`s**, and **40 photos** (37 under
  `uploads/members/<slug>_<id><ts>.JPG`, 3 under `static.goavidhansabha.gov.in/goalpub/docs/members/`).
  Headed *"MEMBERs OF Eighth Legislative Assembly 2022"* — **the term is published on the page**.
- Per-member: `member_detail.php?mem_id=94` (200, **58,741 bytes** — byte-identical). Publishes constituency
  number + name (`22 - Shiroda`), personal/contact details, and a genuine **per-term Election Details table**
  (assembly, constituency, party, votes polled/received/margin across the 8th, 7th, 4th, 3rd assemblies).
  A **"VIEW PROFILE"** button links a Who's Who PDF with a **real text layer** (not a scan).
- **Transport quirk worth recording:** the host resolves (`goavidhansabha.gov.in` → 103.119.239.16, same IP
  as the non-`.gov.in` mirror `goavidhansabha.in`) and `host`/`dig` answer, but `curl` intermittently failed
  with *"Could not resolve host"*. Retry, or pin with
  `curl --resolve www.goavidhansabha.gov.in:443:103.119.239.16`. Do not record the site as down on one
  resolver hiccup — it returned 200/41,305 bytes on the pinned retry.

**Punjab — complete roster with photos, no session seeding required.**
- `Members` is **server-rendered static HTML paginated 5 ways** via `?Page_No=1..5` (24+24+24+24+21).
  Union across the five pages = **117 member links / 117 distinct photo paths** — so every sitting
  member has a photo, not a subset. Photo pattern: `/NevaMemberPic/16/<file>.jpg`.
- Per-member profile `Members/MembersProfile?MemberID={id}&AssemblyID=16` (200, 110 KB server-rendered):
  name, party, constituency + number (`Dhuri -[107]- Sangrur`), permanent/local address, mobile, email,
  photo, and a Personal Details block (father's name, DOB, caste category, marital status, spouse,
  children, education, sports, interests, foreign travel, Positions Held).
- Unlike Gujarat, **no session seeding is needed** — a bare `curl` with a UA returns the roster and the
  profiles directly. The NeVA template's redirect trap does not fire on these routes.

## Questions

| State/UT | Working source | Kind | Status |
|---|---|---|---|
| Bihar — starred | https://vidhansabha.bihar.gov.in/starred_question.html | official assembly | ⚠️ scanned Hindi PDFs (444); current (18th Assembly) |
| Bihar — unstarred | https://vidhansabha.bihar.gov.in/Unstared%20Question.html | official assembly | ⚠️ scanned Hindi PDFs (42); stale (stops at 16th Assembly) |
| Maharashtra — starred | https://mls.org.in/Starred_list_Assembly.aspx | official assembly | per-sitting PDFs; Marathi legacy font |
| Maharashtra — unstarred | https://mls.org.in/atarankit-yadi-assembly.aspx | official assembly | per-list PDFs; member names present; Marathi legacy font |
| Gujarat — starred | https://gujarat.neva.gov.in/Member/Member_Question?MemberId={id}&AssemblyID=15 | official (NeVA) | ✅ per-member HTML table (Gujarati) |
| Gujarat — unstarred | same NeVA per-member question endpoint | official (NeVA) | ⚠️ **unverified** — no member with unstarred questions sampled yet |
| Rajasthan — starred | https://rlaoasys.rajasthan.gov.in/QuestionsWeb/MemberWise.aspx | official assembly | ✅ per-member, **verified**: 22/39/37 rows across 3 members (see note) |
| Rajasthan — unstarred | same endpoint — type column `प्रश्न का प्रकार` distinguishes them | official assembly | ✅ per-member, **verified**: 57/60/12 rows across the same 3 members |
| Punjab — starred | https://punjabassembly.gov.in/Questions/StarredQuestion | official assembly | ✅ session PDFs, **current** (13th Session, 10.08.2026); per-MLA via the PDF |
| Punjab — unstarred | https://punjabassembly.gov.in/Questions/UnStarredQuestion | official assembly | ✅ session PDFs, **current**; **not stale** — same sessions as starred |
| Goa — starred | https://www.goavidhansabha.gov.in/questions_list.php | official assembly | ✅ per-sitting **Question Booklet Report**, per-member table; **born-digital text** |
| Goa — unstarred | same page — separate PDF per sitting | official assembly | ✅ same report + per-member table, but **JBIG2 scan** — needs OCR |
| Uttar Pradesh — starred | https://vsopp.up.gov.in/uplaquest/Question_Online/MemberWise.aspx | official assembly | ✅ per-member, **curl-replayable**, **with answer text** — type column distinguishes the two |
| Uttar Pradesh — unstarred | same endpoint — `प्रश्न का प्रकार` column | official assembly | ✅ per-member, same call; sampled 38 starred / 32 unstarred for one MLA |
| Andhra Pradesh — starred | — | — | ❌ **none** — `legislation.aplegislature.org` questions module is behind login + CAPTCHA (5/5 `.do` endpoints = identical 12,014-byte login page) |
| Andhra Pradesh — unstarred | — | — | ❌ **none** — same wall |
| Arunachal Pradesh — starred | https://arla.neva.gov.in/Member/Member_Question?MemberId={id}&AssemblyID=7 | official (NeVA) | ✅ per-member, 2 Starred verified for member 53; ⚠️ **stale** (all data 27/08/2020) |
| Arunachal Pradesh — unstarred | same endpoint — `Question Type` column | official (NeVA) | ✅ per-member, 5 Unstarred verified for member 53; ⚠️ **stale** |
| Assam — starred | http://aladigitallibrary.in/handle/123456789/4109 (DSpace) | official (DSpace 6.3) | ✅ per-sitting-day PDFs (Budget Session 2026); **Assamese scan** — needs `ben` OCR; not per-member |
| Assam — unstarred | http://aladigitallibrary.in/handle/123456789/4110 | official (DSpace 6.3) | ✅ separate collection, same shape |
| Madhya Pradesh — starred | https://mpvidhansabha.nic.in/house%20proceedings/hp.htm (star*.pdf index + ques*.pdf Part 1) | official assembly | ✅ per-sitting PDFs, member name + Q no. in text; born-digital (partial Devanagari garbling) |
| Madhya Pradesh — unstarred | same `ques*.pdf` — Part 2 (Rule 46(2)) | official assembly | ✅ per-sitting; the `ques` book is **combined** starred+unstarred, not unstarred-only |
| Tamil Nadu — starred | https://tnla.neva.gov.in/ (Notice Board → cms.neva.gov.in `17_1_S_*.pdf`) | official (NeVA) | ⚠️ per-day PDFs only; member + Q no. in text; **Tamil legacy-encoded (lossy)** — not per-member indexed |
| Tamil Nadu — unstarred | — | — | ❌ **none** — not separately indexed anywhere (recon + live) |
| _all others_ | — | — | pending review |

**Andhra Pradesh — questions are NOT public (login + CAPTCHA).** `legislation.aplegislature.org` returns a
**12,014-byte login page** (title-less, "Member Services"/"Questions" module names visible in the nav). All
five probed endpoints — `/Questions.do`, `/QuestionList.do`, `/MemberList.do`, `/login.do`, `/Home.do` —
returned the **identical 12,014 bytes** (5/5 md5-equal), so there is no public question list. The data exists
behind a `username/password/Captcha` gate. Recorded as **absent publicly**, not missing.

**Arunachal Pradesh — per-member, both types, but STALE (2020).** `Member/Member_Question?MemberId={id}&AssemblyID={7|8}`
returns an HTML table `Sr No | Question Number | Question Type | Date | Minister | Subject | Document`.
Verified member 53 → **7 rows: 2 Starred + 5 Unstarred**, all dated **27/08/2020**, with 5 PDF links on
`cms.neva.gov.in/NeVA/AR/FileStructures///PaperLaid/…` (subjects: "33 KV LT LINE FROM DEOMALI",
"DE-ADDICTION CENTER", "TOTAL GOVERNMENT EMPLOYEES…"). Member 9 (CM) → "No Records Founds" (ministers don't
ask questions). ⚠️ **`AssemblyID=8` returns the exact same 2020 rows as `AssemblyID=7`** (both 7,300 bytes),
so the current 8th Assembly (2024–) has **no question records** — the latest published is the 7th Assembly's
Fifth Session, Aug 2020. Both types share one table; the type is a column, not a separate list.

**Assam — per-sitting-day PDFs, starred and unstarred as separate collections, Assamese scans.**
- NeVA `asla.neva.gov.in/Questions` now **redirects to the NeVA home dashboard** (title "National e-Vidhan
  Application - Digital Legislators", 192 KB, zero "Starred"/"Unstarred") — the redirect trap; the list is
  JS-fetched and not curl-queryable.
- The usable source is the **ALA Digital Library (DSpace 6.3)**, community *"06. Questions & Answers"*
  (`aladigitallibrary.in/handle/123456789/3219`) → `2025` / `2026` → sessions → **four separate collections**:
  `01. Starred Question` (4109) · `02. Unstarred Question` (4110) · `03. Starred Questions with Replies`
  (4390) · `04. Unstarred Questions With Replies` (4151). Items are one PDF per sitting day, titled
  *"Starred Question Budget Session 2026 06th July 2026 Monday Q 1 to 20"*, `Q 21 to 40`, `Q 41 to 60`…
  → **indexed by date + Q-range, not by member**.
- **Read (step 10):** downloaded `…/bitstream/123456789/4113/1/Starred Question…06th July 2026…pdf`
  (200, **2,768,330 bytes, 8 pages**) — **0 `/BaseFont`, 8 image XObjects → a pure scan, no text layer**.
  OCR of page 1 with `eng` is garbage because the text is **Assamese (Bengali script)** — needs a
  **Bengali/Assamese model (`tesseract -l ben`)**, which is not vendored here (only `eng` + `hin`).

**Madhya Pradesh — per-sitting PDFs; the `star`/`ques` split is INDEX vs full-book, not starred vs unstarred.**
- Hub `house%20proceedings/hp.htm` (31,399 B) publishes, per sitting day, `starDDMMYY.pdf`,
  `quesDDMMYY.pdf`, `spDDMMYY.pdf` (corrigenda) and `hpDDMMYY.pdf` (proceedings).
- **CORRECTION to `SOURCES.md`:** it maps `star` → starred and `ques` → unstarred. That is imprecise.
  `star220726.pdf` is the **"तारांकित प्रश्नोत्तर की अनुक्रमणिका"** — a 1-page *INDEX* (S.No | Member Name |
  Question Number | Department), not the questions. `ques220726.pdf` is the **combined "प्रश्नोत्तर-सूची"**,
  **293 pages, 818 KB text** — **भाग-1 = तारांकित (starred) Q&A** (full question + ministerial answer) then
  **भाग-2 = अतारांकित (unstarred)** — specifically *starred Q&A converted to unstarred under Rule 46(2)*.
  So **both types are in the one `ques` book**; the `star` file is only the starred index.
- **Both per-member attributable** — each question carries the member name and Q number
  (`( सि. 1122 ) श्री सुनील उईके`, `( सि. 4 ) श्री प्रहलाद लोधी`), plus the replying minister
  (`स्कूल शिक्षा मंत्री (श्री उदय प्रताप सिंह)`). No per-member aggregate — you must download every day's
  PDF and attribute manually (recon's point).
- **Encoding:** born-digital text (`/ToUnicode` present), but **Devanagari conjuncts garble under pypdf**
  (`श्री`→`ी`, `शिक्षा`→`िशा`, `तारांकित`→`ताराांककत`) — a partial-CMap issue, not a scan. Read with a
  Devanagari-aware extractor or OCR; do not call it "clean text" on pypdf's output alone.

**Tamil Nadu — starred questions are per-day PDFs only; unstarred are not published at all.**
- The assembly's own `questions.php` and `17thassembly/questions.php` both **404** — there is no question
  page, no per-member question list, and no starred/unstarred index on `assembly.tn.gov.in`.
- **Starred** reach the public only as **per-day PDFs on the NeVA notice board**:
  `https://cms.neva.gov.in/NeVA/TN/FileStructures//Notices/17_1_S_03-09-2026.pdf` ("Starred Questions,
  Thursday, 03 September 2026"; also `31-08-2026`, `01-09-2026`). **Read (step 10):** that PDF is 200,
  **251,224 bytes, 2 pages** (byte-exact) — header *"தமிழ்நாடு சட்டமன்ற பேரவை … உறியிட வினாக்கள் …
  மொத்த வினாக்கள் 5"* (Total questions 5), each question identified by **member + Q number**
  (`*21 தி. மா. NM.`, `*22 …`). So **per-member attribution is possible from the PDF**, but there is no
  per-member *index*.
- **⚠️ The Tamil is legacy-encoded and lossy.** Extraction yields `தமி நா ச டம ற ேபரைவ` for `தமிழ்நாடு
  சட்டமன்ற பேரவை` and `வியாாழக்கிழமை` for `வியாழக்கிழமை` — vowel signs and conjuncts are silently dropped
  (TSCII/TAB-era pre-Unicode Tamil). English extracts clean; Tamil does not round-trip. Any derived
  per-member count would rest on unreliable Tamil extraction.
- **Unstarred questions are NOT separately indexed** — the recon's finding holds; the notice board carries
  only "Starred" PDFs.

**Uttar Pradesh — CORRECTION: the WebForms portal IS curl-replayable, and it is the richest questions
source found in any state so far, because it returns the ANSWERS too.**
- `SOURCES.md` concludes that a **headless browser is required** for `vsopp.up.gov.in/uplaquest/Question_Online/*`
  and that "the questions data itself cannot be reached without replaying that state". **The second half is
  the key: replaying the state is exactly what works via plain curl.** No browser was needed.
- **The replay recipe.** GET `MemberWise.aspx`, then POST `application/x-www-form-urlencoded` back with
  `__VIEWSTATE` (**34,524** chars — byte-exact with the recon), `__EVENTVALIDATION` (**9,212** — byte-exact),
  `__VIEWSTATEGENERATOR`, **`__ncforminfo`** (the WAF field — echo it back), plus
  `DdlHouse` / `DdlSession` / `DdlMemberName` / `BtnSubmit=Submit Query`. Status **200**, real data.
- **Two failure modes I hit, both of which look like a broken portal:**
  1. Posting an **invalid member id** returned **HTTP 200 with a 0-byte body** — which reads as "blocked".
     The id must come from the page's *own* `DdlMemberName` select. My first attempt scraped the *session*
     select by accident and posted a session id as a member id.
  2. **Rapid POSTs get the server to start timing out** (the `__ncforminfo` WAF). After 4 quick POSTs the
     host stopped answering entirely for ~20 s, then recovered. **Space requests ~5 s apart.**
- **What a result actually contains** — columns
  `क्र.सं. | प्रश्न का प्रकार | सूचीबद्ध तिथि | विभाग का नाम | (आइटम नं.) - प्रश्न | उत्तर`
  i.e. S.No · **question type** · listed date · department · question text · **answer text**.
  For member **18346 (श्री अखिलेश, Karhal–346)**, 18th Assembly session 7 (प्रथम सत्र, 2024): **72 table
  rows** — **38 starred (`तारांकित`) and 32 unstarred (`अतारांकित`) mentions**. A row reads
  `अतारांकित | 06/02/2024 | पंचायती राज | प्रश्न (63) … | उत्तर …` closing with the replying minister —
  e.g. **`योगी आदित्यनाथ मुख्यमंत्री, पंचायती राज विभाग`**. Bihar and Rajasthan publish question *lists*;
  **UP publishes the reply.**
- **One endpoint serves BOTH types** — the type is a column (`प्रश्न का प्रकार`), the same shape as Rajasthan.
  Sessions available: **7** (1 = प्रथम सत्र 2022 … 7 = प्रथम सत्र 2024).
- ⚠️ **Coverage is sparse and member-specific.** Sampling 9 members on session 7: **2 had records**
  (18346 → 38/32; 18050 डॉ अजय कुमार → 16/10) and the other 7 returned
  `Information that you might want or need is not be available !!!`. Member 12722 returned that message for
  **all 7 sessions**. I did **not** establish whether "not available" means *the member asked no questions
  that session* or *that member's record was never uploaded* — treat the per-member coverage as unverified.
- Other axes exist (`SessionWise`, `QuestionWise`, `DateWise`, `DepartmentWise`, `AdvanceSearch` —
  133,105 B, the best bulk target). The portal root `/` returns **403**; the `.aspx` pages do not.

**Goa — both types present, per-member attributable, but the two differ in encoding.**
- `questions_list.php` shell + `_questions_list.php?assembly_id=14&session_id=&sitting_id=&display_id=`,
  and combos from `_get_combo_details.php?mode=QUESTIONS_LIST&a_id=14`. Returns **one card per sitting**
  carrying **separate "Starred List" and "UnStarred List" PDFs** — 5 sittings × 2 = **10 PDFs**, so
  **neither type is stale or missing** (both live at the current 14th Session, 2 Sep 2026).
- **Both are the same document type — a "Question Booklet Report"** with a Portfolios Index *and* a
  **per-Member table**: columns `Member Name | Member LAQ No. | Portfolio`, e.g. under starred
  `Shri. Premendra Shet → 001B Social Welfare, 001C Empowerment of persons with disabilities, 001A Power`.
  So questions **are per-MLA attributable** — parse the PDF.
- **The asymmetry that matters: starred is text, unstarred is a scan.**

| Variant (sitting 166, 02.09.2026) | Size | Pages | Questions | Encoding |
|---|---|---|---|---|
| Starred | 227 KB | 35 | **50** | **born-digital text** — 4 `/BaseFont`, 68,924 chars |
| Unstarred | **68 MB** | **110** | **185** | **pure JBIG2 scan** — 0 `/BaseFont`, 0 `/FontFile`, 119 images, no `/ToUnicode` |

- **Reading note:** the unstarred list needs OCR. `pypdf` cannot even extract the images —
  **JBIG2 needs `jbig2dec`, which is not installed here** (`DependencyError`). Working route found:
  render with macOS `qlmanage -t -s 3000` (or `sips`), then **Tesseract 5.5 with `-l eng`** (Goa's
  legislation is English, so no Indic model is needed). Verified: page 1 → *"Question Booklet Report,
  Report Generated On: 28-Aug-2026 12:33 PM … List of UnStarred Questions For Answer on 02 September
  2026, Total Number of Questions: 185"*; page 3 → the per-member table (`Shri. Aleixo Lourenco`,
  `Shri. Antonio Vas`, `Shri. Altone D'Costa`, `Shri. Carlos Ferreira`, `Shri. Chandrakant Shetye`).
  The report also carries deletion notes (`NOTE:-Unstarred LAQ191 is deleted.`).

Bihar also publishes **House questions** (`house_question.html`), **Short Notice**
(`short_notice_ques.html`) and **Answer to questions not put in House**
(`notputinhouse.html`) — same scanned-PDF shape.

**Reading them needs Hindi OCR — use Gemini 2.5 Flash.** Measured on 300 real printed
Devanagari scans, it is the strongest reader (chrF++ **86.3**, median CER 0.0), ahead of
Claude Opus 4.7 (82.2) and the best open option Qwen3-VL-8B (75.2). Do **not** use
specialised OCR-VLMs: DeepSeek-OCR collapses on real scans (89% catastrophic rate).
Every extracted name is validated against the official 243-name roster before storing.
Evidence: *Can OCR-VLMs Read Devanagari?* [arXiv 2606.29213](https://arxiv.org/abs/2606.29213).

**Rajasthan — one endpoint serves BOTH types; the boundary is the session, not the topic.**
- `MemberWise.aspx` is an ASP.NET WebForms POST (`BtnSubmit`): harvest `__VIEWSTATE` /
  `__VIEWSTATEGENERATOR` / `__EVENTVALIDATION`, set `DdlHouse` + `DdlSession` + `DdlMemberName`.
  The **type is a column** (`प्रश्न का प्रकार`), not a separate list — values seen:
  `तारांकित` (starred), `अतारांकित` (unstarred), `अन्तः सत्र` (intra-session).
- Verified live, 16th Assembly **session 2**: member 2023001 **79 rows (57 unstarred / 22 starred)**,
  2023002 **100 (60 / 39 / 1 intra-session)**, 2023003 **49 (12 / 37)**; session 1 gives 4 rows.
- **Coverage stops at session 2.** Session 3+ is delegated to NeVA — the page says so itself
  ("16वीं विधान सभा के तृतीय सत्र एवं आगे के सत्रों के प्रश्नों हेतु यहां Click करें") — and the
  legacy portal returns **0 rows** for session 3. On the NeVA side the route redirects to the
  national landing and `Questions/FetchDataList` returns **HTTP 500**, so **current-session questions are a gap**.
- Transport quirk: Python's default trust store rejects the `rlaoasys` cert chain
  (`self signed certificate in certificate chain`); macOS `curl` succeeds.

**Punjab — both types live and in step; per-MLA from the PDF, not the endpoint.**
- Two endpoints, one per type: `Questions/StarredQuestionSession` and
  `Questions/UnStarredQuestionSession`, both GET JSON taking `?AssemblyCode=16&SessionCode={s}`.
  Payload: `RecordId, Heading, **FilePath** (English), **FilePathLocal** (Punjabi), SessionDate, SessionId`.
- **CORRECTION — the recon says questions are "not attributable per MLA". They are.** The per-member
  *endpoint* is indeed dead (`Members/GetQuestions?MemberCode={id}` → `[]` for all 10 members tested),
  but **each question in the PDF carries the member's name and constituency** with a question number and
  the minister answerable — e.g. `*1877 Smt. Neena Mittal (Rajpura):` and `706 Sardar Manjinder Singh
  Lalpura (Khadoor Sahib):` — under a `Total Questions - 16` / `Total Questions - 5` count. **Per-MLA
  attribution = parse the session PDF**, exactly as with the bills. Do not record "not attributable"
  from the empty endpoint alone.
- **Neither type is stale — a clean ✅✅** (rare: Bihar's unstarred stops at the 16th Assembly). Both
  cover the **same 8 of 14** sessions (185, 184, 177, 176, 175, 174, 173, 171 populated; 183, 181, 179,
  178, 172, 170 empty — the one-day/special sessions). Newest = 13th Session, **10.08.2026**.
- **Two session-ID namespaces — do not cross-post.** Questions numbers sessions **170–185**; the
  Members API numbers the *same* sessions **170–397** (Questions `185` = Members `397` = "Thirteenth
  Session"). A session id valid on one route is silently wrong on the other.
- English PDFs are **born-digital clean text** (`/ToUnicode` present). Punjabi PDFs extract as Gurmukhi
  Unicode but with **matra-reordering artefacts** (`ਿਨਸ਼ਾਨ ਵਾਲੇ` for `ਤਾਰਾਂਕਿਤ ਵਾਲੇ`) — **read English**.

## Development fund

Per-MLA fund data exists in only **4** jurisdictions — Mizoram, Odisha, Rajasthan,
Puducherry. See `SOURCES.md` §2.

| State/UT | Working source | Kind | Status |
|---|---|---|---|
| Rajasthan | https://ework.rajasthan.gov.in/iwmsweb/Pdmn/Dashboard_graph_amchart_new.aspx | official (RDIWMS) | ✅ per-MLA JSON over POST, 200 records, live |
| Punjab | — | — | **none** — no portal, and no per-MLA fund (per-segment scheme only) |
| Goa | — | — | **none** — MLA-LAD runs per-constituency; no portal, only a sparse `MLA/ALD` gazette trace |
| Uttar Pradesh | — | — | **none** — 11 candidate hosts DNS-fail; zero `विधायक निधि`/`Vidhayak` on any assembly property |
| Madhya Pradesh | — | — | **none** — Vidhayak Nidhi exists (name attested) but no portal; 4 candidate hosts NXDOMAIN; only NEGD documents an *internal* MLALAD app (no URL) |
| Tamil Nadu | https://www.tnrd.tn.gov.in/schemes/st_mlacds.html | official (RDPR dept) | ⚠️ **MLACDS** scheme (not MLALAD) — rules + per-constituency entitlement (Rs.2–3 cr/yr) published, but **no per-MLA data portal** |
| Mizoram / Odisha / Puducherry | — | — | pending review |

**Madhya Pradesh — none publicly; the fund exists but the only "system" is internal.**
- Fund name: **विधायक स्थानीय क्षेत्र विकास निधि (Vidhayak Nidhi / MLALAD)** — attested. But `mlalad.mp.gov.in`,
  `mlaladapp.mp.gov.in`, `vidhayaknidhi.mp.gov.in`, `vidhayak.mp.gov.in` all **NXDOMAIN**.
- The only official trace is the NEGD India-Stack-Local entry *"MLALAD Application — MADHYA PRADESH"*
  (`negd.gov.in/isl/Directory/statedata/244`): describes an MPSEDC-built workflow app, but its **"Website
  Link" field is empty** — documented as on-premise/internal, no public URL.
- `vsgrant*.htm` (स्वेच्छानुदान) is the Speaker/Dy.Speaker/LoP **discretionary grant**, not the MLA fund —
  three columns, no amounts, no MLA names. Record as absent, not missing.

**Tamil Nadu — MLACDS: the scheme is fully documented, but there is no per-MLA data portal.**
- The fund's official name is the **Member of Legislative Assembly Constituency Development Scheme (MLACDS)**
  — **not** Vidhayak Nidhi and **not** MLALAD (that name belongs to other states). Scheme page
  `tnrd.tn.gov.in/schemes/st_mlacds.html` (200, 24,963 B); rules in **G.O.(Ms.) No.145, RDPR (SGS.1), dated
  10.12.2021** (`tnrd.tn.gov.in/project/go_files/3_99999_2021_145.pdf`, ~25 MB, OCR'd/searchable — range-check
  206 confirmed live).
- **Entitlement is uniform and published** (Rs.2–3 crore per constituency per annum, Tied + Untied split), but
  **no per-MLA or per-constituency works/sanction/expenditure data exists** — the G.O. documents allocation
  history and aggregate sanctions, nothing per member. `mlacds.tn.gov.in` and `tnmlacds.tn.gov.in` both
  **NXDOMAIN**. Record as aggregate-only, not missing-entirely: the scheme and its entitlement are official,
  the per-MLA ledger is not.

**Uttar Pradesh — none, and the name-check is clean.**
- **11** candidate hosts probed and **all DNS-fail**: `vidhayaknidhi.up.nic.in`, `mlalad.up.nic.in`,
  `nidhi.up.nic.in`, `vidhayaknidhi.gov.in`, `mlaup.gov.in`, `mlafund.up.gov.in`, `vidhayak.up.gov.in`,
  `eoffice.up.gov.in`, `nagarvikas.up.nic.in`, `upvidhansabha.gov.in`, `vidhansabha.up.nic.in`.
- **Zero** occurrences of `विधायक निधि` or `Vidhayak` on the assembly home (Hindi and English) or the
  Liferay member-information page. The `up.nic.in` family is otherwise live, so this is a genuine absence
  rather than a network artefact.
- **Three-tier check:** PRS = **258** bill/ordinance PDFs, 2019–2026 (see Bills); `egazette.up.gov.in` **resolves to 164.100.186.223
  but the connection times out on both http and https** — a DNS entry with no service, so it is
  *tested-and-absent*, not a gazette; `gazette.up.gov.in` and `upgazette.gov.in` DNS-fail; Internet Archive
  `in.gov.up.gazette*` = **0 items**. **UP has no reachable e-Gazette.**

**NeVA (UP tenant) — redirect trap, thin shell.** `/Bill`, `/Questions` and `/Debates` all bounce to
`/Home/NeVA`; only `/Member/Details/<id>` renders (200, 22,426 B) and it carries **0** attendance hits.

**Goa — no portal, but the e-Gazette carries a live per-MLA `MLA/ALD` trace.**
- **Scheme confirmed from a primary document, still reproducible.** The recon's eProcure tender link still
  returns 200 (70,606 bytes) and its Work Item reads *"**under MLA-LAD Scheme in Cortalim Constituency**"*
  — so the local name **"MLA-LAD Scheme"** is attested officially, not just in the press.
- All candidate hosts **DNS-fail**: `mlaladgoa`, `mlalad.goa`, `mla.goa`, `vidhayaknidhi.goa`,
  `goa.mlalad` `.gov.in`. `goa.gov.in` search returns **no scheme entry**.
- **NEW — the gazette is a per-MLA paper trail.** Goa gazettes cite MLAs' recommendations by a stable
  reference: `Note No. **MLA/ALD**/2025-26/363 dated 16-02-2026 from Hon'ble MLA, **Adv. Carlos Alvares
  Ferreira, Aldona Constituency**, GLA.` (`ALD` = Area Local Development). These appear inside
  District-Magistrate notifications that the MLA's note originated.
- **But it is far too sparse to be a dataset: exactly 1 `MLA/ALD` reference across all 145 gazettes of
  FY 2026-27.** So: the trail is official and per-MLA, but there is **still no allocation, sanction,
  expenditure or works ledger** — per-MLA fund figures remain unpublished.

**Rajasthan — strongest fund case so far (RDIWMS, Rural Development & Panchayati Raj Dept).**
- **Per-MLA JSON over POST**: `POST …/Dashboard_graph_amchart_new.aspx/get_mla_data` with
  `{"a_no":16,"fin_yr":0,"dist_code":0}` and `Content-Type: application/json;charset=utf-8`
  → **200 records / 95,966 B** in one call. Keys: `s_no, HMLAName, const_name, no_proposed,
  recommended_amt, no_fs, no_cc, fs_amt, avail_amt, remain_amt, district_name`; names arrive
  HTML-entity-encoded — run `html.unescape`.
- **Live drift proves it updates**: totals moved since the recon — approved works 58,791 → **58,965**,
  financially sanctioned 35,027 → **35,109**, completed 9,959 → **9,963**.
- ⚠️ **Key and semantics disagree**: `remain_amt` renders under the column headed `व्यय राशि`
  (expenditure). Treat it as the expenditure slot **as displayed**; do not silently rename it.
- ⚠️ **No published per-MLA entitlement/ceiling.** The allocated amount exists only as one unnamed
  component of `उपलब्ध राशि` (initial + other receipts + allocated) — the available total is
  official, the annual limit behind it is not.

**Punjab — none, and the negative is now driven rather than assumed.**
- All five candidate hosts **DNS-fail**: `mlafund`, `mlalad`, `vidhayak`, `mla`, `lgd` `.punjab.gov.in`.
- **Zero** occurrences of `vidhayak` / `nidhi` / `mlalad` on both `punjabassembly.gov.in` (572 KB) and
  `punjab.gov.in` (308 KB).
- **`rangla.punjab.gov.in` is a trap** — it resolves (200, 59 KB) but its title is *"Rangla Punjab |
  Society"*: a WordPress **donation** portal for flood relief (`donat`×16, `flood`×31, `relief`×9,
  `80(G)`×1, and **zero** `MLA`/`Vidhayak`/`Nidhi`). It is the **Chief Minister's Rangla Punjab Fund**,
  unrelated to the per-segment *Rangla Punjab Vikas Scheme*, and publishes no utilisation data.
- The per-segment Vikas Scheme is **news-only** — no government order, guideline PDF or portal found;
  it is an allocation per **assembly segment**, not a per-MLA discretionary fund. No MPLADS analogue.
- **Web-search last resort (searched after the live probes came up empty) — the scheme is real and
  better-documented than "news-only", but still has no per-MLA ledger.** *Rangla Punjab Vikas Yojana*
  had its **guidelines approved by Cabinet** (April 2025): **₹585 crore for FY 2025-26**, **₹5 crore per
  MLA/assembly segment annually** across 117 segments, with a first instalment of **₹213 crore**
  reported released ([Indian Express](https://indianexpress.com/article/cities/chandigarh/punjab-cabinet-meet-117-assembly-receive-rs-5-crore-development-fund-9964631/),
  [Parliamentary Affairs](https://parliamentaryaffairs.in/punjab-mlas-to-get-rs-5-cr-annually-to-boost-local-development/),
  [Babushahi](https://babushahi.com/view-news.php?id=214101)). So the fund is **announced, funded and
  guideline-backed** — **but no per-MLA/segment ledger, utilisation dashboard or portal is published**,
  and no MLALAD exists ([Indian Express, Sep 2024](https://indianexpress.com/article/cities/chandigarh/bereft-of-mlalad-funds-punjab-legislators-feel-helpless-we-are-for-attending-bhogs-weddings-only-9588664/lite/):
  MLAs "feel helpless"; the CM called MLALAD a non-starter). **Official-tier check:** the 701-page
  `Demand for Grants Vol-III FY 2026-27` (`finance.punjab.gov.in`) contains **0** occurrences of
  `MLA` / `Vidhayak` / `MLALAD` / `Legislator`; the only `Rangla` hits are the **`Rangla Punjab
  Society`** grant-in-aid (₹30–50 lakh) — a different entity (the donation body). So the scheme's money
  flows through **district demands**, not a per-MLA budget head, confirming the per-segment framing.
- ⚠️ **Web-search trap — do not import Pakistan's Punjab.** Queries like *"Punjab MLA attendance"*
  return the **Provincial Assembly of the *Punjab* (Pakistan)**, which *does* publish attendance online
  ([PILDAT](https://pildat.org/parliamentary-monitoring1/pildat-welcomes-provincial-assembly-of-the-punjabs-move-to-make-members-attendance-record-public),
  [The News](https://www.thenews.com.pk/print/18142-upload-mpas-attendance-on-web-punjab-pa-directed)).
  That is a **different legislature**, with MPAs not MLAs. Likewise the 2019 TOI case *"HC declines plea
  seeking disclosure of MLAs' attendance on portal"* is about the **Haryana** assembly, not Punjab —
  verified by reading the article body. Neither is evidence about Indian Punjab.

**Punjab — the *parliamentary* tier is a different answer: both figures ARE published.** For Punjab's
**MPs** (Lok Sabha), unlike its MLAs, fund and attendance are both retrievable per member — already
implemented in this repo:
- **Fund** — `tools/fetch-mplads.py IN-PB 1` (eSAKSHI / `mplads.mospi.gov.in/digigov/`, house 2 = Lok
  Sabha). Live-run: **13 constituencies**; Bathinda (Harsimrat Kaur Badal) **391 works**, Gurdaspur
  (Sukhjinder Singh Randhawa) **337 works** — per-MP, per-work, with amounts.
- **Attendance** — `tools/fetch-sansad-record.py 4433 18 IN-PB bhatinda` (`sansad.in/api_ls/member/getMemberAttendanceByMpsno`).
  Live-run: **107/156 across 8 sessions**. Same call also returns questions (88 for that MP) and bills.
- So if the MLA figure is unavailable, the **MP analogue is not** — worth stating explicitly rather than
  letting "Punjab publishes no attendance" stand unqualified.

**Goa e-Gazette — MAJOR CORRECTION TO `SOURCES.md`: it is LIVE, browseable, and born-digital.**
`SOURCES.md` records `goaprintingpress.gov.in` as **HTTP 503** ("server unavailable") and concludes the
scheme notification "could not be retrieved from the official gazette". **That is no longer true.**
- **Host is up**: `https://goaprintingpress.gov.in/` → **200, 277,232 bytes**, titled *"DEPARTMENT OF
  PRINTING & STATIONERY – GOVERNMENT PRINTING PRESS"*.
- **It is a browsable Apache directory**, not a search API: `/downloads/` lists **73 year folders**
  (FY-coded `0001`…`2627`, plus historical `3637`…`9900`) — effectively **1936-37 → 2026-27**.
  Folder sizes: `2627` (2026-27) **145** PDFs, `2526` **443**, `2425` **368**.
- **Gazettes are born-digital text** — e.g. `downloads/2627/2627-19-SII-EOG-2.pdf` (200, 384 KB):
  `/BaseFont` ×31, `/ToUnicode` ×14, 3,804 chars, opening *"EXTRAORDINARY No. 2 — GOVERNMENT OF GOA,
  Department of Finance, Revenue and Control Division, Notification"* (an excise/liquor closure order for
  a Village Panchayat bye-election). **No OCR required** — a genuine upgrade to Goa's bill/index tier.
- ⚠️ **The site advertises a search that is not deployed.** `/recent-e-gazettes/`, `/about-e-gazettes/`,
  `/search-e-gazettes-by-date/`, `/search-e-gazettes-by-no/`, `/dops/search-e-gazettes-by-ocr/`,
  `/bulletin/`, `/about-us` **all return 404** despite appearing in the nav. Several individual download
  links 404 too (`2627-21-SI-OG.pdf`, `2627-20-SI-EOG-1.pdf`), so the file list has gaps. **Treat this as
  a directory crawl, not a queryable gazette.**
- Naming: `SI/SII/SIII` = series, `OG` = Ordinary Gazette, `EOG` = Extraordinary, `SUG` = Supplement.
- **Round trip:** the recon's own conclusion (*no gazette*) would have been overturned by a single retry —
  worth re-testing any host recorded as 5xx before it hardens into a gap. Internet Archive has **0 items**
  for `in.gov.ga.gazette*` and `in.gov.goa.gazette*`, so this host is the **only** gazette tier.

## Attendance

**Goa — none, and this is the most thoroughly driven negative so far.**
- **The answer is not "the page is a stub" — the word does not exist on the site.** Fetched **all 44
  distinct `.php` pages** linked from the homepage and grepped each: **0 pages contain "attendance"**
  (the string is likewise absent from `mlas.php`, `member_detail.php?mem_id=94` and the homepage).
- **The paperless SPA has no attendance route either.** Fetched all **36 JS bundles** behind
  `eassemblygoa.gov.in` (`app.*.js`, `vendor.*.js` and 33 chunks, incl. the 1.4 MB main chunk):
  **0 bundles contain "attendance"**, and its route table (**39 routes** — `/bill`, `/laq`, `/lob`,
  `/motion`, `/SearchArchives_*`, `/verbatim`, …) has **no attendance route**. Note
  `goavidhansabha.gov.in/questions.php` serves this same 3,745-byte SPA shell, not HTML.
- **NeVA does not fill the gap.** `goa.neva.gov.in/Member/Details/94` renders an **empty shell** —
  `Assurances No Records Founds`, `Debates No Records Founds`, `BILLS No Records Founds`, and **no
  attendance tab at all** (0 hits). `/Bill` and `/Questions` hit the **redirect trap** → `/Home/NeVA`.
  The page title carries the shared-template artifact *"Member Details | NeVA | **eVidhan- Himachal
  Pradesh**"*, confirming it is the unmodified national template.
- Goa therefore joins the majority; nothing was missed, it was never published.

**Madhya Pradesh — none.** 0 hits for `attendance`/`उपस्थिति` across the home, profile
index, bills and proceedings pages; NeVA `Member_ProfileDetail` has no attendance field and returns blank.
Matches the recon's "hard, absolute gap" — no attendance page, table, PDF or portal anywhere.

**Tamil Nadu — none.** A **46-page sweep** of the assembly site found **zero** `attendance`
hits; `attendance.php` returns **404**. No per-member, per-sitting or aggregate attendance anywhere —
matches the recon's "hard gap".

**Uttar Pradesh — MAJOR CORRECTION. `SOURCES.md` says "Attendance: NOT PUBLISHED. No attendance data was
found on any official property." That is wrong — and it was found only by sweeping the site, not by
looking at member pages.**
- **The document exists and is official.** `uplegisassembly.gov.in/Library/pdf/Archives/upvs_upveshan_mla_upasthiti_1937_1993.pdf`
  (200, **8,876,170 B**) — *"उत्तर प्रदेश विधान सभा के उपवेशन और उनमें माननीय सदस्यों की उपस्थिति
  [1937–1993]"* — **"Sittings of the UP Legislative Assembly and the Attendance of Hon'ble Members,
  1937–1993"**. It is linked from the Assembly **Library** pages (`Library/HindiPages/Pustakalay_hi.aspx`,
  `Library/EnglishPages/Library_en.aspx`), which is why a member-page/tab sweep misses it.
- **Format: 132 pages, pure scan** (0 `/BaseFont`, 0 `/ObjStm`, 132 image XObjects, 0 `/ToUnicode`).
  **How to read it:** `qlmanage -t -s 3000` to render a page, then Tesseract **`-l hin`** against the repo's
  vendored model — `tesseract <png> - -l hin --tessdata-dir work/election-atlas/tools/tessdata`. Homebrew's
  Tesseract ships only `eng/osd/snum`, so the vendored `hin.traineddata` is what makes this readable.
- **What it contains:** the bulk is a **date-wise sitting register** —
  `दिनांक | वर्ष | दिन | खण्ड संख्या | उपस्थिति संख्या` — for every sitting 1937→1993 (e.g. Sept 1958: 346,
  361, 300, 351…; Apr 1988: 374, 408, 364…). It closes with a substantive narrative on **members whose
  membership was terminated for long absence**, naming individuals (श्री अख्तर आंदिल, श्रीमती महारानी
  जगदम्बा देवी) and discussing leave applications and missing medical certificates.
- ⚠️ **Honest limit — it is not a per-member table.** Verified across pages 20 / 52 / 110: what the book
  tabulates is **house-level attendance COUNTS per sitting date**, not rows of members. The per-member names
  live one tier down, and the book's own preface says so: from **1957–1984 the names of all *present*
  members were published day-by-day in the proceedings**, and from **1985 onward only *absent* members were
  named** (the rest deemed present) — so per-member attendance for that span is derived from the
  **कार्यवाही (proceedings)**, which the Assembly also publishes. **I did not verify the proceedings side.**
- **Current House (18th Assembly, 2022–): still nothing.** A sweep of **134 pages** on the assembly site
  produced exactly **4** matches for `attendance`/`उपस्थिति` — all four on the Library pages, all four this
  same archival book. NeVA `/Attendance`, `/attendance`, `/MemberAttendance` and `/Member/Attendance` are
  all **404**.
- **Lesson worth generalising:** the recon searched for attendance *pages and tabs*. The data was a
  **library publication**. A negative for "attendance" must sweep **every page**, including Library/archives,
  before it is recorded.

Rajasthan is the **first** jurisdiction found with per-MLA attendance. Everywhere else: none.

| State/UT | Working source | Kind | Status |
|---|---|---|---|
| Rajasthan | https://assembly.rajasthan.gov.in/MemberAttendance/MemberWiseAttendance.aspx | official assembly | ✅ **per-member signed / not-signed days, all 200 MLAs, per session** |
| Punjab | — | — | **none** — endpoint live but empty (112 calls, 0 rows) |
| Goa | — | — | **none** — 0 hits across 44 site pages and 36 SPA bundles |
| Uttar Pradesh | https://uplegisassembly.gov.in/Library/pdf/Archives/upvs_upveshan_mla_upasthiti_1937_1993.pdf | official assembly | ⚠️ **historical only (1937–1993)** — date-wise attendance counts; per-member names live in the proceedings. **Current House: none** |
| Madhya Pradesh | — | — | **none** — 0 hits across home/profile/bills/proceedings; NeVA `Member_ProfileDetail` blank |
| Tamil Nadu | — | — | **none** — 46-page sweep 0 hits; `attendance.php` 404; no per-member or per-sitting record |
| _all others_ | — | — | none found |

**Rajasthan — MAJOR CORRECTION. `SOURCES.md` records attendance as "ADVERTISED BUT NOT
RETRIEVABLE" with "no attendance figure … obtainable". That is wrong — the data is public.**
- **The postback works.** Two steps: (1) POST the house dropdown → a session list
  (`सत्र संख्या | बैठक की अवधि`, e.g. session 5 = 28/01/2026 to 10/03/2026); (2) POST that session's
  `__doPostBack` LinkButton → the per-member grid:
  `क्र.सं. | विभाजन संख्या | सदस्य का नाम | सदस्य द्वारा हस्ताक्षरित दिवस | सदस्य द्वारा अनहस्ताक्षरित दिवस`.
- Verified across **three sessions → 200 / 200 / 195 member rows**, with real variance
  (days signed 0–3, days not signed 0–2) — not a stub, not all-zero.
- **Why the recon got it wrong (and I nearly repeated it):** the house dropdown's option
  **display text is `16` but its `value` is `4`**. POSTing the *displayed* number returns
  `302 → /404?aspxerrorpath=…`; POSTing `4` returns the data. The same display/value split exists
  on the sibling report (`DatewiseAttendanceStatus.aspx`).

**Punjab — none, and this time the negative was *driven*, not inherited.**
- The endpoint is real and correctly shaped —
  `Members/GetAllMemberAttendanceDates_Neva_Latest?AssemblyID=16&SessionID={s}&MemberID={m}`, returning
  the `{sessionDates, Attendancestatus}` JSON the page's own JS expects — it is simply **unpopulated**.
- Swept **14 sessions × 8 members = 112 calls → 0 non-empty**. The rendered profile tab agrees
  ("No Record Found"), and the **sitemap shows no attendance route at all** — the tab is its only entry
  point, so there is nothing else to drill into.
- **Two traps recorded so this is not re-probed as broken.** (1) The page hardcodes
  `var defaultSessionID = '42'` — a NeVA template leftover, and **42 is not one of the 14 real session
  IDs** (397, 389, 388, 386, 379, 200, 194, 193, 188, 187, 173, 172, 171, 170); calling 42 returns `[]`
  and means nothing. (2) The Members and Questions routes use **different session-ID namespaces**
  (Members `397` ↔ Questions `185` for the same session) — posting one into the other is silently wrong.
- **Web-search last resort: no alternative source, and one that will mislead.** No news article, RTI
  report or third-party tracker publishing Punjab *MLA* attendance was found — the only systematic
  figures are for **Punjab MPs** (`sansad.in`, 107/156 for Bathinda). Two near-misses to reject
  explicitly: the *"HC declines plea seeking disclosure of MLAs' attendance on portal"* case is
  **Haryana**, and *"Punjab PA makes attendance record available online"* is **Pakistan's** Provincial
  Assembly. The MLA-level gap is therefore a **real documented gap**, not a search failure.

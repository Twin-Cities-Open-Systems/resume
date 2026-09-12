# YaW! Ham Radio Cheat Sheet: Technician, General and Extra

**Status:** held, not published. A study sheet for the soup-to-nuts license series. Every row below comes from a source listed at the bottom, fetched 2026-09-11; anything that could not be sourced is marked `TODO(verify)`.

> WHISKEY ZERO YANKEE ALFA WHISKEY. In Morse: `·––  –––––  –·––  ·–  ·––`. You are Wrong, at 20 words per minute.

## 1. Phonetic alphabet (ICAO)

Official spellings are **Alfa** and **Juliett**. Pronunciations as printed in FAA JO 7110.65, TBL 2-4-1 (the source bolds the stressed syllable; bold is not reproduced here). The FCC encourages a phonetic alphabet when identifying on phone (47 CFR 97.119(b)(2)).

| Letter | Word | Say | Letter | Word | Say |
|---|---|---|---|---|---|
| A | Alfa | AL FAH | N | November | NO VEM BER |
| B | Bravo | BRAH VOH | O | Oscar | OSS CAH |
| C | Charlie | CHAR LEE | P | Papa | PAH PAH |
| D | Delta | DELL TAH | Q | Quebec | KEH BECK |
| E | Echo | ECK OH | R | Romeo | ROW ME OH |
| F | Foxtrot | FOKS TROT | S | Sierra | SEE AIR AH |
| G | Golf | GOLF | T | Tango | TANG GO |
| H | Hotel | HOH TELL | U | Uniform | YOU NEE FORM |
| I | India | IN DEE AH | V | Victor | VIK TAH |
| J | Juliett | JEW LEE ETT | W | Whiskey | WISS KEY |
| K | Kilo | KEY LOH | X | X-ray | ECK SRAY |
| L | Lima | LEE MAH | Y | Yankee | YAN GKEY |
| M | Mike | MIKE | Z | Zulu | ZOO LOO |

| Digit | Word | Say |
|---|---|---|
| 0 | Zero | ZE-RO |
| 1 | One | WUN |
| 2 | Two | TOO |
| 3 | Three | TREE |
| 4 | Four | FOW-ER |
| 5 | Five | FIFE |
| 6 | Six | SIX |
| 7 | Seven | SEV-EN |
| 8 | Eight | AIT |
| 9 | Nine | NIN-ER |

ARRL's own sheets print "Alpha" and "Juliet"; the ICAO table above is the official spelling.

## 2. Morse code (ITU-R M.1677-1)

`·` is a dot (dit), `–` is a dash (dah). **Timing:** a dash is three dots; the space inside a letter is one dot; between letters, three dots; between words, seven dots.

| Letter | Code | Letter | Code | Letter | Code |
|---|---|---|---|---|---|
| A | `·–` | B | `–···` | C | `–·–·` |
| D | `–··` | E | `·` | F | `··–·` |
| G | `––·` | H | `····` | I | `··` |
| J | `·–––` | K | `–·–` | L | `·–··` |
| M | `––` | N | `–·` | O | `–––` |
| P | `·––·` | Q | `––·–` | R | `·–·` |
| S | `···` | T | `–` | U | `··–` |
| V | `···–` | W | `·––` | X | `–··–` |
| Y | `–·––` | Z | `––··` |  |  |

| Figure | Code | Figure | Code |
|---|---|---|---|
| 1 | `·––––` | 2 | `··–––` |
| 3 | `···––` | 4 | `····–` |
| 5 | `·····` | 6 | `–····` |
| 7 | `––···` | 8 | `–––··` |
| 9 | `––––·` | 0 | `–––––` |

| Sign | Char | Code |
|---|---|---|
| Full stop (period) | `.` | `·–·–·–` |
| Comma | `,` | `––··––` |
| Colon | `:` | `–––···` |
| Question mark | `?` | `··––··` |
| Apostrophe | `'` | `·––––·` |
| Hyphen | `-` | `–····–` |
| Fraction bar | `/` | `–··–·` |
| Left parenthesis | `(` | `–·––·` |
| Right parenthesis | `)` | `–·––·–` |
| Quotation marks | `"` | `·–··–·` |
| Double hyphen | `=` | `–···–` |
| Cross (addition sign) | `+` | `·–·–·` |
| Commercial at | `@` | `·––·–·` |
| Understood | | `···–·` |
| Error (eight dots) | | `········` |
| Invitation to transmit | | `–·–` |
| Wait | | `·–···` |
| End of work | | `···–·–` |
| Starting signal | | `–·–·–` |

### Prosigns

A prosign is one or two letters sent as a single character (ARRL glossary), so its code is the letters run together, with no letter space. Meanings from ARRL.

| Prosign | Code | Meaning | Same signal in M.1677-1 |
|---|---|---|---|
| K | `–·–` | Go ahead; any station transmit | Invitation to transmit |
| KN | `–·––·` | Only the called station transmit | Left parenthesis `(` |
| AR | `·–·–·` | End of transmission or end of message | Cross (addition sign) `+` |
| AS | `·–···` | Please stand by | Wait |
| SK | `···–·–` | End of contact; sent before the final identification | End of work |
| BT | `–···–` | `TODO(verify)`: ARRL's prosign list does not include BT | Double hyphen `=` |
| R | `·–·` | All received correctly |  |
| CL | `–·–··–··` | Closing, going off the air; sent after the final identification |  |
| BK | `–···–·–` | Break, or back to you |  |

## 3. Common transmissions

| Send | Meaning |
|---|---|
| CQ | Calling any station; the general call for a contact |
| DE | From; this is |
| 73 | Best regards |
| 88 | Love and kisses |
| QRL | I am busy. `QRL?` Are you busy? (checks whether a frequency is in use) |
| QRM | Your transmission is being interfered with (1 nil to 5 extremely) |
| QRN | I am troubled by static (1 to 5) |
| QRO | Increase power |
| QRP | Decrease power |
| QRQ | Send faster |
| QRS | Send more slowly |
| QRT | Stop sending |
| QRV | I am ready |
| QRX | I will call you again at ___ |
| QRZ | You are being called by ___. `QRZ?` Who is calling me? |
| QSB | Your signals are fading |
| QSK | I can hear you between signals; break in |
| QSL | I am acknowledging receipt |
| QSO | I can communicate with ___ (a contact, a conversation) |
| QSY | Change to another frequency |
| QTH | My location is ___ |

A Q signal is a question only when it is followed by a question mark. ARRL's Q-signal sheet notes they are common on phone too ("QRZ?", "QSY to 146.55"); ARRL's operating-procedures unit advises using them on CW and saying what you mean on voice.

### RST signal report

R is readability, S is strength, T is tone. Phone reports leave out the tone.

| # | Readability | Strength | Tone |
|---|---|---|---|
| 1 | Unreadable | Faint signals, barely perceptible | Sixty cycle a.c. or less, very rough and broad |
| 2 | Barely readable, occasional words distinguishable | Very weak signals | Very rough a.c., very harsh and broad |
| 3 | Readable with considerable difficulty | Weak signals | Rough a.c. tone, rectified but not filtered |
| 4 | Readable with practically no difficulty | Fair signals | Rough note, some trace of filtering |
| 5 | Perfectly readable | Fairly good signals | Filtered rectified a.c. but strongly ripple-modulated |
| 6 |  | Good signals | Filtered tone, definite trace of ripple modulation |
| 7 |  | Moderately strong signals | Near pure tone, trace of ripple modulation |
| 8 |  | Strong signals | Near perfect tone, slight trace of modulation |
| 9 |  | Extremely strong signals | Perfect tone, no trace of ripple or modulation of any kind |

Suffixes: X for crystal-control steadiness, C for chirp, K for click. Example from ARRL: RST 368 is "readable with considerable difficulty, good strength, with a slight trace of modulation."

### A contact, start to finish

1. Find a clear frequency first. On CW, `QRL?` asks whether it is in use.
2. **Phone CQ:** "CQ, CQ, CQ. This is KB1AFE, Kilo Bravo One Alfa Foxtrot Echo, KB1AFE calling CQ and standing by." Let up on the push-to-talk between calls.
3. **CW CQ,** a 3x3 call: `CQ CQ CQ DE KA7XYZ KA7XYZ KA7XYZ K`.
4. Exchange a signal report, names, location (QTH) and equipment. Once in contact you do not need phonetics or the other station's call each time.
5. Identify at least every 10 minutes during the contact and at its end (47 CFR 97.119(a)). An automatic CW identifier may not exceed 20 words per minute; phone identification is in English.
6. End with SK before your final identification; send CL after it if you are leaving the air.

Call sign structure (prefix, district digit, suffix) and the four US call sign groups are covered in episode one. `TODO(verify)`: ITU prefix allocation basics were not sourced for this sheet.

## 4. SI prefixes (NIST)

| Prefix | Symbol | Factor |
|---|---|---|
| tera | T | 10¹² |
| giga | G | 10⁹ |
| mega | M | 10⁶ |
| kilo | k | 10³ |
| (none) |  | 10⁰ |
| milli | m | 10⁻³ |
| micro | μ | 10⁻⁶ |
| nano | n | 10⁻⁹ |
| pico | p | 10⁻¹² |

Multiples use uppercase symbols except kilo (k), hecto (h) and deka (da).

**Exam-style conversions,** each from a pool question:

| Question | Conversion |
|---|---|
| T5B01 | 1.5 A = 1500 mA |
| T5B06 | 3000 mA = 3 A |
| T5B03 | 1 kV = 1000 V |
| T5B04 | 1 μV = one one-millionth of a volt |
| T5B05 | 500 mW = 0.5 W |
| T5B08 | 1,000,000 pF = 1 μF |
| G5C08 | 5.0 nF + 5.0 nF + 750 pF (parallel) = 10.750 nF |
| T5C06, T5C07 | kilohertz is kHz, megahertz is MHz; 7,125 kHz = 7.125 MHz |

## 5. Ohm's law

| Letter | Quantity | Unit |
|---|---|---|
| E | Voltage, the difference that makes electrons flow | volts (V) |
| I | Current, the flow of electrons | amperes (A) |
| R | Resistance | ohms (Ω) |
| P | Power, the rate electrical energy is used | watts (W) |

Letters and quantities: T5D01-T5D03 (formulas for current, voltage and resistance), T5A03 (current is the flow of electrons), T5A05 (a voltage difference causes electron flow), T5A10 (power is the rate energy is used). Units: T5A01 (amperes), T5A02 (watts), and the pool answers in volts and ohms (T5D04, T5D10).

**The two formulas the pools print:**

- **E = I × R**, so **I = E / R** and **R = E / I** (T5D01, T5D02, T5D03).
- **P = I × E** (T5C08). Substituting E = I × R gives **P = I² × R**; substituting I = E / R gives **P = E² / R**. The pool's numbers confirm both: G5B05 and G5B03 below.

### The wheel

Every row below is one of the two formulas above, rearranged. Each was checked numerically on T5C09's circuit (13.8 V, 10 A, 138 W, so 1.38 Ω).

| To find | From I and R, or E and I | From P and I, or P and E | From P and R, or E and P |
|---|---|---|---|
| E (volts) | E = I × R | E = P / I | E = √(P × R) |
| I (amperes) | I = E / R | I = P / E | I = √(P / R) |
| R (ohms) | R = E / I | R = P / I² | R = E² / P |
| P (watts) | P = I × E | P = I² × R | P = E² / R |

### Worked examples from the pools

| Question | Given | Work | Answer |
|---|---|---|---|
| T5D08 | 100 Ω across 200 V; find current | I = E / R = 200 / 100 | 2 A |
| T5D05 | 12 V at 1.5 A; find resistance | R = E / I = 12 / 1.5 | 8 Ω |
| T5C10 | 12 V DC at 2.5 A; find power | P = I × E = 2.5 × 12 | 30 W |
| G5B04 | 12 V DC bulb drawing 0.2 A; find power | P = I × E = 0.2 × 12 | 2.4 W |
| G5B03 | 400 V DC across 800 Ω; find power | P = E² / R = 400² / 800 | 200 W |
| G5B05 | 7.0 mA through 1,250 Ω; find power | P = I² × R = 0.007² × 1,250 | ≈ 61 mW |

**Series and parallel:** current is the same through every part of a series circuit, and voltage is the same across every part of a parallel circuit (T5D13, T5D14). Series resistances add; parallel resistances combine as 1/R = 1/R₁ + 1/R₂ + … (G5C03, G5C04). Capacitors and inductors are in section 6.

## 6. Formulas the pools test

Element: **T** Technician, **G** General, **E** Extra, from the question ID. Where a formula is not printed in the pool, the pool's numeric answer was recomputed with it and matched. Ohm's law and power are in section 5.

| Topic | Formula or fact | Pool check |
|---|---|---|
| Series / parallel | Series: same current through every part. Parallel: same voltage across every part; branch currents add | T5D13, T5D14, G5B02 |
| Resistors | Series add. Parallel: 1/R = 1/R₁ + 1/R₂ + … | G5C03: 10, 20, 50 Ω parallel = 5.9 Ω; G5C04: 100 ∥ 200 ≈ 67 Ω |
| Capacitors | Parallel add. Series: 1/C = 1/C₁ + 1/C₂ + … | G5C08 (parallel); G5C09: three 100 μF series = 33.3 μF; G5C12: 20 and 50 μF series = 14.3 μF |
| Inductors | Series add. Parallel: 1/L = 1/L₁ + 1/L₂ + … | G5C11: 20 + 50 mH = 70 mH; G5C10: three 10 mH parallel = 3.3 mH |
| Wavelength | λ (meters) = 300 / f (MHz); wavelength shortens as frequency rises | T3B06, T3B05; T3B11: radio waves travel about 300,000,000 m/s |
| Decibels | 3 dB ≈ 2× power; 10 dB = 10× power; −6 dB = one quarter | T5B09: 5→10 W = 3 dB; T5B11: 20→200 W = 10 dB; T5B10: 12→3 W = −6 dB; G5B01 |
| Decibels | A 1 dB loss ≈ 20.6 % of the power | G5B10 |
| SWR | 1:1 is a perfect match; 4:1 is a mismatch; measure it with a directional wattmeter; solid-state transmitters cut power as SWR rises | T7C04, T7C06, T7C08, T7C05 |
| RMS / peak | V_rms = V_peak / √2; V_p-p = 2 × V_peak. RMS AC heats a resistor the same as DC of that value | G5B07; G5B08: 120 V RMS = 339.4 V p-p; G5B09: 17 V peak ≈ 12 V RMS |
| PEP | PEP = (V_p-p / 2 / √2)² / R; unmodulated carrier PEP = average power | G5B06: 200 V p-p on 50 Ω = 100 W; G5B14: 500 V p-p = 625 W; G5B11, G5B13 |
| Reactance | Inductive reactance rises with frequency; capacitive reactance falls. Symbol X, unit ohm | G5A05, G5A06, G5A09, G5A11 |
| Resonance | f = 1 / (2π√(LC)); X_L and X_C cancel; series RLC impedance ≈ R | G5A12, E5A03; E5A02: 50 μH, 40 pF = 3.56 MHz; E5A10: 50 μH, 10 pF = 7.12 MHz |
| Q and bandwidth | Half-power bandwidth = f / Q; parallel Q = R / X | E5A11: 7.1 MHz, Q 150 = 47.3 kHz; E5A12; E5A09 |
| Time constant | τ = R × C; one time constant charges to 63.2 %, discharges to 36.8 % | E5B01; E5B04: 2 × 220 μF and 2 × 1 MΩ, all parallel = 220 s |
| Phase | In a capacitor, current leads voltage by 90° | E5B09 |
| Admittance | The inverse of impedance | E5B12, G5A07 |

## 7. License classes and exams

| Element | License | Questions | Pass | Current pool |
|---|---|---|---|---|
| 2 | Technician | 35 | 26 correct | 2026-2030, effective 7/01/2026 to 6/30/2030 |
| 3 | General | 35 | 26 correct | 2023-2027, effective 7/01/2023 to 6/30/2027 (6th errata, Feb 4, 2026) |
| 4 | Amateur Extra | 50 | 37 correct | 2024-2028, effective July 1, 2024 (4th errata, Feb 4, 2026). `TODO(verify)`: the end date is not printed in the pool file |

Counts and passing scores: 47 CFR 97.503. Pools: NCVEC. Each pool holds at least ten times the questions on one exam and is normally valid for four years.

## 8. Privileges by class, common bands

Band edges are 47 CFR 97.301 (Region 2, the US mainland). Modes are from the ARRL US allocations page (updated April 14, 2022), checked against the emission table in 47 CFR 97.305(c) as amended through Jan 14, 2026. Maximum power is 1,500 W PEP unless noted, and always the minimum needed. 2200 m and 630 m (General and up) need a one-time Utilities Technology Council registration. 60 m channels are omitted.

### Technician

| Band | Frequencies | Modes |
|---|---|---|
| 80 m | 3.525-3.600 MHz | CW only, 200 W PEP |
| 40 m | 7.025-7.125 MHz | CW only, 200 W PEP |
| 15 m | 21.025-21.200 MHz | CW only, 200 W PEP |
| 10 m | 28.000-28.300 MHz | CW, RTTY/data, 200 W PEP |
| 10 m | 28.300-28.500 MHz | CW, phone, 200 W PEP. `TODO(verify)`: 97.305(c) lists phone and image for 28.3-28.5 MHz; whether image applies to Technicians depends on 97.307(f)(10), not fetched |
| 6 m | 50.0-50.1 MHz | CW only |
| 6 m | 50.1-54.0 MHz | CW, phone, image, MCW, RTTY/data |
| 2 m | 144.0-144.1 MHz | CW only |
| 2 m | 144.1-148.0 MHz | CW, phone, image, MCW, RTTY/data |
| 1.25 m | 222.00-225.00 MHz | CW, phone, image, MCW, RTTY/data |
| 70 cm | 420.0-450.0 MHz | CW, phone, image, MCW, RTTY/data |
| 33 cm | 902.0-928.0 MHz | CW, phone, image, MCW, RTTY/data |
| 23 cm | 1240-1300 MHz | CW, phone, image, MCW, RTTY/data |

VHF and up is the same for every class above Novice. The General and Extra tables list HF only.

### General

| Band | CW, RTTY/data | CW, phone, image |
|---|---|---|
| 160 m | 1.800-2.000 MHz (all modes) | 1.800-2.000 MHz |
| 80 / 75 m | 3.525-3.600 MHz | 3.800-4.000 MHz |
| 40 m | 7.025-7.125 MHz | 7.175-7.300 MHz |
| 30 m | 10.100-10.150 MHz, 200 W PEP | none |
| 20 m | 14.025-14.150 MHz | 14.225-14.350 MHz |
| 17 m | 18.068-18.110 MHz | 18.110-18.168 MHz |
| 15 m | 21.025-21.200 MHz | 21.275-21.450 MHz |
| 12 m | 24.890-24.930 MHz | 24.930-24.990 MHz |
| 10 m | 28.000-28.300 MHz | 28.300-29.700 MHz |

### Amateur Extra

Extra adds the bottom of 80, 40, 20 and 15 m and wider phone segments; 160, 30, 17, 12 and 10 m match General.

| Band | CW, RTTY/data | CW, phone, image |
|---|---|---|
| 80 / 75 m | 3.500-3.600 MHz | 3.600-4.000 MHz |
| 40 m | 7.000-7.125 MHz | 7.125-7.300 MHz |
| 20 m | 14.000-14.150 MHz | 14.150-14.350 MHz |
| 15 m | 21.000-21.200 MHz | 21.200-21.450 MHz |

## Sources

- FAA JO 7110.65, paragraph 2-4-16 and TBL 2-4-1, ICAO Phonetics: https://www.faa.gov/air_traffic/publications/atpubs/atc_html/chap2_section_4.html
- ITU-R M.1677-1 (10/2009), International Morse code: https://www.itu.int/dms_pubrec/itu-r/rec/m/R-REC-M.1677-1-200910-I!!PDF-E.pdf
- ARRL, Communicating with Other Hams: Q-Signals: https://www.arrl.org/files/file/Get%20on%20the%20Air/Comm%20w%20Other%20Hams-Q%20Signals.pdf
- ARRL FSD-220, Communications Procedures, ITU Phonetic Alphabet, R-S-T System: https://www.arrl.org/files/file/Public%20Service/fsd220.pdf
- ARRL Amateur Radio Education & Technology Program, Unit 5, Amateur Radio Operating Procedures: https://www.arrl.org/files/file/LabHandbook/RLH%20Unit%205.pdf
- ARRL Ham Radio Glossary: https://www.arrl.org/ham-radio-glossary
- ARRL, US Amateur Radio Frequency Allocations: https://www.arrl.org/frequency-allocations
- 47 CFR 97.119, Station identification (via Cornell LII; eCFR refused automated fetches): https://www.law.cornell.edu/cfr/text/47/97.119
- 47 CFR 97.301, Authorized frequency bands: https://www.law.cornell.edu/cfr/text/47/97.301
- 47 CFR 97.305, Authorized emission types: https://www.law.cornell.edu/cfr/text/47/97.305
- 47 CFR 97.503, Element standards: https://www.law.cornell.edu/cfr/text/47/97.503
- NIST, Metric (SI) Prefixes: https://www.nist.gov/pml/owm/metric-si-prefixes
- NCVEC, Amateur Question Pools and the 2026-2030 Technician, 2023-2027 General and 2024-2028 Extra pool pages and files: https://ncvec.org/index.php/amateur-question-pools
- HamStudy pool browser, sections T3B, T5A, T5B, T5C, T5D, T7C (E2_2026), G4E, G5A, G5B, G5C (E3_2023), E5A, E5B (E4_2024): https://hamstudy.org/browse/E2_2026/T5D
- ARRL, Getting Licensed, Step by Step: https://www.arrl.org/getting-licensed-step-by-step

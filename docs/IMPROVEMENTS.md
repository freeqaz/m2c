# m2c Improvement Ideas

Tracked improvements and feature requests for m2c, primarily from DC3 decomp work.

## High Priority

### Low-Noise Output Mode

**Source:** seed_chase session (2026-02-04)

Add a mode that suppresses obvious artifacts and highlights stable structure:

- Filter out `phi_*` variables that represent unresolved register tracking
- Filter out `temp_*` assignments that are clearly artifacts
- Filter out `sp*` stack variables that were never properly set
- Highlight the "stable" parts of the output that can be trusted

**Possible implementation:**
```bash
python3 m2c.py --low-noise input.s  # or --clean-output
```

Could also add confidence annotations:
```c
// HIGH confidence - straightforward data flow
result = a + b;

// LOW confidence - register tracking lost
temp_f1 = (f32) spC;  // [m2c: unset register artifact]
```

### Improved Loop Analysis

**Source:** seed_chase session (2026-02-04)

Tight loops with complex iteration patterns produce unreliable output:
- Misattributes loop counters
- Generates incorrect loop bounds
- Confuses loop-carried dependencies

**Investigation needed:**
- Identify why liveness analysis fails for tight loops
- Consider special-casing common loop patterns (for, while with simple conditions)
- Add heuristics for detecting loop-carried values

**Related files:** `flow_graph.py`, `translate.py`

---

## Medium Priority

### Better Unset-Register Handling

When m2c loses track of a register's value, it currently emits artifacts like:
```c
temp_f1 = (f32) spC;  // spC never set
var_r3 = phi_r3;      // phi from unknown source
```

Improvements:
1. Track which registers have known vs unknown provenance
2. Emit warnings/comments when using unset values
3. Option to replace unset values with `/* UNKNOWN */` placeholder

### Register Swap Detection Hints

When the output shows potential register allocation issues (common in REGISTER_SWAP pattern functions), m2c could:
- Detect when two variables are used in symmetric ways
- Suggest which variables might need reordering
- Identify "swappable" variable pairs based on usage patterns

---

## Low Priority / Research

### Context-Aware Decompilation

Use DC3 header context more effectively:
- Auto-detect class method patterns from `this` pointer usage
- Infer virtual function calls from vtable offsets
- Better MSVC calling convention support

### Integration with objdiff

Potential synergies:
- Use objdiff's instruction diff to validate m2c output
- Feed objdiff pattern detection back to guide m2c heuristics
- Combined tool that shows m2c output alongside instruction diff

---

## Completed

- [x] VMX128 instruction support (2026-01)
- [x] MSVC symbol parsing fixes (2026-01, in progress)

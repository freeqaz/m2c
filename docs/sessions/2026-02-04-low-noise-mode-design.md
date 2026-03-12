# m2c Low-Noise Mode Design Session

**Date:** 2026-02-04
**Status:** Ready for Implementation
**Goal:** Add output filtering/annotation to help decomp workflows focus on match-critical code

## Background

When using m2c for decompilation matching work, the output often contains "noise" - artifacts from the decompilation process that won't exist in the final matched code. This noise increases cognitive load when comparing against target assembly.

### Types of Noise

| Artifact | Cause | Example |
|----------|-------|---------|
| `phi_*` variables | SSA phi nodes from control flow merges | `phi_r3 = ...` |
| `temp_*` variables | Intermediate values needing storage | `temp_r5 = foo()` |
| `unksp*` variables | Stack accesses without resolved structure | `unksp48 = 0` |
| `unk_0x48` fields | Struct field access without type info | `self->unk_0x48` |

### Use Case

This tooling is for **decomp work**, not producing compilable code. Goals:
- Reduce visual noise
- Help focus on match-critical logic
- Annotate uncertain/artifact code
- **Not** produce valid C syntax (that's a non-goal)

---

## Existing Infrastructure (Key Discovery)

Deep dive into m2c revealed significant existing support:

### Already Implemented

| Feature | How It Works |
|---------|--------------|
| **Temp collapsing** | `EvalOnceExpr` with `transparent`/`trivial` flags already inlines single-use expressions. Temps only appear when multi-use or function calls. |
| **Comment infrastructure** | `fmt.with_comments(content, comments)` and `SimpleStatement(comments=[...])` |
| **Register in var names** | `Var.prefix` stores `temp_r5`, `phi_r3` - register info already visible |
| **Struct offset stored** | `StructAccess.offset` is an int field, used to generate `unk_0x48` names |
| **Expression provenance** | `sources: List[Reference]` tracks origin on `EvalOnceExpr`, `NaivePhiExpr` |
| **Artifact lists** | `stack_info.naive_phi_vars`, `stack_info.temp_vars`, `LocalVar.path is None` |

### Implications

1. **No need to track "low confidence" through expression trees** - artifacts are identifiable structurally
2. **`--collapse-temps` is unnecessary** - already the default behavior
3. **Frozen FlowGraph is a non-issue** - we don't need to modify it
4. **Implementation is much simpler than originally planned**

---

## Design

### Noise Levels

```python
class NoiseLevel(ChoicesEnum):
    FULL = "full"       # Default - show everything (current behavior)
    LOW = "low"         # Annotate artifact declarations with comments
    MINIMAL = "minimal" # Comment out artifact declarations entirely
```

### Example Outputs

**Input (current m2c output):**
```c
int test_func(int arg0) {
    int temp_r5;
    int phi_r3;

    temp_r5 = some_call();
    if (arg0 > 0) {
        phi_r3 = temp_r5 + 1;
    } else {
        phi_r3 = arg0;
    }
    return phi_r3;
}
```

**With `--noise=low`:**
```c
int test_func(int arg0) {
    int temp_r5;  /* artifact */
    int phi_r3;   /* artifact */

    temp_r5 = some_call();
    if (arg0 > 0) {
        phi_r3 = temp_r5 + 1;
    } else {
        phi_r3 = arg0;
    }
    return phi_r3;
}
```

**With `--noise=minimal`:**
```c
int test_func(int arg0) {
    /* int temp_r5; -- artifact */
    /* int phi_r3; -- artifact */

    temp_r5 = some_call();
    if (arg0 > 0) {
        phi_r3 = temp_r5 + 1;
    } else {
        phi_r3 = arg0;
    }
    return phi_r3;
}
```

Note: We only comment out **declarations**, not usages. Commenting out usages inline would be complex and provides minimal additional value - the declaration annotation is sufficient to mark what's an artifact.

**With `--show-offsets`:**
```c
self->mMember = x;      /* 0x48 */
self->unk_0x50 = y;     /* 0x50 */
```

**With `--decomp` preset:**
Combines `--noise=low` + `--show-offsets` for optimal decomp workflow.

---

## Design Decisions

### 1. Minimal mode: Comment out declarations only
```c
/* int phi_r3; -- artifact */
```
- Preserves structure visibility
- Doesn't try to comment out usages inline (too complex, low value)
- Usages still show `phi_r3` but you know from declaration it's an artifact

### 2. Drop `--collapse-temps`
Already the default behavior in m2c. Temps only appear when:
- Expression used multiple times
- Function calls (`emit_exactly_once`)
- Forced emit situations

Could add `--no-collapse-temps` later if needed for debugging.

### 3. `--show-offsets`: End-of-line comments
```c
self->field = x;  /* 0x48 */
```
Simple and non-intrusive. Helps match against objdiff output like `stw r3, 0x48(r4)`.

### 4. Register provenance: Already in var names
`temp_r5` and `phi_r3` already tell you the register. Additional `--show-regs` feature deferred - lower priority since info is already there.

### 5. Orchestrator integration: Default on
The DC3 orchestrator's `analyze-function` MCP tool should use `--decomp` by default.

---

## Implementation Plan

### Phase 1: Core Noise Filtering (~25 lines of real code)

**1. Add NoiseLevel enum to `options.py`:**
```python
# After line 23 (after other enums, outside CodingStyle)
class NoiseLevel(ChoicesEnum):
    FULL = "full"
    LOW = "low"
    MINIMAL = "minimal"
```

**2. Add to Options dataclass (`options.py` ~line 186):**
```python
noise_level: NoiseLevel = NoiseLevel.FULL
```

**3. Add CLI argument (`main.py` in Formatting Options group ~line 395):**
```python
group.add_argument(
    "--noise",
    dest="noise_level",
    type=NoiseLevel,
    choices=list(NoiseLevel),
    default="full",
    help="Output noise level: full (default), low (annotate artifacts), minimal (comment out artifacts)",
)
group.add_argument(
    "--low-noise",
    dest="noise_level",
    action="store_const",
    const=NoiseLevel.LOW,
    help="Shorthand for --noise=low",
)
```

**4. Wire up in Options construction (`main.py` ~line 674):**
```python
noise_level=args.noise_level,
```

**5. Modify declaration output (`if_statements.py` ~lines 1493-1508):**
```python
# For temp_vars
for var in function_info.stack_info.temp_vars:
    if var.is_emitted:
        type_decl = var.type.to_decl(var.format(fmt), fmt)
        if options.noise_level == NoiseLevel.MINIMAL:
            temp_decls.append(f"/* {type_decl}; -- artifact */")
        elif options.noise_level == NoiseLevel.LOW:
            temp_decls.append((f"{type_decl};", ["artifact"]))  # with comment
        else:
            temp_decls.append(f"{type_decl};")

# Similar for naive_phi_vars
for phi_var in function_info.stack_info.naive_phi_vars:
    type_decl = phi_var.type.to_decl(phi_var.get_var_name(), fmt)
    if options.noise_level == NoiseLevel.MINIMAL:
        function_lines.append(SimpleStatement(f"/* {type_decl}; -- artifact */").format(fmt))
    elif options.noise_level == NoiseLevel.LOW:
        function_lines.append(SimpleStatement(f"{type_decl};", comments=["artifact"]).format(fmt))
    else:
        function_lines.append(SimpleStatement(f"{type_decl};").format(fmt))
```

### Phase 2: Offset Annotations (~10 lines)

**1. Add to Options:**
```python
show_offsets: bool = False
```

**2. Add CLI arg:**
```python
group.add_argument("--show-offsets", action="store_true", help="Show struct field offsets in comments")
```

**3. Add to Formatter:**
```python
show_offsets: bool = False
```

**4. Modify `StructAccess.format()` (`translate.py` ~line 1560):**
```python
def format(self, fmt: Formatter) -> str:
    # ... existing logic to build result ...

    if fmt.show_offsets and self.offset != 0:
        return f"{result}  /* 0x{self.offset:X} */"
    return result
```

### Phase 3: Decomp Preset (~5 lines)

```python
group.add_argument(
    "--decomp",
    action="store_true",
    help="Decomp-friendly output: enables --noise=low --show-offsets",
)

# In option processing:
if args.decomp:
    if args.noise_level == NoiseLevel.FULL:  # not explicitly set
        args.noise_level = NoiseLevel.LOW
    args.show_offsets = True
```

### Phase 4: Orchestrator Integration

Update DC3 orchestrator's `analyze-function` MCP tool to pass `--decomp` flag by default.

---

## Files to Modify

| File | Changes | Lines |
|------|---------|-------|
| `m2c/options.py` | Add `NoiseLevel` enum, add to `Options`, add `show_offsets` | ~10 |
| `m2c/main.py` | Add CLI args, wire to Options | ~20 |
| `m2c/if_statements.py` | Annotate/comment-out declarations | ~15 |
| `m2c/translate.py` | Add offset comment in `StructAccess.format()` | ~5 |

**Total: ~50 lines of code**

---

## Testing

### Manual Verification
```bash
# Test flag parsing
python3 -m m2c --help | grep -A2 noise

# Test with real code
python3 -m m2c -t ppc some_function.s              # default
python3 -m m2c -t ppc --noise=low some_function.s  # annotated
python3 -m m2c -t ppc --noise=minimal some_function.s  # commented out
python3 -m m2c -t ppc --decomp some_function.s     # preset
```

### Regression Check
```bash
# Ensure default output unchanged
python3 -m m2c -t ppc test.s > /tmp/before.c
# ... make changes ...
python3 -m m2c -t ppc test.s > /tmp/after.c
diff /tmp/before.c /tmp/after.c  # should be identical
```

---

## Future Enhancements (Deferred)

| Feature | Notes |
|---------|-------|
| `--show-regs` | Register info already in var names (`temp_r5`). Could add equation comments later. |
| `--no-collapse-temps` | Force all temps to be emitted. Useful for debugging register allocation. |
| Inline usage annotation | Comment out artifact usages like `/* phi_r3 */`. Complex, low value. |
| Confidence tiers | Distinguish "artifact" vs "uncertain" vs "unknown". May not be needed. |

---

## References

- m2c source: `/home/free/code/milohax/m2c/`
- Key files: `options.py`, `main.py`, `if_statements.py`, `translate.py`
- EvalOnceExpr transparency logic: `translate.py:1809-1902`
- Declaration output: `if_statements.py:1493-1508`

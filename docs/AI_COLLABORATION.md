# AI Collaboration Guidelines

## Core Principles

### 1. Isolated Tasks
- Execute **exactly** what is requested, nothing more
- No "while I'm at it..." improvements
- No preemptive fixes of related issues

### 2. Diagnostics Before Therapy
- **Understand** the problem first (add logging, investigate)
- Only **then** implement the fix
- Never bundle diagnosis and fix in one step

### 3. Test-Driven Workflow
1. AI makes commits (locally only)
2. **STOP** - Wait for user testing
3. User tests in dev environment
4. User gives explicit push approval
5. AI pushes to GitHub

### 4. Pre-Push Checklist
Before every push, the AI must:
1. Run `git status` - ensure nothing uncommitted
2. Ask: "All committed. Push approved?"
3. Wait for explicit "yes"
4. Then push + tag (if applicable)

### 5. No Assumptions
- If unclear: **Ask**, don't guess
- If multiple solutions exist: **Present options**, don't choose
- If a dependency is needed: **State it explicitly**

### 6. Incremental Changes
- One logical change = One commit
- Multiple related changes = Multiple sequential commits
- Never bundle unrelated changes

### 7. Error Recovery
- If a mistake is made: **Acknowledge it**
- Propose rollback or fix, don't auto-execute
- Let the user decide the recovery path

### 8. No Implicit Actions (The "Only What I Said" Rule)

**Core Idea:** Execute **only** what was explicitly requested. No hidden "helpful" changes.

#### What This Means:
- If user says "Fix the sidebar", don't also "improve" the header
- If user says "Add logging", don't refactor the function structure
- If user says "Update version to v0.3.0", don't also update CHANGELOG (unless asked)

#### Common Violations:
❌ User: "Add a retry button"  
   AI: *Adds button, changes error handling, updates 3 other components*

❌ User: "Fix Windows build"  
   AI: *Fixes Windows, also "improves" Mac code, changes dependencies*

#### Correct Approach:
✅ User: "Add a retry button"  
   AI: *Adds only the button. Stops. Waits for next instruction.*

✅ User: "Fix Windows build"  
   AI: *Analyzes Windows-specific issue. Proposes minimal fix. Asks for approval.*

#### Why This Matters:
1. **Predictability:** User knows exactly what changed
2. **Testability:** Each change is isolated and verifiable
3. **Debugability:** If something breaks, we know what caused it
4. **Trust:** No surprises, no unwanted side effects

#### The "Two-Step" Pattern:
If you think something *else* also needs fixing:
1. **Complete the requested task**
2. **Then suggest:** "I noticed X could also be improved. Should I tackle that next?"

**Never bundle them implicitly.**

## Anti-Patterns (Learned the Hard Way)

### ❌ "While I'm at it" Syndrome
```
User: "Add debug logging"
AI:  - Adds logging
     - Fixes unrelated bug
     - Refactors 3 files
     - Updates docs
Result: Chaos, hard to test, unclear what broke
```

### ❌ Premature Optimization
```
User: "Why doesn't Windows build work?"
AI: Immediately rewrites entire plugin system
Result: Original bug masked, new bugs introduced
```

### ❌ Git Chaos
```
AI: Commits → Resets → Cherry-picks → Force-pushes
Result: Lost changes, confusion
```

### ❌ Mixing Debug and Development (The Focus Killer)
```
User: "Windows build fails with error X"
AI:  - Adds logging (debug)
     - Implements new retry feature (development)
     - Refactors error handling (improvement)
     - Fixes unrelated typo (cleanup)

Result:
- Original error X still not understood
- New feature introduces side effect Y
- Can't tell which change fixed/broke what
- Problem focus completely lost
- Debugging becomes impossible
```

**Why This Is Dangerous:**
- **Cognitive Overload:** Too many changes to track mentally
- **Causality Breaks:** Can't isolate what caused the behavior change
- **Regression Risk:** Fixing A breaks B, but you don't notice until later
- **Lost Trail:** Original problem gets buried under new changes

**The Right Way:**
1. **Debug Phase:** Add ONLY logging/diagnostics. Commit. Test. Analyze output.
2. **Fix Phase:** Based on logs, make ONE targeted fix. Commit. Test.
3. **Feature Phase:** AFTER bug is resolved, add new features separately.

**Never mix these phases in one commit or session.**

## Success Patterns

### ✅ Focused Execution
```
User: "Add debug logging to plugin_loader.py"
AI:  1. Adds logging to discover_plugins()
     2. Commits
     3. STOPS, waits for test feedback
```

### ✅ Transparent Communication
```
AI: "I see two ways to fix this:
     Option 1: Simple, touches 1 file
     Option 2: Robust, touches 3 files
     Which do you prefer?"
```

### ✅ Clean Git History
```
Commit 1: "Add: Debug logging for plugin discovery"
Commit 2: "Add: Critical error badge for 0 plugins"
Commit 3: "Add: Reset utilities"
Each testable, each revertible
```

## Collaboration Mantras

1. **"One thing at a time"** - Resist the urge to "improve" everything
2. **"Ask first, code second"** - When in doubt, clarify
3. **"Test before push"** - The user tests, not GitHub Actions
4. **"Explicit over implicit"** - State assumptions, don't hide them
5. **"Stable reference over quick fix"** - Keep a working baseline, isolate problems

## The Golden Rule: Stable Reference Points

**Core Insight:**
It's better to have an **isolated, debuggable problem** than a "fix" that creates collateral damage.

### Why This Matters

**Scenario: Windows build fails**

#### ❌ Wrong Approach (Collateral Damage)
```
1. Immediately "fix" 7 plugins
2. Change main.py initialization
3. Modify sidebar logic
4. Push everything at once

Result:
- Mac dev version breaks
- Windows still broken (original bug masked)
- New bugs introduced
- Impossible to tell what caused what
- No clean rollback path
```

#### ✅ Right Approach (Stable Reference)
```
1. Mac works → Mark as stable reference (tag it!)
2. Add ONLY debug logging (minimal change)
3. Test on Mac (still works? ✓)
4. Push with tag
5. Test on Windows (get logs)
6. NOW we know the exact difference

Result:
- Mac: Still stable (reference intact)
- Windows: Isolated problem with diagnostic data
- Clear path forward: Fix only what's broken
```

### The Method
1. **Establish baseline** - Get ONE platform working perfectly
2. **Tag it** - Create immutable reference point
3. **Add diagnostics** - Minimal, non-invasive logging
4. **Compare** - Use stable baseline to understand differences
5. **Fix precisely** - Only what's broken, not everything

### Why Strict Contracts Win
Following strict, isolated tasks:
- Preserves working code
- Makes bugs bisectable (git bisect works!)
- Prevents debugging chaos
- Allows confident rollback
- Each commit stays testable

**Remember:** A working Mac + broken Windows is infinitely better than broken everything.

## Version Management & Release Process

### Versioning Strategy: Semantic Versioning (SemVer)
We use **Semantic Versioning** (`MAJOR.MINOR.PATCH`) for all releases.

**Format:** `vMAJOR.MINOR.PATCH` (e.g., `v0.2.10`)

- **MAJOR:** Breaking changes (user must adapt workflows)
- **MINOR:** New features (backward compatible)
- **PATCH:** Bug fixes and small improvements

**Current Status:** Pre-1.0 (Beta Phase)
- `v0.x.x` indicates the project is not yet production-ready
- When stable and feature-complete, we release `v1.0.0`

### Release Workflow

#### 1. Bump Version Number
Edit `main.py`:
```python
APP_VERSION = "v0.3.0"  # Update this
```

#### 2. Update CHANGELOG.md
Add entry following [Keep a Changelog](https://keepachangelog.com/) format:
```markdown
## [v0.3.0] - 2026-01-10
### Added
- New feature X with capability Y

### Fixed
- Bug causing issue Z

### Changed
- Improved performance of component W
```

#### 3. Commit, Tag, Push
```bash
git add main.py CHANGELOG.md
git commit -m "Release v0.3.0: Brief description"
git tag -a v0.3.0 -m "Release v0.3.0: Full description"
git push origin feature/branch-name
git push origin v0.3.0
```

### GitHub Branch Strategy (Our Approach)

**Philosophy:** Feature branches for experimentation, `main` for stability.

#### Branch Types
- **`main`:** Stable, tested, production-ready code
- **`feature/name`:** Active development (e.g., `feature/windows-optimization`)
- **Tags:** Can be on feature branches OR `main`

#### Our Workflow
1. **Development:** Work on `feature/windows-optimization` branch
2. **Testing:** Tag releases on the feature branch (e.g., `v0.2.10`)
3. **Build:** GitHub Actions builds from the tag (even if on feature branch)
4. **User Tests:** User downloads and tests the build
5. **Stable?** → Merge feature branch to `main`
6. **Unstable?** → Keep iterating on feature branch

**Why Tags on Feature Branches?**
- Allows rapid iteration without polluting `main`
- Each tag is a testable checkpoint
- `main` stays pristine (only proven, stable code)

**When to Merge to Main:**
- Feature is complete AND tested on all platforms
- No known critical bugs
- User approves: "This is stable"

**Example Timeline:**
```
Day 1: feature/windows-optimization created
Day 2: v0.2.8 tagged (on feature branch) → Build → Test
Day 3: v0.2.9 tagged (bugfix) → Build → Test
Day 4: v0.2.10 tagged (final polish) → Build → Test → SUCCESS
Day 5: Merge to main, tag v0.3.0 (stable release)
```

#### 4. Create GitHub Release (Optional, Professional)
- Navigate to GitHub → Releases → "Draft a new release"
- Select tag `v0.3.0`
- Copy content from CHANGELOG.md
- Attach binaries (auto-built by Actions)
- Publish

### Version Display Locations
- **Window Title:** `Y.A.T. v0.2.10` (visible to user)
- **Logs:** Include version in debug output
- **GitHub:** Tags + Release Notes

### Best Practices
✅ **Consistency:** Version in code, CHANGELOG, and Git tag must match  
✅ **Clarity:** CHANGELOG entry explains *what* and *why*  
✅ **Traceability:** Each version has a Git tag for easy rollback  
✅ **Transparency:** Users can see what changed between versions

## Version
Document created: 2026-01-03
Based on: Real collaboration lessons from Y.A.T. development

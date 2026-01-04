# Week 1 — Logic Foundations & Automated Reasoning

This week implements the core machinery of propositional and first-order automated reasoning, inspired by the Logic Theorist and classical resolution-based proof systems. All components were implemented from scratch using the Python standard library and validated using the provided autograders.

## What Was Implemented

### 1. Propositional Logic → CNF (`prop_logic/to_cnf.py`)

A complete structural CNF conversion pipeline for propositional logic expression trees.

**Implemented transformations:**

- **Implication elimination**  
  `A → B ⟶ ¬A ∨ B`

- **Negation Normal Form (NNF)**
  - De Morgan's laws
  - Double / nested negation elimination

- **Distribution of OR over AND**

- **Clause flattening and normalization**

**Output representation:**
- CNF is represented as `List[Set[str]]`
- Literals are strings: `"P"` or `"~P"`

**Design choices:**
- Conversion is done structurally on the AST, not via truth tables
- OR–AND distribution is handled recursively to avoid ad-hoc flattening
- Final CNF is guaranteed to contain only disjunctions of literals inside conjunctions

*This module passes all 15 CNF autograder tests, including nested negations and non-trivial distributions.*

---

### 2. DPLL SAT Solver (`prop_logic/dpll.py`)

A full implementation of the Davis–Putnam–Logemann–Loveland (DPLL) algorithm for SAT solving.

**Implemented features:**
- Unit clause propagation
- Pure literal elimination
- Recursive backtracking with branching
- Early conflict detection

**Interface:**
```python
(satisfiable: bool, assignment: dict)
```

**Design choices:**
- Assignments are copied per recursion to avoid mutation bugs
- Literals are parsed syntactically (`"~P"` vs `"P"`)
- Clause simplification is performed eagerly after each assignment
- Solver stops as soon as a satisfying assignment is found

**This solver correctly handles:**
- Contradictory unit clauses
- Chains of implications
- Minimal satisfying assignments

*All 15 DPLL autograder tests pass.*

---

### 3. First-Order Logic — Robinson's Resolution (`fol/robinson.py`)

An implementation of Robinson's resolution algorithm for First-Order Logic with unification and bounded search.

**Implemented components:**
- Literal parsing (predicate, arguments, polarity)
- **Unification** with:
  - Most General Unifier (MGU)
  - Occurs check
- Resolution between complementary literals
- Iterative deepening via `max_iterations`
- Timeout handling for undecidable cases

**Output:**
```python
("UNSAT", proof)   # if empty clause is derived
("TIMEOUT", [])    # if no contradiction found within bounds
```

**Design choices:**
- Clauses are treated as sets to avoid duplicate literals
- Substitutions are applied immediately after resolution
- Resolution history is tracked only for UNSAT proofs
- Timeout is treated as a first-class correct outcome, not a failure

**This module demonstrates:**
- Correct refutation of logically inconsistent clause sets
- Proper non-termination handling for satisfiable FOL inputs

*All 15 FOL autograder tests pass, including cases requiring unification and occurs checks.*

---

## Key Insights from the Implementation

1. **CNF correctness is structural, not semantic**  
   Logical equivalence alone is insufficient—distribution must be exact.

2. **DPLL is simple but fragile**  
   Small mistakes in clause simplification or assignment propagation lead to silent failures.

3. **Unification is the heart of FOL resolution**  
   Most bugs came from inconsistent substitution application, not resolution itself.

4. **FOL undecidability is very real**  
   Timeouts are not edge cases; they are expected and correct behavior.

5. **Resolution ≠ Prolog**  
   Robinson's resolution is fundamentally different from goal-directed logic programming.

---

## Verification

All implementations were verified using the provided autograders:

```bash
cd Week1/prop_logic
python autograder.py

cd Week1/fol
python autograder.py
```

**Environment:**
- Python ≥ 3.6
- Standard library only
- No external dependencies

---

## Outcome

At the end of Week 1, the project includes:

- ✅ A working propositional CNF converter
- ✅ A complete DPLL SAT solver
- ✅ A bounded first-order logic resolution prover

Together, these form a foundational symbolic AI reasoning stack, closely aligned with the ideas introduced by the original Logic Theorist (1956) and modern automated theorem proving.


# Week 2 — Resolution Control, Search Strategies & Clause Management

Week 2 extends the basic resolution prover from Week 1 by incorporating classical **search control and redundancy management techniques** used in practical automated theorem provers. The focus is on *how* resolution is performed rather than *whether* it is possible.

The implementations and experiments in this week are inspired by Otter-style provers and modern saturation-based theorem proving.

---

## What Was Implemented

### 1. Given-Clause Algorithm

Read upon a saturation-style resolution loop based on the **Given-Clause Algorithm**, separating clauses into:

- **Active set** (processed clauses)
- **Passive set** (unprocessed clauses)

At each iteration:
1. A clause is selected from the passive set (the *given clause*)
2. It is moved to the active set
3. Resolution is performed only between the given clause and active clauses
4. Newly generated clauses are filtered and inserted into the passive set

Design choices:
- Strict separation of active/passive clauses to control combinatorial explosion
- Resolution is asymmetric by design (given × active)
- Algorithm terminates on empty clause or resource limits

This replaces naïve pairwise resolution used in Week 1.

---

### 2. Set of Support (SOS) Strategy

Read upon **Set of Support (SOS)** as a restriction on resolution to improve goal-directedness.

Key behavior:
- Initial clauses are divided into:
  - Background knowledge
  - Set of Support (typically negated conjecture)
- Resolution is allowed only if **at least one parent clause is from SOS**

Effects:
- Prevents irrelevant resolutions among background axioms
- Greatly reduces search space
- Preserves refutational completeness

SOS is integrated directly into the given-clause selection logic.

---

### 3. Subsumption & Redundancy Elimination

Read upon **forward and backward subsumption** to remove redundant clauses.

Subsumption logic:
- Clause C₁ subsumes C₂ if there exists a substitution θ such that  
  `C₁θ ⊆ C₂`

Applied as:
- **Forward subsumption**: discard newly generated clauses if subsumed
- **Backward subsumption**: remove existing clauses subsumed by a new one

Additional redundancy handling:
- Duplicate clause elimination
- Tautology detection
- Literal-level simplifications

These mechanisms are essential for keeping the clause database manageable.

---

### 4. Clause Weighting & Selection Heuristics

Read upon basic **clause weighting** and **selection heuristics** to guide search.

Clause metrics explored:
- Clause length (number of literals)
- Symbol count
- Variable count
- Depth / structural complexity

Selection strategies:
- Lightest clause first
- FIFO / age-based selection
- Hybrid heuristics (weight + age)

Design insight:
- No single heuristic dominates
- Weighting dramatically affects convergence speed
- Heuristics trade completeness speed vs exploration breadth

---

### 5. Search Perspective

Viewed resolution as a **state-space search problem**:

- States: clause sets
- Actions: resolution inferences
- Goal: derive empty clause

Connections explored:
- Uninformed search → naïve resolution
- Informed search → weighting & heuristics
- Search control as a precursor to ML-guided theorem proving

This perspective bridges symbolic reasoning and modern heuristic search.

---

## Key Insights

- Resolution without control is impractical beyond toy problems
- Given-Clause Algorithm is the backbone of real-world provers
- SOS dramatically improves relevance without sacrificing correctness
- Subsumption is expensive but indispensable
- Clause selection heuristics define prover behavior more than inference rules
- Theorem proving is fundamentally a search problem

---

## References & Influences

- Otter Theorem Prover Manual (Given-Clause model)
- Robinson-style saturation provers
- SOS strategy lecture notes (Schubert, Reger)
- Redundancy control techniques in resolution
- Search algorithms from AI foundations

---

## Outcome
This week marks the transition from *theoretical completeness* to *practical automated reasoning*, laying the groundwork for advanced provers and heuristic or ML-guided inference systems.

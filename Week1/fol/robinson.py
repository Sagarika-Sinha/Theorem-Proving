from typing import List, Tuple, Dict, Optional
import itertools

def is_variable(term: str) -> bool:
    return term[0].islower() or term == "_"

def parse_term(term: str):
     
    if "(" not in term:
        return term, []

    fname, rest = term.split("(", 1)
    args = rest[:-1].split(",") if rest[:-1] else []
    return fname, args

def parse_literal(lit: str):

    negated = lit.startswith("~")
    if negated:
        lit = lit[1:]
      
    pred, rest = lit.split("(", 1)
    args = rest[:-1].split(",") if rest[:-1] else []
    return negated, pred, args

def substitute_term(term: str, subs: Dict[str, str]) -> str:
    while term in subs:
        term = subs[term]
    return term

def apply_substitution_literal(lit: str, subs: Dict[str, str]) -> str:
    neg, pred, args = parse_literal(lit)
    new_args = [substitute_term(a, subs) for a in args]
    s = f"{pred}({','.join(new_args)})"
    return "~" + s if neg else s

def unify_terms(t1: str, t2: str, subs: Dict[str, str]) -> Optional[Dict[str, str]]:
    t1 = substitute_term(t1, subs)
    t2 = substitute_term(t2, subs)

    if t1 == t2:
        return subs

    if is_variable(t1):
        subs[t1] = t2
        return subs

    if is_variable(t2):
        subs[t2] = t1
        return subs

    f1, args1 = parse_term(t1)
    f2, args2 = parse_term(t2)

    if f1 != f2 or len(args1) != len(args2):
        return None
     
    for a1, a2 in zip(args1, args2):
        subs = unify_terms(a1, a2, subs)
        if subs is None:
            return None
        
    return subs


def unify_literals(l1: str, l2: str) -> Optional[Dict[str, str]]:
    neg1, p1, args1 = parse_literal(l1)
    neg2, p2, args2 = parse_literal(l2)

    if p1 != p2 or neg1 == neg2 or len(args1) != len(args2):
        return None

    subs: Dict[str, str] = {}
    for a1, a2 in zip(args1, args2):
        subs = unify_terms(a1, a2, subs)
        if subs is None:
            return None

    return subs

def robinson_resolution(
    clauses: List[List[str]],
    max_iterations: int = 1000
) -> Tuple[str, List]:

    clauses = [list(set(c)) for c in clauses]
    seen = set(tuple(sorted(c)) for c in clauses)
    proof = []

    for _ in range(max_iterations):
        new_clause_added = False

        for c1, c2 in itertools.combinations(clauses, 2):
            for l1 in c1:
                for l2 in c2:
                    subs = unify_literals(l1, l2)
                    if subs is None:
                        continue

                    resolvent = []

                    for lit in c1:
                        if lit != l1:
                            resolvent.append(
                                apply_substitution_literal(lit, subs)
                            )
                    for lit in c2:
                        if lit != l2:
                            resolvent.append(
                                apply_substitution_literal(lit, subs)
                            )

                    resolvent = list(set(resolvent))

                    if not resolvent:
                        proof.append((c1, c2, {}))
                        return "UNSAT", proof

                    r_tuple = tuple(sorted(resolvent))
                    if r_tuple not in seen:
                        seen.add(r_tuple)
                        clauses.append(resolvent)
                        proof.append((c1, c2, resolvent))
                        new_clause_added = True

        if not new_clause_added:
            break

    return "TIMEOUT", []

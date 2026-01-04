def dpll(clauses,assignment=None):
    if assignment is None:assignment={}
    clauses=[list(c) if isinstance(c,set) else c for c in clauses]

    if not clauses:return True,assignment
    if any(len(c)==0 for c in clauses):return False,None

    while True:
        units=[c[0] for c in clauses if len(c)==1]
        if not units:break
        for u in units:
            v=u.lstrip('~');val=not u.startswith('~')
            if v in assignment and assignment[v]!=val:return False,None
            assignment[v]=val
            new=[]
            for c in clauses:
                if u in c:continue
                neg='~'+v if val else v
                nc=[l for l in c if l!=neg]
                if not nc:return False,None
                new.append(nc)
            clauses=new

    lits={l for c in clauses for l in c}
    for l in lits:
        v=l.lstrip('~')
        if v in assignment:continue
        neg='~'+v if not l.startswith('~') else v
        if neg not in lits:
            assignment[v]=not l.startswith('~')
            clauses=[c for c in clauses if l not in c]

    if not clauses:return True,assignment

    vars={l.lstrip('~') for c in clauses for l in c}-set(assignment)
    if not vars:return True,assignment
    v=vars.pop()

    at=dict(assignment);at[v]=True
    nt=[];ok=True
    for c in clauses:
        if v in c:continue
        if '~'+v in c:
            nc=[l for l in c if l!='~'+v]
            if not nc:ok=False;break
            nt.append(nc)
        else:nt.append(c)
    if ok:
        s,r=dpll(nt,at)
        if s:return True,r

    af=dict(assignment);af[v]=False
    nf=[];ok=True
    for c in clauses:
        if '~'+v in c:continue
        if v in c:
            nc=[l for l in c if l!=v]
            if not nc:ok=False;break
            nf.append(nc)
        else:nf.append(c)
    if ok:return dpll(nf,af)

    return False,None

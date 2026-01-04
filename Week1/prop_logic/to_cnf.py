class Expr:pass
class Var(Expr):
    def __init__(self,name):self.name=name
class Not(Expr):
    def __init__(self,expr):self.expr=expr
class And(Expr):
    def __init__(self,left,right):self.left=left;self.right=right
class Or(Expr):
    def __init__(self,left,right):self.left=left;self.right=right
class Implies(Expr):
    def __init__(self,left,right):self.left=left;self.right=right

def eliminate_implications(expr):
    if isinstance(expr,Implies):return Or(Not(eliminate_implications(expr.left)),eliminate_implications(expr.right))
    if isinstance(expr,And):return And(eliminate_implications(expr.left),eliminate_implications(expr.right))
    if isinstance(expr,Or):return Or(eliminate_implications(expr.left),eliminate_implications(expr.right))
    if isinstance(expr,Not):return Not(eliminate_implications(expr.expr))
    return expr

def move_not_inwards(expr):
    if isinstance(expr,Not):
        inner=expr.expr
        if isinstance(inner,Not):return move_not_inwards(inner.expr)
        if isinstance(inner,And):return Or(move_not_inwards(Not(inner.left)),move_not_inwards(Not(inner.right)))
        if isinstance(inner,Or):return And(move_not_inwards(Not(inner.left)),move_not_inwards(Not(inner.right)))
        return expr
    if isinstance(expr,And):return And(move_not_inwards(expr.left),move_not_inwards(expr.right))
    if isinstance(expr,Or):return Or(move_not_inwards(expr.left),move_not_inwards(expr.right))
    return expr

def distribute(expr):
    if isinstance(expr,Or):
        A=distribute(expr.left)
        B=distribute(expr.right)
        if isinstance(A,And):return And(distribute(Or(A.left,B)),distribute(Or(A.right,B)))
        if isinstance(B,And):return And(distribute(Or(A,B.left)),distribute(Or(A,B.right)))
        return Or(A,B)
    if isinstance(expr,And):return And(distribute(expr.left),distribute(expr.right))
    return expr

def collect_literals(expr):
    if isinstance(expr,Or):return collect_literals(expr.left)|collect_literals(expr.right)
    if isinstance(expr,Var):return {expr.name}
    if isinstance(expr,Not) and isinstance(expr.expr,Var):return {"~"+expr.expr.name}
    raise ValueError("Invalid CNF literal")

def flatten_and(expr):
    if isinstance(expr,And):return flatten_and(expr.left)+flatten_and(expr.right)
    return [expr]

def to_cnf(expr):
    expr=eliminate_implications(expr)
    expr=move_not_inwards(expr)
    expr=distribute(expr)
    clauses=[]
    for p in flatten_and(expr):clauses.append(sorted(collect_literals(p)))
    return clauses

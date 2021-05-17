import copy
from collections import OrderedDict
from asdl.asdl import *
from asdl.asdl_ast import AbstractSyntaxTree
from asdl.lang.alive_lang.alive.language import *
from asdl.lang.alive_lang.alive.value import *
from asdl.lang.alive_lang.alive.constants import *
from asdl.lang.alive_lang.alive.precondition import *
from asdl.lang.alive_lang.alive.alive import check_opt
from asdl.lang.alive_lang.alive_form_helpers import *

## todo names: for TypeFixedValue, because unsure about function, unsure about name construction
## todo still implement boolPred ops


def bool_pred_to_alive_form(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    # print(constructor_name)
    # print(ast_tree.__dict__)
    if constructor_name == "BinaryBoolPred":
        op = tree2llvmPredOp(ast_tree["op"].value)
        v1 = instrOperand_to_alive_form(ast_tree["v1"].value)
        v2 = instrOperand_to_alive_form(ast_tree["v2"].value)
        bool_pred = BinaryBoolPred(op=op, v1=v1, v2=v2)
    elif constructor_name == "LLVMBoolPred":
        op = tree2llvmPredOp(ast_tree["op"].value)
        args = [instrOperand_to_alive_form(v) for v in ast_tree["args"].value]
        bool_pred = LLVMBoolPred(op=op, args=args)
    elif constructor_name == "PredOr":
        args = [bool_pred_to_alive_form(p) for p in  ast_tree["args"].value]
        bool_pred = PredOr(args)
    elif constructor_name == "PredAnd":
        args = [bool_pred_to_alive_form(p) for p in ast_tree["args"].value]
        bool_pred = PredAnd(args=args)
    elif constructor_name == "PredNot":
        v = bool_pred_to_alive_form(ast_tree["args"].value)
        bool_pred = PredNot(v=v)
    elif constructor_name == "TruePred":
        bool_pred = TruePred()
    else:
        print("constructor name was {}, didn't match with any bool_pred constructors".format(constructor_name))
        raise ValueError
    return bool_pred


def type_to_alive_form(ast_tree: AbstractSyntaxTree):
    constructor_name = ast_tree.production.constructor.name
    # print(constructor_name)
    # print(ast_tree.__dict__)
    if constructor_name == "UnknownType":
        depth = ast_tree["depth"].value if ast_tree["depth"].value != None else 0
        t = UnknownType(d=depth)
    elif constructor_name == "NamedType":
        name = ast_tree["name"].value
        t = NamedType(name=name)
    elif constructor_name == "IntType":
        size = ast_tree["size"].value if ast_tree["size"].value != None else None
        t = UnknownType(d=size)
    elif constructor_name == "PtrType":
        underlyingType = type_to_alive_form(ast_tree["t"].value) if ast_tree["t"].value != None else None
        depth = ast_tree["d"].value if ast_tree["d"].value != None else 0
        t = PtrType(type=underlyingType, depth=depth)
    elif constructor_name == "ArrayType":
        ### if elems not none, then it is turned into TypeFixedValue
        ### TypeFixedValue receives v, which must be a value with .type IntType and is a subclass of Value
        elems = value_to_alive_form(ast_tree["e"].value) if ast_tree["e"].value != None else None
        underlyingType = type_to_alive_form(ast_tree["t"].value) if ast_tree["t"].value != None else None
        depth = ast_tree["d"].value if ast_tree["d"].value != None else 0
        t = ArrayType(elems=elems, type=underlyingType, depth=depth)
    else:
        print("constructor name was {}, didn't match with any type constructors".format(constructor_name))
        raise ValueError
    return t


def value_to_alive_form(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    # print(constructor_name)
    # print(ast_tree.__dict__)
    if constructor_name == "TypeFixedValue":
        id = ast_tree["name"].value
        v = value_to_alive_form(ast_tree["v"].value)
        min = int(ast_tree["min"].value)
        max = int(ast_tree["max"].value)
        outValue = TypeFixedValue(v=v, min=min, max=max)
        out = (id, outValue)
    elif constructor_name == "Input":
        id = ast_tree["name"].value
        t = type_to_alive_form(ast_tree["t"].value)
        outValue = Input(name=id, type=t)
        out = (id, outValue)
    else:
        print("constructor name was {}, didn't match with any value constructors".format(constructor_name))
        raise ValueError
    # add new guy to idents
    idents.add(id)
    prog_idents[id] = outValue
    return out


def constant_to_alive_form(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    # print(constructor_name)
    # print(ast_tree.__dict__)
    if constructor_name == "ConstantVal":
        val = int(ast_tree["val"].value)
        t = type_to_alive_form(ast_tree["t"].value)
        const = ConstantVal(val=val, type=t)
    elif constructor_name == "UndefVal":
        t = type_to_alive_form(ast_tree["t"].value)
        const = UndefVal(type=t)
    elif constructor_name == "CnstUnaryOp":
        op = tree2cnstAliveOp(asdl_name=ast_tree["op"].value,
                              constructor_name=constructor_name)
        v = ast_tree["v"].value
        const = CnstUnaryOp(op=op, v=v)
    elif constructor_name == "CnstBinaryOp":
        op = tree2cnstAliveOp(asdl_name=ast_tree["op"].value, constructor_name=constructor_name)
        v1 = ast_tree["c1"].value
        v2 = ast_tree["c2"].value
        const = CnstBinaryOp(op=op, v1=v1, v2=v2)
    elif constructor_name == "CnstFunction":
        op = tree2cnstAliveOp(asdl_name=ast_tree["op"].value, constructor_name=constructor_name)
        args = [value_to_alive_form(v) for v in ast_tree["args"].value]
        t = type_to_alive_form(ast_tree["t"].value)
        const = CnstFunction(op=op, args=args, type=t)
    else:
        print("constructor name was {}, didn't match with any constant constructors".format(constructor_name))
        raise ValueError
    # TODO: get the name of the constant!!
    name = const.getUniqueName()
    idents.add(name)
    prog_idents[name] = const
    return const


def instrOperand_to_alive_form(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    # print(constructor_name)
    # print(ast_tree.__dict__)
    # ast_tree = ast_tree.production.constructor
    # breakpoint()
    if constructor_name in assignInstrs:
        name, expr = instr_to_alive_form(ast_tree)
        instr_operands.add(name)
    elif constructor_name in const:
        expr = constant_to_alive_form(ast_tree)
    elif constructor_name in input:
        expr = value_to_alive_form(ast_tree)
    else:
        print("constructor name was {}, didn't match with any instr operand constructors".format(constructor_name))
        raise ValueError
    return expr


def instr_to_alive_form(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    # print(constructor_name)
    # print(ast_tree.__dict__)
    if constructor_name == "CopyOperand":
        name = ast_tree["reg"].value
        v = instrOperand_to_alive_form(ast_tree["v"].value)
        t = type_to_alive_form(ast_tree["t"].value)
        expr = CopyOperand(v=v, type=t)
        stmt = (name, expr)

    elif constructor_name == "BinOp":
        name = ast_tree["reg"].value
        op = tree2AliveOp(asdl_name=ast_tree["op"].value, constructor_name=constructor_name)
        t = type_to_alive_form(ast_tree["t"].value)
        v1 = instrOperand_to_alive_form(ast_tree["v1"].value)
        v2 = instrOperand_to_alive_form(ast_tree["v2"].value)
        # flag names are identical to strings used in the BinOp constructor
        flags = [v.production.constructor.name for v in ast_tree["flags"].value]
        expr = BinOp(op=op, type=t, v1=v1, v2=v2, flags=flags)
        stmt = (name, expr)

    elif constructor_name == "ConversionOp":
        name = ast_tree["reg"].value
        op = tree2AliveOp(asdl_name=ast_tree["op"].value, constructor_name=constructor_name)
        st = type_to_alive_form(ast_tree["st"].value)
        v = instrOperand_to_alive_form(ast_tree["v"].value)
        t = type_to_alive_form(ast_tree["t"].value)
        expr = ConversionOp(op=op, stype=st, v=v, type=t)
        stmt = (name, expr)

    elif constructor_name == "Icmp":
        name = ast_tree["reg"].value
        op = tree2AliveOp(asdl_name=ast_tree["op"].value, constructor_name=constructor_name)
        t = type_to_alive_form(ast_tree["t"].value)
        v1 = instrOperand_to_alive_form(ast_tree["v1"].value)
        v2 = instrOperand_to_alive_form(ast_tree["v2"].value)
        expr = Icmp(op=op, type=t, v1=v1, v2=v2)
        stmt = (name, expr)

    elif constructor_name == "Select":
        name = ast_tree["reg"].value
        t = type_to_alive_form(ast_tree["t"].value)
        # will be be icmp
        c = instr_to_alive_form(ast_tree["c"].value)
        v1 = instrOperand_to_alive_form(ast_tree["v1"].value)
        v2 = instrOperand_to_alive_form(ast_tree["v2"].value)
        expr = Select(type=t, c=c, v1=v1, v2=v2)
        stmt = (name, expr)

    # todo: you could make align optional and parse differently to make this easier
    elif constructor_name == "Alloca":
        name = ast_tree["reg"].value
        t = type_to_alive_form(ast_tree["t"].value)
        elemsType = type_to_alive_form(ast_tree["elemsType"].value)
        # num elems is passed onto TypeFixedValue inside Alloca, so it must be of type Value
        numElems = instrOperand_to_alive_form(ast_tree["numElems"].value)
        align = int(ast_tree["align"].value)
        expr = Alloca(type=t, elemsType=elemsType, numElems=numElems, align=align)
        stmt = (name, expr)

    # todo
    elif constructor_name == "GEP":
        # t = ast_tree["t"].value
        # pte = ast_tree["prt"].value
        raise NotImplementedError

    # todo: you could make align optional and parse differently to make this easier
    elif constructor_name == "Load":
        name = ast_tree["reg"].value
        st = type_to_alive_form(ast_tree["st"].value)
        v = instrOperand_to_alive_form(ast_tree["v"].value)
        align = int(ast_tree["align"].value)
        expr = Load(stype=st, v=v, align=align)
        stmt = (name, expr)

    # todo: you could make align optional and parse differently to make this easier
    elif constructor_name == "Store":
        st = type_to_alive_form(ast_tree["st"].value)
        src = instrOperand_to_alive_form(ast_tree["src"].value)
        t = type_to_alive_form(ast_tree["t"].value)
        dst = instrOperand_to_alive_form(ast_tree["dst"].value)
        align =int(ast_tree["align"].value)
        expr = Store(stype=st, src=src, type=t, dst=dst, align=align)
        name = expr.getUniqueName()
        stmt = (name, expr)

    # todo bb label
    elif constructor_name == "Br":
        raise NotImplementedError
        # id = "Br" + str(len(idents) + 1)
        # bb_label = ast_tree["bb_label"].value
        # cond = ast_tree["cond"].value
        # true = ast_tree["true"].value
        # false = ast_tree["false"].value
        # expr = Br(bb_label=bb_label, cond=cond, true=true, false=false)
        # stmt = (id, expr)

    elif constructor_name == "Ret":
        raise NotImplementedError
        # id = "Ret" + str(len(idents) + 1)
        # bb_label = ast_tree["bb_label"].value
        # t = ast_tree["t"].value
        # val = ast_tree["val"].value
        # expr = Ret(bb_label=bb_label, type=t, val=val)
        # stmt = (id, expr)

    elif constructor_name == "Skip":
        expr = Skip()
        name = expr.getUniqueName()
        stmt = (name, expr)

    elif constructor_name == "Unreachable":
        expr = Unreachable()
        name = expr.getUniqueName()
        stmt = (name, expr)

    else:
        print("constructor name was {}, didn't match with any instr constructors".format(constructor_name))
        raise ValueError

    # add to the global prog dict
    # sometimes we may recursively call on instr and we'd like to add it first
    prog[name] = expr
    prog_idents[name] = expr
    # add the id to idents
    idents.add(name)

    return stmt

def prog_to_alive_form(ast_tree):
    constructor_name = ast_tree.production.constructor.name
    assert constructor_name == "Prog"
    global prog
    global prog_idents
    global idents
    global operands
    prog = OrderedDict()
    prog_idents = OrderedDict()
    idents = set()
    instr_operands = set()
    for instr in ast_tree["instructions"].value:
        instr_to_alive_form(instr)
    used_instrs = set([v for v in instr_operands if v in prog.keys() and isinstance(prog[v], Instr)])
    return prog, prog_idents, used_instrs

def opt_to_alive_form(ast_tree, name = "optimization"):
    pre = TruePred() # bool_pred_to_alive_form(ast_tree.fields[0])
    src, src_idents, used_src = prog_to_alive_form(ast_tree.fields[1].value)
    tgt, tgt_idents, used_tgt = prog_to_alive_form(ast_tree.fields[2].value)
    # add all tgt idents that also appear in src
    used_tgt |= set([v for v in tgt_idents if v in src_idents])
    skip_tgt = set(src_idents.keys()).difference(used_tgt)
    # add this addtl wrapper due to use of BasicBlock in Alive
    src_final = OrderedDict(); tgt_final = OrderedDict()
    src_final[""] = src; tgt_final[""] = tgt
    #breakpoint()
    print_prog(src_final, set([]))
    print_prog(tgt_final, skip_tgt)
    return name, pre, src_final, tgt_final, src_idents, tgt_idents, used_src, list(used_tgt), list(skip_tgt)

def check_ast_tree_opt(ast_tree):
    alive_opt = opt_to_alive_form(ast_tree)
    return check_opt(alive_opt, hide_progress=False)

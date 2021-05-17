from asdl.lang.alive_lang.alive.language import Icmp, BinOp, ConversionOp
from asdl.lang.alive_lang.alive.constants import CnstUnaryOp, CnstBinaryOp, CnstFunction
from asdl.lang.alive_lang.alive.precondition import BinaryBoolPred, LLVMBoolPred

assignInstrs = set(["CopyOperand",
                "BinOp",
                "ConversionOp",
                "Select",
                "Alloca",
                "GEP",
                "Load"])

const = set(["ConstantVal",
             "UndefVal",
             "CnstUnaryOp",
             "CnstBinaryOp",
             "CnstFunction"])

input = set(["Input"])


binBoolPredTree2OpName = {
    'EQ': '==',
    'NE': '!=',
    'SLT': '<',
    'SLE': '<=',
    'SGT': '>',
    'SGE': '>=',
    'ULT': 'u<',
    'ULE': 'u<=',
    'UGT': 'u>',
    'UGE':'u>=',
}

llvmBoolPredTree2OpName = {
    'eqptrs': 'equivalentAddressValues',
    'isPower2': 'isPowerOf2',
    'isPower2OrZ': 'isPowerOf2OrZero',
    'isShiftedMask': 'isShiftedMask',
    'isSignBit': 'isSignBit',
    'maskZero': 'MaskedValueIsZero',
    'NSWAdd': 'WillNotOverflowSignedAdd',
    'NUWAdd': 'WillNotOverflowUnsignedAdd',
    'NSWSub': 'WillNotOverflowSignedSub',
    'NUWSub': 'WillNotOverflowUnsignedSub',
    'NSWMul': 'WillNotOverflowSignedMul',
    'NUWMul': 'WillNotOverflowUnsignedMul',
    'NUWShl': 'WillNotOverflowUnsignedShl',
    'OneUse': 'hasOneUse',
}



def tree2llvmPredOp(asdl_name: str, constructor_name: str):
    # print(asdl_name)
    # print(constructor_name)
    if constructor_name == "BinaryBoolPred":
        opName = binBoolPredTree2OpName[asdl_name]
        op = BinaryBoolPred.getOpId(opName)
    elif constructor_name == "LLBMBoolPred":
        opName = llvmBoolPredTree2OpName[asdl_name]
        op = LLVMBoolPred.getOpId(opName)
    else:
        print("constructor name is {} not found in tree2llvmPredOp constructors".format(constructor_name))
        raise ValueError
    return op


cnstUnaryTree2OpName = {
    'Not':  '~',
    'Neg': '-'
}


cnstBinaryTree2OpName = {
    'And': '&',
    'Or': '|',
    'Xor': '^',
    'Add': '+',
    'Sub': '-',
    'Mul': '*',
    'Div': '/',
    'DivU': '/u',
    'Rem': '%',
    'RemU': '%u',
    'AShr': '>>',
    'LShr': 'u>>',
    'Shl': '<<',
}

cnstFunctionTree2OpName = {
    'abs':   'abs',
    'sbits': 'ComputeNumSignBits',
    'obits': 'computeKnownOneBits',
    'zbits': 'computeKnownZeroBits',
    'ctlz':  'countLeadingZeros',
    'cttz':  'countTrailingZeros',
    'log2':  'log2',
    'lshr':  'lshr',
    'max':   'max',
    'sext':  'sext',
    'trunc': 'trunc',
    'umax':  'umax',
    'width': 'width',
    'zext':  'zext',
}


def tree2cnstAliveOp(asdl_name: str, constructor_name: str):
    # print(asdl_name)
    # print(constructor_name)
    if constructor_name == "CnstUnaryOp":
        opName = cnstUnaryTree2OpName[asdl_name.production.constructor.name]
        op = CnstUnaryOp.getOpId(opName)
    elif constructor_name == "CnstBinaryOp":
        opName = cnstBinaryTree2OpName[asdl_name.production.constructor.name]
        op = CnstBinaryOp.getOpId(opName)
    elif constructor_name == "CnstFunction":
        ## Icmp is different where we pass in the opName !
        opName = cnstFunctionTree2OpName[asdl_name.production.constructor.name]
        op = CnstFunction.getOpId(opName)
    else:
        print("constructor name is {} not found in tree2cnstAliveOp constructors".format(constructor_name))
        raise ValueError
    return op


icmpTree2OpName = {
    'EQ': 'eq',
    'NE': 'ne',
    'UGT': 'ugt',
    'UGE': 'uge',
    'ULT': 'ult',
    'ULE': 'ule',
    'SGT': 'sgt',
    'SGE': 'sge',
    'SLT': 'slt',
    'SLE': 'sle',
}


conversionOpTree2OpName = {
    'Trunc': 'trunc',
    'ZExt': 'zext',
    'SExt': 'sext',
    'ZExtOrTrunc': 'ZExtOrTrunc',
    'Ptr2Int': 'ptrtoint',
    'Int2Ptr': 'inttoptr',
    'Bitcast': 'bitcast',
  }


binOpTree2OpName = {
    'Add':  'add',
    'Sub':  'sub',
    'Mul':  'mul',
    'UDiv': 'udiv',
    'SDiv': 'sdiv',
    'URem': 'urem',
    'SRem': 'srem',
    'Shl':  'shl',
    'AShr': 'ashr',
    'LShr': 'lshr',
    'And':  'and',
    'Or':   'or',
    'Xor':  'xor',
  }

def tree2AliveOp(asdl_name: str, constructor_name: str):
    # print(asdl_name)
    # print(constructor_name)
    if constructor_name == "BinOp":
        opName = binOpTree2OpName[asdl_name.production.constructor.name]
        op = BinOp.getOpId(opName)
    elif constructor_name == "ConversionOp":
        opName = conversionOpTree2OpName[asdl_name.production.constructor.name]
        op = ConversionOp.getOpId(opName)
    elif constructor_name == "Icmp":
        ## Icmp is different where we pass in the opName !
        op = icmpTree2OpName[asdl_name.production.constructor.name]
    else:
        print("constructor name is {} not found in tree2AliveOp constructors".format(constructor_name))
        raise ValueError
    return op

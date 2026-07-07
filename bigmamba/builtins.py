KEYWORD_MAP = {
    'fn':     'def',
    'ret':    'return',
    'cls':    'class',
    'wl':     'while',
    'brk':    'break',
    'cnt':    'continue',
    'catch':  'except',
    'fin':    'finally',
    'throw':  'raise',
    'chk':    'assert',
    'gl':     'global',
    'yld':    'yield',
    'lm':     'lambda',
    'rm':     'del',
    'use':    'import',
    'T':      'True',
    'F':      'False',
    'N':      'None',
}

SYMBOL_KEYWORD_MAP = {
    '?':   'if',
    '??':  'elif',
    '!:':  'else:',
    '..':  'pass',
    '&&':  'and',
    '||':  'or',
    '~':   'not',
    'w/':  'with',
}

BUILTIN_FUNC_MAP = {
    'say':    'print',
    'ask':    'input',
    'l':      'len',
    'rng':    'range',
    'i':      'int',
    's':      'str',
    'fl':     'float',
    'ls':     'list',
    'dt':     'dict',
    'tp':     'tuple',
    'st':     'set',
    'bl':     'bool',
    'typ':    'type',
    'isa':    'isinstance',
    'enum':   'enumerate',
    'zp':     'zip',
    'mp':     'map',
    'flt':    'filter',
    'srt':    'sorted',
    'rev':    'reversed',
    'ab':     'abs',
    'mx':     'max',
    'mn':     'min',
    'sm':     'sum',
    'rnd':    'round',
    'opn':    'open',
    'nxt':    'next',
    'hsh':    'hash',
    'chr_':   'chr',
    'ord_':   'ord',
    'hex_':   'hex',
    'oct_':   'oct',
    'bin_':   'bin',
    'any_':   'any',
    'all_':   'all',
}

METHOD_MAP = {
    '.add(':      '.append(',
    '.addall(':   '.extend(',
    '.rm(':       '.remove(',
    '.up()':      '.upper()',
    '.lo()':      '.lower()',
    '.trim()':    '.strip()',
    '.spl(':      '.split(',
    '.jn(':       '.join(',
    '.rep(':      '.replace(',
    '.starts(':   '.startswith(',
    '.ends(':     '.endswith(',
    '.fmt(':      '.format(',
    '.ks()':      '.keys()',
    '.vs()':      '.values()',
    '.its()':     '.items()',
    '.idx(':      '.index(',
    '.cnt(':      '.count(',
    '.ins(':      '.insert(',
    '.clr()':     '.clear()',
    '.cp()':      '.copy()',
    '.upd(':      '.update(',
    '.get(':      '.get(',
    '.srt()':     '.sort()',
    '.rev()':     '.reverse()',
}

DECORATOR_MAP = {
    '@static':   '@staticmethod',
    '@clsm':     '@classmethod',
    '@prop':     '@property',
}

SPECIAL_OPERATORS = {
    '++':    'increment',
    '--':    'decrement',
    '<>':    'swap',
    '$"':    'fstring',
    '//':    'comment',
    '///':   'docstring',
    '->':    'import_from',
    '=>':    'import_as',
}

RESERVED_WORDS = set(KEYWORD_MAP.keys()) | {
    '?', '??', '!', '..', '&&', '||', '~', 'w/',
    'say', 'ask', 'quit', 'me', 'init',
    'T', 'F', 'N',
    'fn', 'ret', 'cls', 'wl', 'brk', 'cnt',
    'catch', 'fin', 'throw', 'chk', 'gl', 'yld', 'lm', 'rm',
    'use', 'try', 'in', 'is', 'as',
}

RUNTIME_PREAMBLE = '''
import sys as _sys

say = print
ask = input
l = len
rng = range
i = int
s = str
fl = float
ls = list
dt = dict
tp = tuple
st = set
bl = bool
typ = type
isa = isinstance
enum = enumerate
zp = zip
mp = map
flt = filter
srt = sorted
rev = reversed
ab = abs
mx = max
mn = min
sm = sum
rnd = round
opn = open
nxt = next
hsh = hash
chr_ = chr
ord_ = ord
hex_ = hex
oct_ = oct
bin_ = bin
any_ = any
all_ = all

T = True
F = False
N = None

def quit():
    _sys.exit(0)
'''

FILE_EXTENSION = '.mamba'

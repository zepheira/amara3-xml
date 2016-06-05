# amara3.uxml.uxpath.parserules
'''
XPath parsing rules.

Heavy debt to: https://github.com/emory-libraries/eulxml/blob/master/eulxml/xpath/parserules.py
'''

from . import ast
from .lexrules import tokens

precedence = (
    ('left', 'OR_OP'),
    ('left', 'AND_OP'),
    ('left', 'EQUAL_OP'),
    ('left', 'REL_OP'),
    ('left', 'PLUS_OP', 'MINUS_OP'),
    ('left', 'MULT_OP', 'DIV_OP', 'MOD_OP'),
    ('right', 'UMINUS_OP'),
    ('left', 'UNION_OP'),
)

#
# basic expressions
#

def p_expr_boolean(p):
    """
    Expr : Expr OR_OP Expr
         | Expr AND_OP Expr
         | Expr EQUAL_OP Expr
         | Expr REL_OP Expr
         | Expr PLUS_OP Expr
         | Expr MINUS_OP Expr
         | Expr MULT_OP Expr
         | Expr DIV_OP Expr
         | Expr MOD_OP Expr
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

def p_expr_unary(p):
    """
    Expr : MINUS_OP Expr %prec UMINUS_OP
    """
    p[0] = ast.UnaryExpression(p[1], p[2])

#
# path expressions
#

def p_path_union_expr(p):
    """
    Expr : Expr UNION_OP Expr
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

def p_path_expr_binary(p):
    """
    Expr : FilterExpr PATH_SEP RelativeLocationPath
         | FilterExpr ABBREV_PATH_SEP RelativeLocationPath
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

def p_path_expr_unary(p):
    """
    Expr : RelativeLocationPath
         | AbsoluteLocationPath
         | AbbreviatedAbsoluteLocationPath
         | FilterExpr
         | FunctionCall
    """
    p[0] = p[1]

#
# paths
#

def p_absolute_location_path_rootonly(p):
    """
    AbsoluteLocationPath : PATH_SEP
    """
    p[0] = ast.AbsolutePath(p[1])

def p_absolute_location_path_subpath(p):
    """
    AbsoluteLocationPath : PATH_SEP RelativeLocationPath
    """
    p[0] = ast.AbsolutePath(p[1], p[2])

def p_abbreviated_absolute_location_path(p):
    """
    AbbreviatedAbsoluteLocationPath : ABBREV_PATH_SEP RelativeLocationPath
    """
    p[0] = ast.AbsolutePath(p[1], p[2])

def p_relative_location_path_simple(p):
    """
    RelativeLocationPath : Step
    """
    p[0] = p[1]

def p_relative_location_path_binary(p):
    """
    RelativeLocationPath : RelativeLocationPath PATH_SEP Step
                         | RelativeLocationPath ABBREV_PATH_SEP Step
    """
    p[0] = ast.BinaryExpression(p[1], p[2], p[3])

#
# path steps
#

def p_step_axis_nodetest(p):
    """
    Step : AxisSpecifier NodeTest
    """
    p[0] = ast.Step(p[1], p[2], [])

def p_step_axis_nodetest_predicates(p):
    """
    Step : AxisSpecifier NodeTest PredicateList
    """
    p[0] = ast.Step(p[1], p[2], p[3])

def p_step_nodetest(p):
    """
    Step : NodeTest
    """
    #For MicroXML we can assume child axis
    p[0] = ast.Step('child', p[1], [])

def p_step_nodetest_predicates(p):
    """
    Step : NodeTest PredicateList
    """
    p[0] = ast.Step(None, p[1], p[2])

def p_step_abbrev(p):
    """
    Step : ABBREV_STEP_SELF
         | ABBREV_STEP_PARENT
    """
    p[0] = ast.AbbreviatedStep(p[1])

#
# axis specifier
#

def p_axis_specifier_full(p):
    """
    AxisSpecifier : NAME AXIS_SEP
    """
    #XPath 1.0 axes - namespace
    if p[1] not in ('self', 'attribute', 'ancestor', 'ancestor-or-self', 'attribute', 'child', 'descendant', 'descendant-or-self', 'following', 'following-sibling', 'parent', 'preceding', 'preceding-sibling'):
        raise RuntimeError("Invalid axis name '{0}'".format(p[1]))
    p[0] = p[1]

def p_axis_specifier_abbrev(p):
    """
    AxisSpecifier : ABBREV_AXIS_AT
    """
    p[0] = 'attribute'

#
# node test
#

def p_node_test_name_test(p):
    """
    NodeTest : NameTest
    """
    p[0] = p[1]

def p_node_test_type(p):
    """
    NodeTest : NAME OPEN_PAREN CLOSE_PAREN
    """
    if p[1] not in ('node', 'text'):
        raise RuntimeError("Invalid node type '{0}'".format(p[1]))
    p[0] = ast.NodeType(p[1])

#
# name test
#

def p_name_test_star(p):
    """
    NameTest : STAR_OP
    """
    p[0] = ast.NameTest('*')

def p_name_test_name(p):
    """
    NameTest : NAME
    """
    p[0] = ast.NameTest(p[1])

#
# filter expressions
#

def p_filter_expr_simple(p):
    """
    FilterExpr : VariableReference
               | LITERAL
               | Number
    """
    # FIXME: | FunctionCall moved so as not to conflict with NodeTest :
    # FunctionCall
    p[0] = p[1]

def p_filter_expr_grouped(p):
    """
    FilterExpr : OPEN_PAREN Expr CLOSE_PAREN
    """
    p[0] = p[2]

def p_filter_expr_predicate(p):
    """
    FilterExpr : FilterExpr Predicate
    """
    if not hasattr(p[1], 'append_predicate'):
        p[1] = ast.PredicatedExpression(p[1])
    p[1].append_predicate(p[2])
    p[0] = p[1]

#
# predicates
#

def p_predicate_list_single(p):
    """
    PredicateList : Predicate
    """
    p[0] = [p[1]]

def p_predicate_list_recursive(p):
    """
    PredicateList : PredicateList Predicate
    """
    p[0] = p[1]
    p[0].append(p[2])

def p_predicate(p):
    """
    Predicate : OPEN_BRACKET Expr CLOSE_BRACKET
    """
    p[0] = p[2]

#
# variable
#

def p_variable_reference(p):
    """
    VariableReference : DOLLAR NAME
    """
    p[0] = ast.VariableReference(p[2])

#
# number
#

def p_number(p):
    """
    Number : FLOAT
           | INTEGER
    """
    p[0] = p[1]

#
# funcall
#

def p_function_call(p):
    """
    FunctionCall : NAME FormalArguments
    """
    #Hacking around the ambiguity between node type test & function call
    if p[1] in ('node', 'text'):
        p[0] = ast.NodeType(p[1])
    else:
        p[0] = ast.FunctionCall(p[1], p[2])

def p_formal_arguments_empty(p):
    """
    FormalArguments : OPEN_PAREN CLOSE_PAREN
    """
    p[0] = []

def p_formal_arguments_list(p):
    """
    FormalArguments : OPEN_PAREN ArgumentList CLOSE_PAREN
    """
    p[0] = p[2]

def p_argument_list_single(p):
    """
    ArgumentList : Expr
    """
    p[0] = [p[1]]

def p_argument_list_recursive(p):
    """
    ArgumentList : ArgumentList COMMA Expr
    """
    p[0] = p[1]
    p[0].append(p[3])

#
# error handling
#

def p_error(p):
    # In some cases, p could actually be None.
    # However, stack trace should have enough information to identify the problem.
    raise RuntimeError("Syntax error at '{0}'".format(p))


#import ply.yacc as yacc
# Build the parser
#parser = yacc.yacc()
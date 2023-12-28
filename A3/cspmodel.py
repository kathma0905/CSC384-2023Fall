
############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 3 Starter Code
## v1.1
## Changes:
##   v1.1: updated the comments in kropki_model. 
##         the second return value should be a 2d list of variables.
############################################################

from board import *
from cspbase import *

def kropki_model(board):
    """
    Create a CSP for a Kropki Sudoku Puzzle given a board of dimension.

    If a variable has an initial value, its domain should only contain the initial value.
    Otherwise, the variable's domain should contain all possible values (1 to dimension).

    We will encode all the constraints as binary constraints.
    Each constraint is represented by a list of tuples, representing the values that
    satisfy this constraint. (This is the table representation taught in lecture.)

    Remember that a Kropki sudoku has the following constraints.
    - Row constraint: every two cells in a row must have different values.
    - Column constraint: every two cells in a column must have different values.
    - Cage constraint: every two cells in a 2x3 cage (for 6x6 puzzle) 
            or 3x3 cage (for 9x9 puzzle) must have different values.
    - Black dot constraints: one value is twice the other value.
    - White dot constraints: the two values are consecutive (differ by 1).

    Make sure that you return a 2D list of variables separately. 
    Once the CSP is solved, we will use this list of variables to populate the solved board.
    Take a look at csprun.py for the expected format of this 2D list.

    :returns: A CSP object and a list of variables.
    :rtype: CSP, List[List[Variable]]

    """
    var = create_variables(board.dimension)
    csp = CSP('csp')
 
    # Satisfy constraints
    sat_rc = satisfying_tuples_difference_constraints(board.dimension)
    sat_bd = satisfying_tuples_black_dots(board.dimension)
    sat_wd = satisfying_tuples_white_dots(board.dimension)
 
    # Build empty assignment
    empty = []
    var_idx = 0
    for row in board.cells:
        empty_row = []
        for col in row:
            if col != 0: # Has initial value
                variable = var[var_idx]
                variable.assign(col)
                variable.dom = [col]
                empty_row.append(variable)
                csp.add_var(variable)
            else:
                empty_row.append(var[var_idx])
                csp.add_var(var[var_idx])
            var_idx += 1
        empty.append(empty_row)

 
    # Adding initial constraints
    cons_rc = create_row_and_col_constraints(board.dimension, sat_rc, var)
    cons_cage = create_cage_constraints(board.dimension, sat_rc, var)
    cons_dots = create_dot_constraints(board.dimension, board.dots, sat_wd, sat_bd, var)

    all_cons = cons_rc + cons_cage
    
    for c in all_cons:
        checked = []
        if c.get_scope() not in checked:
            csp.add_constraint(c)
            checked.append(c.get_scope())
 
    for dot in cons_dots:
        csp.add_constraint(dot)
    
    return csp, empty

    # raise NotImplementedError
    
def create_initial_domain(dim):
    """
    Return a list of values for the initial domain of any unassigned variable.
    [1, 2, ..., dimension]

    :param dim: board dimension
    :type dim: int

    :returns: A list of values for the initial domain of any unassigned variable.
    :rtype: List[int]
    """

    domain = [i+1 for i in range(dim)]
    return domain

    # raise NotImplementedError



def create_variables(dim):
    """
    Return a list of variables for the board.

    We recommend that your name each variable Var(row, col).

    :param dim: Size of the board
    :type dim: int

    :returns: A list of variables, one for each cell on the board
    :rtype: List[Variables]
    """
    result = []
    for row in range(dim):
        for col in range(dim):
            name = "Var({0}, {1})".format(row+1, col+1)
            var = Variable(name, domain=create_initial_domain(dim))
            result.append(var)
    return result
    # raise NotImplementedError

    
def satisfying_tuples_difference_constraints(dim):
    """
    Return a list of satifying tuples for binary difference constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satifying tuples
    :rtype: List[(int,int)]
    """
    result = []
    for var1 in range(1, dim+1):
        for var2 in range(1, dim+1):
            if var1 != var2:
                result.append((var1, var2))
    return result
    # raise NotImplementedError
  
  
def satisfying_tuples_white_dots(dim):
    """
    Return a list of satifying tuples for white dot constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satifying tuples
    :rtype: List[(int,int)]
    """
    result = []
    for var1 in range(1, dim+1):
        for var2 in range(1, dim+1):
            if var1 == var2 + 1 or var1 == var2 - 1:
                result.append((var1, var2))
    return result

    # raise NotImplementedError
  
def satisfying_tuples_black_dots(dim):
    """
    Return a list of satifying tuples for black dot constraints.

    :param dim: Size of the board
    :type dim: int

    :returns: A list of satifying tuples
    :rtype: List[(int,int)]
    """
    result = []
    for var1 in range(1, dim+1):
        for var2 in range(1, dim+1):
            if var1 == var2 * 2 or var2 == var1 * 2:
                result.append((var1, var2))
    return result
    # raise NotImplementedError
    
def create_row_and_col_constraints(dim, sat_tuples, variables):
    """
    Create and return a list of binary all-different row/column constraints.

    :param dim: Size of the board
    :type dim: int

    :param sat_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple are different.
    :type sat_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary all-different constraints
    :rtype: List[Constraint]
    """
    result = []
    checked = []

    # Use Variable.get_assigned_value()
    # Each row must contain different numbers from 1 to dim. ->
    # All variables in the same row has different values
    for row in range(1, dim+1):
        for var1 in variables:
            row1, _ = get_location(var1)
            if row1 == row:
                for var2 in variables:
                    row2, _ = get_location(var2)
                    if var1 != var2 and row1 == row2 and (var2, var1) not in checked: # They are in the same row, but not the same var
                        result.extend(build_constraints(sat_tuples, var1, var2, 'row'))
                        checked.append((var1, var2))
    # Each column must contain different numbers from 1 to dim. 
    for col in range(1, dim+1):
        for var3 in variables:
            _, col1 = get_location(var3)
            if col1 == col:
                for var4 in variables:
                    _, col2 = get_location(var4)
                    if var3 != var4 and col1 == col2 and (var4, var3) not in checked: # They are in the same col
                        result.extend(build_constraints(sat_tuples, var3, var4, 'col'))
                        checked.append((var3, var4))
    
    return result
    
    # raise NotImplementedError
    
    
def create_cage_constraints(dim, sat_tuples, variables):
    """
    Create and return a list of binary all-different constraints for all cages.

    :param dim: Size of the board
    :type dim: int

    :param sat_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple are different.
    :type sat_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary all-different constraints
    :rtype: List[Constraint]
    """
    # Each sub-grid must contain different numbers from 1 to N.
    result = []
    checked = []
    for cage in range(1, dim+1):
        locations = get_cage_locations(dim, cage)
        for var1 in variables:
            for var2 in variables:
                if in_same_cage(locations, var1, var2) and var1 != var2 and (var2, var1) not in checked:
                    result.extend(build_constraints(sat_tuples, var1, var2, 'cage'))
                    checked.append((var1, var2))
    return result

    # raise NotImplementedError
    
def create_dot_constraints(dim, dots, white_tuples, black_tuples, variables):
    """
    Create and return a list of binary constraints, one for each dot.

    :param dim: Size of the board
    :type dim: int
    
    :param dots: A list of dots, each dot is a Dot object.
    :type dots: List[Dot]

    :param white_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple satisfy the white dot constraint.
    :type white_tuples: List[(int, int)]
    
    :param black_tuples: A list of domain value pairs (value1, value2) such that 
        the two values in each tuple satisfy the black dot constraint.
    :type black_tuples: List[(int, int)]

    :param variables: A list of all the variables in the CSP
    :type variables: List[Variable]
        
    :returns: A list of binary dot constraints
    :rtype: List[Constraint]
    """
    result = []
    checked = []
    for dot in dots:
        color = dot.color
        pair = [(dot.cell_row+1, dot.cell_col+1), (dot.cell2_row+1, dot.cell2_col+1)]
        for var1 in variables:
            for var2 in variables:
                if (var2, var1) not in checked:
                    locations = [get_location(var1), get_location(var2)]
                    if locations == pair: # This is the correlated pair
                        if color == CHAR_WHITE:
                            result.extend(build_constraints(white_tuples, var1, var2, "white"))
                        else:
                            result.extend(build_constraints(black_tuples, var1, var2, "black"))
                    checked.append((var1, var2))
    return result
    # raise NotImplementedError


############### Helper Function ###################
def get_location(var: Variable):
    """
    Return the location of var.

    :param var: A variable of CSP
    :type var: Variable

    :returns: A tuple of the location of var on board
    :rtype: (int, int)
    
    """
    name = var.name
    row_col = name[4 : 8]
    row, col = row_col.split(', ')
    return int(row), int(col)

def get_cage_locations(dim, cagenum):
    """
    Return the locations of the cagenum-th cage.

    :param cagenum: The i-th cage.
    :type cagenum: int

    :returns: A list of locations in that cage.
    :stypes: List[(int, int)]
    """
    
    if dim == 6:
        if cagenum == 1:
            result = []
            for row in range(1, 4):
                for col in range(1, 3):
                    result.append((row, col))
            return result
        elif cagenum == 2:
            result = []
            for row in range(1, 4):
                for col in range(3, 5):
                    result.append((row, col))
            return result
        elif cagenum == 3:
            result = []
            for row in range(1, 4):
                for col in range(5, 7):
                    result.append((row, col))
            return result
        elif cagenum == 4:
            result = []
            for row in range(4, 7):
                for col in range(1, 3):
                    result.append((row, col))
            return result
        elif cagenum == 5:
            result = []
            for row in range(4, 7):
                for col in range(3, 5):
                    result.append((row, col))
            return result
        else:
            result = []
            for row in range(4, 7):
                for col in range(5, 7):
                    result.append((row, col))
            return result
    else:
        if cagenum == 1:
            result = []
            for row in range(1, 4):
                for col in range(1, 4):
                    result.append((row, col))
            return result
        elif cagenum == 2:
            result = []
            for row in range(1, 4):
                for col in range(4, 7):
                    result.append((row, col))
            return result
        elif cagenum == 3:
            result = []
            for row in range(1, 4):
                for col in range(7, 10):
                    result.append((row, col))
            return result
        elif cagenum == 4:
            result = []
            for row in range(4, 7):
                for col in range(1, 4):
                    result.append((row, col))
            return result
        elif cagenum == 5:
            result = []
            for row in range(4, 7):
                for col in range(4, 7):
                    result.append((row, col))
            return result
        elif cagenum == 6:
            result = []
            for row in range(4, 7):
                for col in range(7, 10):
                    result.append((row, col))
            return result
        elif cagenum == 7:
            result = []
            for row in range(7, 10):
                for col in range(1, 4):
                    result.append((row, col))
            return result
        elif cagenum == 8:
            result = []
            for row in range(7, 10):
                for col in range(4, 7):
                    result.append((row, col))
            return result
        elif cagenum == 9:
            result = []
            for row in range(7, 10):
                for col in range(7, 10):
                    result.append((row, col))
            return result
        
def build_constraints(sat_tuples, var1, var2, name):
    val1 = var1.domain()
    # print("var1", var1.name, "var2", var2.name)
    val2 = var2.domain()
    cons = Constraint(name+"("+var1.name + ", "+var2.name+")", [var1, var2])
    result = []
    for value1 in val1:
        for value2 in val2:
            tup = (value1, value2)
            if tup in sat_tuples:
                result.append(tup)
    cons.add_satisfying_tuples(result)
    # print(cons.sat_tuples)
    return [cons]
    

def in_same_cage(cage_locations, var1, var2):
    loc1 = get_location(var1)
    loc2 = get_location(var2)
    return loc1 in cage_locations and loc2 in cage_locations

def is_adjacent(var1, var2):
    row1, col1 = get_location(var1)
    row2, col2 = get_location(var2)
    if row1 == row2:
        return abs(col1 - col2) == 1
    elif col1 == col2:
        return abs(row1 - row2) == 1
    else:
        return False
    
def get_dot_pairs(dots, location = True):
    result = {}
    for dot in dots:
        if dot.location == location: # dot is to the right of the cell in [cell_row, cell_col].
            color = dot.color
            if color not in result:
                result[color] = []
            result[color].append([(dot.cell_row, dot.cell_col), (dot.cell2_row, dot.cell2_col)])
    return result

# if __name__ == "__main__":
#     import random
#     result = create_variables(6)
#     for var in result:
#         var.add_domain_values(create_initial_domain(6))  
#     # result[0].assign(3) 
#     # # print(result[0].cur_domain()) 
#     # result[1].assign(2)
#     # # print(result[1].cur_domain())
#     # for var in result[2:]:
#     #     var.assign(3)
#     result[10].assign(3)
#     result[11].assign(4)
#     result[17].assign(2)
#     sat_tuples = satisfying_tuples_difference_constraints(6)
    
#     # actual_row_col = create_row_and_col_constraints(6, sat_tuples, result)
#     # for constraint in actual_row_col:
#     #     print(constraint)

#     actural_cage = create_cage_constraints(6, sat_tuples, result)
#     # for c in actural_cage:
#     #     # print(c)

#     # print(is_adjacent(result[0], result[6]))

#     dot1 = Dot(CHAR_WHITE, 2, 5, True)
#     dot2 = Dot(CHAR_BLACK, 2, 6, False)
#     dot3 = Dot(CHAR_WHITE, 1, 4, False)
#     dot4 = Dot(CHAR_WHITE, 2, 4, False)

#     dots = get_dot_pairs([dot1, dot2, dot3, dot4], False)

#     white = satisfying_tuples_white_dots(6)
#     black = satisfying_tuples_black_dots(6)
#     print(white)

#     actual_dots = create_dot_constraints(6, [dot3], white, black, result)
#     for cons in actual_dots:
#         print(cons)
#         print(cons.sat_tuples)
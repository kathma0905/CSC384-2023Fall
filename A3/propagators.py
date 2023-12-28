############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 3 Starter Code
## v1.0
##
############################################################


def prop_FC(csp, last_assigned_var=None):
    """
    This is a propagator to perform forward checking. 

    First, collect all the relevant constraints.
    If the last assigned variable is None, then no variable has been assigned 
    and we are performing propagation before search starts.
    In this case, we will check all the constraints.
    Otherwise, we will only check constraints involving the last assigned variable.

    Among all the relevant constraints, focus on the constraints with one unassigned variable. 
    Consider every value in the unassigned variable's domain, if the value violates 
    any constraint, prune the value. 

    :param csp: The CSP problem
    :type csp: CSP
        
    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: The boolean indicates whether forward checking is successful.
        The boolean is False if at least one domain becomes empty after forward checking.
        The boolean is True otherwise.
        Also returns a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]
    """
    # Collect all relevant constraints
    const = csp.get_all_cons()
    if last_assigned_var:
        const = csp.get_cons_with_var(last_assigned_var)

    # Filter the constraints to have the ones with only one unassigned variable
    pruned_values = []
    one_unasgns = has_exactly_one_unasgn(const)

    for c in one_unasgns:
        x = c.get_unassigned_vars()[0]

        if x.cur_domain_size() != 0:
            # Consider every value in the domain
            for value in x.cur_domain():
                # If violate the constraint
                if not is_satisfied(c, x, value):
                    x.prune_value(value)
                    pruned_values.append((x, value))

                    if x.cur_domain_size() == 0: # After pruning, X becomes empty
                        return False, pruned_values
        else:
            return False, pruned_values
    return True, pruned_values

def prop_AC3(csp, last_assigned_var=None):
    """
    This is a propagator to perform the AC-3 algorithm.

    Keep track of all the constraints in a queue (list). 
    If the last_assigned_var is not None, then we only need to 
    consider constraints that involve the last assigned variable.

    For each constraint, consider every variable in the constraint and 
    every value in the variable's domain.
    For each variable and value pair, prune it if it is not part of 
    a satisfying assignment for the constraint. 
    Finally, if we have pruned any value for a variable,
    add other constraints involving the variable back into the queue.

    :param csp: The CSP problem
    :type csp: CSP
        
    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: a boolean indicating if the current assignment satisifes 
        all the constraints and a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]
    """
    queue = csp.get_all_cons()
    if last_assigned_var:
        queue = csp.get_cons_with_var(last_assigned_var)

    pruned_values = []
    while queue:
        cons = queue.pop(0)
        curr_vars = cons.get_scope()
        vars = cons.get_unassigned_vars()

        for var in vars:
            if revise(cons, var, pruned_values):
                if var.cur_domain_size() == 0:
                    return False, pruned_values
                for neighbor_cons in csp.get_cons_with_var(var):
                    neighbor_pair = neighbor_cons.get_scope()
                    if neighbor_pair != curr_vars and neighbor_pair[1] == var and neighbor_cons not in queue:
                        queue.append(neighbor_cons)
    return True, pruned_values
    
    # raise NotImplementedError

def ord_mrv(csp):
    """
    Implement the Minimum Remaining Values (MRV) heuristic.
    Choose the next variable to assign based on MRV.

    If there is a tie, we will choose the first variable. 

    :param csp: A CSP problem
    :type csp: CSP

    :returns: the next variable to assign based on MRV

    """
    unasgn_var = csp.get_all_unasgn_vars()

    if not unasgn_var:
        return None
    mrv = min(unasgn_var, key=lambda var: var.cur_domain_size())

    return mrv

    # raise NotImplementedError



###############################################################################
# Helper Function
###############################################################################
def has_exactly_one_unasgn(constraints):
    result = []
    for const in constraints:
        if const.get_num_unassigned_vars() == 1:
            result.append(const)
    return result

def is_satisfied(constraint, var, value):
    sups = constraint.sup_tuples
    
    if (var, value) not in sups:
        return False
    
    sats = sups[(var, value)]
    scope = constraint.get_scope()

    for i, curr_var in enumerate(scope):
        satisfy = any(any(sat_tup[i] == val for sat_tup in sats) for val in curr_var.cur_domain())
        if not satisfy:
            return False

    return True


    

    
    
def revise(constraint, var, pruned_values):
    revised = False
    for value in var.cur_domain():
        if not is_satisfied(constraint, var, value):
            var.prune_value(value)
            revised = True
            pruned_values.append((var, value))
    return revised


###############################################################################
# Do not modify the prop_BT function below
###############################################################################


def prop_BT(csp, last_assigned_var=None):
    """
    This is a basic propagator for plain backtracking search.

    Check if the current assignment satisfies all the constraints.
    Note that we only need to check all the fully instantiated constraints 
    that contain the last assigned variable.
    
    :param csp: The CSP problem
    :type csp: CSP

    :param last_assigned_var: The last variable assigned before propagation.
        None if no variable has been assigned yet (that is, we are performing 
        propagation before search starts).
    :type last_assigned_var: Variable

    :returns: a boolean indicating if the current assignment satisifes all the constraints 
        and a list of variable and value pairs pruned. 
    :rtype: boolean, List[(Variable, Value)]

    """
    
    # If we haven't assigned any variable yet, return true.
    if not last_assigned_var:
        return True, []
        
    # Check all the constraints that contain the last assigned variable.
    for c in csp.get_cons_with_var(last_assigned_var):

        # All the variables in the constraint have been assigned.
        if c.get_num_unassigned_vars() == 0:

            # get the variables
            vars = c.get_scope() 

            # get the list of values
            vals = []
            for var in vars: #
                vals.append(var.get_assigned_value())

            # check if the constraint is satisfied
            if not c.check(vals): 
                return False, []

    return True, []

############################################################
## CSC 384, Intro to AI, University of Toronto.
## Assignment 4 Starter Code
## v1.2
## - removed the example in ve since it is misleading.
## - updated the docstring in min_fill_ordering. The tie-breaking rule should
##   choose the variable that comes first in the provided list of factors.
############################################################

from bnetbase import Variable, Factor, BN
import csv


def normalize(factor):
    '''
    Normalize the factor such that its values sum to 1.
    Do not modify the input factor.

    :param factor: a Factor object. 
    :return: a new Factor object resulting from normalizing factor.
    '''

    ### YOUR CODE HERE ###
    variables = factor.get_scope()
    result = Factor('normalized', variables)
    values = factor.values[:]
    # print(values)
    total = sum(values)
    combinations = []
    for var in variables:
        elements = var.domain()
        combinations = generate_combinations(elements, combinations)
    for comb in combinations:
        prob = factor.get_value(comb)
        norm_prob = prob / total
        comb.append(norm_prob)
    result.add_values(combinations)
    return result


############################################################
# Helper Function
############################################################
def generate_combinations(elements, combinations):
    result = []
    i = 0
    while i < len(elements):
        if combinations == []:
            result.append([elements[i]])
        else:
            for comb in combinations:
                copy = comb[:]
                copy.append(elements[i])
                result.append(copy)
        i += 1
    return result

    
    

def restrict(factor:Factor, variable:Variable, value):
    '''
    Restrict a factor by assigning value to variable.
    Do not modify the input factor.

    :param factor: a Factor object.
    :param variable: the variable to restrict.
    :param value: the value to restrict the variable to
    :return: a new Factor object resulting from restricting variable to value.
             This new factor no longer has variable in it.
    ''' 

    ### YOUR CODE HERE ###
    variables = factor.get_scope()[:]
    combinations = []
    for var in variables:
        if var == variable:
            elements = [value]
        else:
            elements = var.domain()
        combinations = generate_combinations(elements, combinations)
    for i in range(len(combinations)):
        var_lst = combinations[i]
        val = factor.get_value(var_lst)
        var_lst.remove(value)
        var_lst.append(val)
        combinations[i] = var_lst
    variables.remove(variable)
    result = Factor('restricted', variables)
    result.add_values(combinations)
    return result



def sum_out(factor:Factor, variable:Variable):
    '''
    Sum out a variable variable from factor factor.
    Do not modify the input factor.

    :param factor: a Factor object.
    :param variable: the variable to sum out.
    :return: a new Factor object resulting from summing out variable from the factor.
             This new factor no longer has variable in it.
    '''       

    ### YOUR CODE HERE ###
    variables = factor.get_scope()[:]
    sorted_dict = {}
    combinations = []
    for var in variables:
        elements = var.domain()
        combinations = generate_combinations(elements, combinations)
    for comb in combinations:
        prob = factor.get_value(comb)
        var_to_remove = variables.index(variable)
        comb.pop(var_to_remove)
        key = tuple(comb)
        if key not in sorted_dict:
            sorted_dict[key] = 0
        sorted_dict[key] += prob
    rest = []
    for rest_var in sorted_dict:
        lst = list(rest_var)
        lst.append(sorted_dict[rest_var])
        rest.append(lst)
    variables.remove(variable)
    result = Factor("summed-out", variables)
    result.add_values(rest)
    return result


def multiply(factor_list:list[Factor]):
    '''
    Multiply a list of factors together.
    Do not modify any of the input factors. 

    :param factor_list: a list of Factor objects.
    :return: a new Factor object resulting from multiplying all the factors in factor_list.
    ''' 
    ### YOUR CODE HERE ###
    comb = []
    variables = []
    for factor in factor_list:
        add_unique_variable(factor, variables)
        curr_comb = build_combination(factor)

        if comb == []:
            for c in curr_comb:
                comb.append([c, factor.get_value(c)])
        else:
            new_comb = []
            for c in comb:
                for c_comb in curr_comb:
                    copy = c[:]
                    var_lst = copy[0][:]
                    var_lst.extend(c_comb)
                    copy[0] = var_lst
                    copy[1] = copy[1] * factor.get_value(c_comb)
                    new_comb.append(copy)
            comb = new_comb

    no_common = []
    for i in range(len(comb)):
        pair = comb[i]
        pair[0] = remove_duplicates(pair[0])
        if len(pair[0]) > len(variables):
            no_common.append(pair)
        else:
            pair[0].append(pair[1])
            comb[i] = pair[0]
    
    for no in no_common:
        comb.remove(no)

    result = Factor('multiply', variables)
    
    result.add_values(comb)
    return result


def add_unique_variable(factor, variables):
    for variable in factor.get_scope():
        if variable not in variables:
            variables.append(variable)

def remove_duplicates(input_list):
    unique_list = []
    for item in input_list:
        if item not in unique_list:
            unique_list.append(item)
    return unique_list
        
        
def build_combination(factor):
    variables = factor.get_scope()
    combinations = []
    for var in variables:
        elements = var.domain()
        combinations = generate_combinations(elements, combinations)
    return combinations


def min_fill_ordering(factor_list, variable_query):
    '''
    This function implements The Min Fill Heuristic. We will use this heuristic to determine the order 
    to eliminate the hidden variables. The Min Fill Heuristic says to eliminate next the variable that 
    creates the factor of the smallest size. If there is a tie, choose the variable that comes first 
    in the provided order of factors in factor_list.

    The returned list is determined iteratively.
    First, determine the size of the resulting factor when eliminating each variable from the factor_list.
    The size of the resulting factor is the number of variables in the factor.
    Then the first variable in the returned list should be the variable that results in the factor 
    of the smallest size. If there is a tie, choose the variable that comes first in the provided order of 
    factors in factor_list. 
    Then repeat the process above to determine the second, third, ... variable in the returned list.

    Here is an example.
    Consider our complete Holmes network. Suppose that we are given a list of factors for the variables 
    in this order: P(E), P(B), P(A|B, E), P(G|A), and P(W|A). Assume that our query variable is Earthquake. 
    Among the other variables, which one should we eliminate first based on the Min Fill Heuristic?

    - Eliminating B creates a factor of 2 variables (A and E).
    - Eliminating A creates a factor of 4 variables (E, B, G and W).
    - Eliminating G creates a factor of 1 variable (A).
    - Eliminating W creates a factor of 1 variable (A).

    In this case, G and W tie for the best variable to be eliminated first since eliminating each variable 
    creates a factor of 1 variable only. Based on our tie-breaking rule, we should choose G since it comes 
    before W in the list of factors provided.
    '''

    ### YOUR CODE HERE ###
    var_dict = {}
    for factor in factor_list:
        variables = factor.get_scope()
        for var in variables:
            if var not in var_dict:
                var_dict[var] = variables
            else:
                add_unique_variable(factor, var_dict[var])
    var_dict.pop(variable_query)
    count_dict = {}
    for key in var_dict:
        create_var = len(var_dict[key]) - 1
        if create_var not in count_dict:
            count_dict[create_var] = [key]
        else:
            count_dict[create_var].append(key)
    count_dict = dict(sorted(count_dict.items()))
    result = []
    for num in count_dict:
        result.extend(count_dict[num])
    return result


def ve(bayes_net:BN, var_query:Variable, varlist_evidence:list[Variable]): 
    '''
    Execute the variable elimination algorithm on the Bayesian network bayes_net
    to compute a distribution over the values of var_query given the 
    evidence provided by varlist_evidence. 

    :param bayes_net: a BN object.
    :param var_query: the query variable. we want to compute a distribution
                     over the values of the query variable.
    :param varlist_evidence: the evidence variables. Each evidence variable has 
                         its evidence set to a value from its domain 
                         using set_evidence.
    :return: a Factor object representing a distribution over the values
             of var_query. that is a list of numbers, one for every value
             in var_query's domain. These numbers sum to 1. The i-th number
             is the probability that var_query is equal to its i-th value given 
             the settings of the evidence variables.

    '''
    ### YOUR CODE HERE ###
    # 1. Categorize the variables: query, evidence, and hidden.
    # Since we already have query and evidence variabels, we only need to filter out the hidden variables
    hidden = bayes_net.variables()[:]
    hidden.remove(var_query)
    for evidence in varlist_evidence:
        hidden.remove(evidence)
    
    # 2. Create a factor for each node in the Bayesian network.
    factors = bayes_net.factors()[:]

    # 3. Restrict each evidence variable to its observed value.
    restrict_factors = []
    for factor in factors:
        vars = factor.get_scope()
        has_evidence = False
        for var in vars:
            if var in varlist_evidence:
                has_evidence = True
                restrict_factors.append(restrict(factor, var, var.get_evidence()))
        if not has_evidence:
            restrict_factors.append(factor)

    # 4. Eliminate the hidden variables
    eliminate_factors = []
    # For each hidden variable h
    for h in hidden:
        # Multiply all the factors that contain h to create a new factor
        all_factors = get_factors_contain_var(restrict_factors, h)
        for f in all_factors:
            restrict_factors.remove(f)
        new_factor = multiply(all_factors)
        # Sum out h from the new factor.
        eliminate_factors.append(sum_out(new_factor, h))
    eliminate_factors.extend(restrict_factors)

    # 5. Multiply the remaining factors.
    multiply_factor = multiply(eliminate_factors)

    # 6. Normalize the remaining factor.
    result = normalize(multiply_factor)
    return result

def get_factors_contain_var(factor_list, var):
    result = []
    for factor in factor_list:
        variables = factor.get_scope()
        if var in variables:
            result.append(factor)
    return result
    


## The order of these domains is consistent with the order of the columns in the data set.
salary_variable_domains = {
"Work": ['Not Working', 'Government', 'Private', 'Self-emp'],
"Education": ['<Gr12', 'HS-Graduate', 'Associate', 'Professional', 'Bachelors', 'Masters', 'Doctorate'],
"Occupation": ['Admin', 'Military', 'Manual Labour', 'Office Labour', 'Service', 'Professional'],
"MaritalStatus": ['Not-Married', 'Married', 'Separated', 'Widowed'],
"Relationship": ['Wife', 'Own-child', 'Husband', 'Not-in-family', 'Other-relative', 'Unmarried'],
"Race": ['White', 'Black', 'Asian-Pac-Islander', 'Amer-Indian-Eskimo', 'Other'],
"Gender": ['Male', 'Female'],
"Country": ['North-America', 'South-America', 'Europe', 'Asia', 'Middle-East', 'Carribean'],
"Salary": ['<50K', '>=50K']
}

salary_variable=Variable("Salary", ['<50K', '>=50K'])

def naive_bayes_model(data_file, variable_domains=salary_variable_domains, class_var=salary_variable):
    '''
    NaiveBayesModel returns a BN that is a Naive Bayes model that represents 
    the joint distribution of value assignments to variables in the given dataset.

    Remember a Naive Bayes model assumes P(X1, X2,.... XN, Class) can be represented as 
    P(X1|Class) * P(X2|Class) * .... * P(XN|Class) * P(Class).

    When you generated your Bayes Net, assume that the values in the SALARY column of 
    the dataset are the CLASS that we want to predict. (query)

    Please name the factors as follows. If you don't follow these naming conventions, you will fail our tests.
    - The name of the Salary factor should be called "Salary" without the quotation marks.
    - The name of any other factor should be called "VariableName,Salary" without the quotation marks. 
      For example, the factor for Education should be called "Education,Salary".

    @return a BN that is a Naive Bayes model and which represents the given data set.
    '''
    ### READ IN THE DATA
    input_data = []
    with open(data_file, newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)
    ### YOUR CODE HERE ###
    variables = [class_var]
    factors = []
    variable_dict = {'Salary':class_var}
    factor_dict = {}

    # Define each variables
    for key in variable_domains:
        if key != 'Salary': # Since Salary is created, we will not create it again.
            name = key
            domains = variable_domains[key]
            var = Variable(name, domains)
            variables.append(var)
            variable_dict[key] = var
            factor_name = key + ',' + 'Salary'
            factor_dict[factor_name] = {}
            for domain in domains:
                for val in salary_variable.domain():
                    pair = domain + ',' + val
                    factor_dict[factor_name][pair] = 0
        else:
            factor_dict['Salary'] = {}
            for val in salary_variable.domain():
                factor_dict['Salary'][val] = 0
    salary_idx = headers.index('Salary')

    # Calculate probabilities
    for comb in input_data:
        for head in headers:
            head_idx = headers.index(head)
            if head != 'Salary':
                title = head + ',' + 'Salary'
                value_pair = comb[head_idx] + ',' + comb[salary_idx]
                factor_dict[title][value_pair] += 1
            else:
                title = head
                value_pair = comb[salary_idx]
                factor_dict[title][value_pair] += 1
    total_number = len(input_data)

    # Calculate P(Salary) i.e P(Class)
    salary_dict = factor_dict['Salary']
    salary_value_lst = build_value_list(salary_dict, total_number)

    # Create Salary factor
    salary_factor = Factor('Salary', [class_var])
    salary_factor.add_values(salary_value_lst)
    factors.append(salary_factor)

    # Create Factors
    for factor in factor_dict:
        name = factor
        if name != "Salary":
            scope = name.split(',')
            created_factor = Factor(name, gather_variables(variable_dict, scope))
            val_lst = build_value_list(factor_dict[factor], total_number)
            for vals in val_lst:
                salary_type = vals[1]
                salary_p = salary_factor.get_value([salary_type])
                vals[-1] = vals[-1]/salary_p
            created_factor.add_values(val_lst)
            # print(created_factor.values)
            factors.append(created_factor)
    bn = BN('result', variables, factors)
    return bn


def gather_variables(var_dict, scope):
    result = []
    for name in scope:
        result.append(var_dict[name])
    return result

def build_value_list(val_dict, total_number):
    result = []
    for val in val_dict:
        vals = val.split(',')
        vals.append(val_dict[val] / total_number)
        result.append(vals)
    return result


def explore(bayes_net:BN, question):
    '''    
    Return a probability given a Naive Bayes Model and a question number 1-6. 
    
    The questions are below: 
    1. What percentage of the women in the test data set does our model predict having a salary >= $50K? 
    2. What percentage of the men in the test data set does our model predict having a salary >= $50K? 
    3. What percentage of the women in the test data set satisfies the condition: P(S=">=$50K"|Evidence) is strictly greater than P(S=">=$50K"|Evidence,Gender)?
    4. What percentage of the men in the test data set satisfies the condition: P(S=">=$50K"|Evidence) is strictly greater than P(S=">=$50K"|Evidence,Gender)?
    5. What percentage of the women in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?
    6. What percentage of the men in the test data set with a predicted salary over $50K (P(Salary=">=$50K"|E) > 0.5) have an actual salary over $50K?

    @return a percentage (between 0 and 100)
    ''' 
    ### YOUR CODE HERE ###
    ### READ IN THE DATA
    input_data = []
    with open('data/adult-test.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None) #skip header row
        for row in reader:
            input_data.append(row)
    ########################
    salary_idx = headers.index('Salary')
    evidence = ['Work', 'Occupation', 'Education', 'Relationship']
    if question == 1: # P(gender=female | salary = >=50K)
        female_idx = headers.index('Gender')
        total_num = 0
        count = 0
        for row in input_data:
            if row[female_idx] == "Female":
                total_num += 1
                prob = ve_calculation(bayes_net, headers, row, evidence)
                if prob.values[1] > 0.5:
                    count += 1
        return count / total_num * 100
    if question == 2: # P(gender=male | salary = >=50K)
        female_idx = headers.index('Gender')
        total_num = 0
        count = 0
        for row in input_data:
            if row[female_idx] == "Male":
                total_num += 1
                prob = ve_calculation(bayes_net, headers, row, evidence)
                if prob.values[1] > 0.5:
                    count += 1
        return count / total_num * 100
    if question == 3: # P(salary = >=50K|evidence) > P(salary = >=50K|evidence, Gender)
        female_idx = headers.index('Gender')
        total_num = 0
        count = 0
        for row in input_data:
            if row[female_idx] == "Female":
                total_num += 1
                prob1 = ve_calculation(bayes_net, headers, row, evidence)
                prob2 = ve_calculation(bayes_net, headers, row, evidence + ['Gender'])
                if prob1.values[1] > prob2.values[1]:
                    count += 1
        return count / total_num * 100
    if question == 4: # P(salary = >=50K|evidence) > P(salary = >=50K|evidence, Gender)
        female_idx = headers.index('Gender')
        total_num = 0
        count = 0
        for row in input_data:
            if row[female_idx] == "Male":
                total_num += 1
                prob1 = ve_calculation(bayes_net, headers, row, evidence)
                prob2 = ve_calculation(bayes_net, headers, row, evidence + ['Gender'])
                if prob1.values[1] > prob2.values[1]:
                    count += 1
        return count / total_num * 100
    if question == 5: # P(gender=female | salary = >=50K)
        female_idx = headers.index('Gender')
        total_num = 0
        count = 0
        for row in input_data:
            if row[female_idx] == "Female":
                prob = ve_calculation(bayes_net, headers, row, evidence)
                if prob.values[1] > 0.5:
                    total_num += 1
                    if row[salary_idx] == '>=50K':
                        count += 1
        return count / total_num * 100
    if question == 6: # P(gender=female | salary = >=50K)
        female_idx = headers.index('Gender')
        total_num = 0
        count = 0
        for row in input_data:
            if row[female_idx] == "Male":
                prob = ve_calculation(bayes_net, headers, row, evidence)
                if prob.values[1] > 0.5:
                    total_num += 1
                    if row[salary_idx] == '>=50K':
                        count += 1
        return count / total_num * 100

def ve_calculation(bayes_net, headers, values, evidence):
    query = bayes_net.get_variable('Salary')
    e_variables = []
    for e in evidence:
        variable = bayes_net.get_variable(e)
        e_idx = headers.index(e)
        e_value = values[e_idx]
        variable.set_evidence(e_value)
        e_variables.append(variable)
    return ve(bayes_net, query, e_variables)


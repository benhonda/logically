import itertools
from halp.directed_hypergraph import DirectedHypergraph
from pprint import pprint
from bitarray import bitarray
import json


class H:
    def __init__(self, n=2, s=2) -> None:
        self.hypergraph = DirectedHypergraph()
        self.n = n
        self.size = s
        self.map_to_tt = None
        self.map_to_canonical = None
        self.replacement_rules = None

    def set_attrs(self, map_to_tt=None, map_to_canonical=None, replacement_rules=None):
        self.map_to_tt = map_to_tt if map_to_tt is not None else self.map_to_tt
        self.map_to_canonical = map_to_canonical if map_to_canonical is not None else self.map_to_canonical
        self.replacement_rules = replacement_rules if replacement_rules is not None else self.replacement_rules

    def add_node_set(self, list_of_nodes=[]):
        '''
        Method to add nodes to the hypergraph.
        '''
        self.hypergraph.add_nodes(list_of_nodes)

    def add_hyperedge(self, premises, conclusion):
        '''
        Method to add the hyperedge to the hypergraph. Called from add_edge(...)
        '''
        prems = []
        for prem in premises:
            prems.append(prem.to01())  # prem is a bitarray. Convert it to str

        concs = []
        for conc in conclusion:
            concs.append(conc.to01())  # conc is a bitarray. Convert it to str

        # print(prems)
        id = self.hypergraph.add_hyperedge(prems, concs)
        # print(f'iddd = {id}')
        # DirectedHypergraph().add

    def add_edges(self):
        if len(self.map_to_tt) == 0:
            print("No nodes to add edges to!")
            return

        # for inf in ['mp', 'mt', 'hs', 'ds', 'cd', 'dd', 'simp', 'conj', 'add']:
        for inf in ['mp', 'mt', 'hs', 'ds', 'cd', 'dd', 'simp', 'conjadd']:
            # enumerate over all possible applications of that rule
            # prop space is all the keys of map_to_tt
            print(f'\n****: {inf}')
            for (i, prop) in enumerate(self.map_to_tt):
                # print(f'**** {prop}')
                print(f'prop {i+1} of {len(self.map_to_tt)} done for "{inf}"', end='\r')

                prop = json.loads(prop)
                if inf == 'mp':  # modus ponens
                    if len(prop) == 3 and prop[1] == '->':  # if the prop is of the form ['p', '->', 'q']

                        p_q, p, q = prop, prop[0], prop[2]

                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p_q, p], prop_concs=[q]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p_q),
                                self.Eval(p),
                            ], conclusion=[
                                self.Eval(q)
                            ])

                elif inf == 'mt':  # modus tonens
                    if len(prop) == 3 and prop[1] == '->':  # if the prop is of the form ['p', '->', 'q']

                        p_q, p, q = prop, prop[0], prop[2]

                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p_q, q], prop_concs=[p]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p_q),
                                ~self.Eval(q),
                            ], conclusion=[
                                ~self.Eval(p)
                            ])

                elif inf == 'hs':  # hypothetical syllogism / chain argument
                    if len(prop) == 3 and prop[1] == '->':  # if prop is of the form ['p', '->', 'q']

                        for second_prop in self.map_to_tt:
                            second_prop = json.loads(second_prop)
                            # we know we can do a chain argument with prop and second_prop if...
                            if len(second_prop) == 3 and second_prop[1] == '->' and prop[2] == second_prop[0]:

                                p_q, q_r, p, r = prop, second_prop, prop[0], second_prop[2]

                                # verify we can add and should add this edge to the hypergraph
                                if self.should_add_edge(prop_prems=[p_q, q_r], prop_concs=[[p, '->', r]]):
                                    # actually add the hyperedge
                                    self.add_hyperedge(premises=[
                                        self.Eval(p_q),
                                        ~self.Eval(q_r),
                                    ], conclusion=[
                                        ~self.Eval(p) | self.Eval(r)
                                    ])

                elif inf == 'ds':  # disjunctive syllogism / disjunctive argument
                    if len(prop) == 3 and prop[1] == '|':  # if props is of the form ['p', '|', 'q']

                        p_or_q, p, q = prop, prop[0], prop[2]

                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p_or_q, p], prop_concs=[q]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p_or_q),
                                ~self.Eval(p),
                            ], conclusion=[
                                self.Eval(q)
                            ])

                        # for ([p v q, ~p], q)
                        # add_edge(H=hypergraph, premises=[
                        #     Eval(prop, state),
                        #     ~Eval(prop[0], state),
                        # ], conclusion=[
                        #     Eval(prop[2], state),
                        # ])

                        # for ([p v q, ~q], state)
                        # -- don't think we need this? should be covered in our node set... but we'll see

                elif inf == 'cd':  # constructive dilemma
                    if len(prop) == 3 and prop[1] == '&' and \
                            isinstance(prop[0], list) and len(prop[0]) == 3 and prop[0][1] == '->' and \
                            isinstance(prop[2], list) and len(prop[2]) == 3 and prop[2][1] == '->':  # if prop is of the form ['(x -> x)', '&', '(x -> x)']

                        p_imp_q_and_r_imp_s, p, q, r, s = prop, prop[0][0], prop[0][2], prop[2][0], prop[2][2],

                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p_imp_q_and_r_imp_s, [
                                                p, '|', r]], prop_concs=[[q, '|', s]]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p_imp_q_and_r_imp_s),
                                self.Eval(p) | self.Eval(r)
                            ], conclusion=[
                                self.Eval(q) | self.Eval(s)
                            ])

                elif inf == 'dd':  # destructive dilemma
                    if len(prop) == 3 and prop[1] == '&' and \
                            isinstance(prop[0], list) and len(prop[0]) == 3 and prop[0][1] == '->' and \
                            isinstance(prop[2], list) and len(prop[2]) == 3 and prop[2][1] == '->':  # if prop is of the form ['(x -> x)', '&', '(x -> x)']

                        p_imp_q_and_r_imp_s, p, q, r, s = prop, prop[0][0], prop[0][2], prop[2][0], prop[2][2],

                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p_imp_q_and_r_imp_s, [
                                                q, '|', s]], prop_concs=[[p, '|', r]]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p_imp_q_and_r_imp_s),
                                ~self.Eval(q) | ~self.Eval(s)
                            ], conclusion=[
                                ~self.Eval(p) | ~self.Eval(r)
                            ])

                elif inf == 'simp':  # simplification
                    if len(prop) == 3 and prop[1] == '&':  # if prop is of the form ['x', '&', 'x']

                        # TODO: need the reverse? same questions for disjunctive syllogism

                        p_and_q, p, q = prop, prop[0], prop[2]

                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p_and_q], prop_concs=[q]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p_and_q),
                            ], conclusion=[
                                self.Eval(q)
                            ])

                elif inf == 'conjadd':  # conjunction or addition
                # elif inf == 'conj' or inf == 'add':  # conjunction or addition
                    for second_prop in self.map_to_tt:
                        second_prop = json.loads(second_prop)

                        p, q = prop, second_prop

                        # conjunction
                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p, q], prop_concs=[[p, '&', q]]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p),
                                self.Eval(q)
                            ], conclusion=[
                                self.Eval(p) & self.Eval(q)
                            ])

                        # addition
                        # verify we can add and should add this edge to the hypergraph
                        if self.should_add_edge(prop_prems=[p], prop_concs=[[p, '|', q]]):
                            # actually add the hyperedge
                            self.add_hyperedge(premises=[
                                self.Eval(p)
                            ], conclusion=[
                                self.Eval(p) | self.Eval(q)
                            ])

                # elif inf == 'add':  # addition
                #     for second_prop in self.map_to_tt:
                #         second_prop = json.loads(second_prop)

                #         p, q = prop, second_prop

                #         # verify we can add and should add this edge to the hypergraph
                #         if self.should_add_edge(prop_prems=[p], prop_concs=[[p, '|', q]]):
                #             # actually add the hyperedge
                #             self.add_hyperedge(premises=[
                #                 self.Eval(p)
                #             ], conclusion=[
                #                 self.Eval(p) | self.Eval(q)
                #             ])

    def should_add_edge(self, prop_prems, prop_concs):
        '''
        Checks that the following constraints are met:
            1. Size(EvalS(p)) <= s for all p in prop_prems and prop_concs
            2. EvalS(p)) is not None for all p in prop_prems and prop_concs

        Note: EvalS returns None when we cannot rewrite p into it's canonical using the given replacement rules
        '''

        for prop_list in (prop_prems, prop_concs):
            for prop in prop_list:
                # condition (2)
                canonical_prop = self.EvalS(prop) if isinstance(prop, list) else self.EvalS([prop])
                if canonical_prop is None:
                    return False

                # condition (1)
                if self.Size(canonical_prop) > self.size:
                    return False

        return True

    def Eval(self, prop):
        '''
        The function Eval is as follows:

        Eval(q1 ∧ q2, p) = Eval(q1, p) & Eval(q2, p)
        Eval(q1 v q2, p) = Eval(q1, p) ‖ Eval(q2, p)
        Eval(~q, p) = ~Eval(q, p)
        Eval(x, p) = p(x)

        Eval should return a bitarray, which can be manipulated using bitwise operators
        '''
        as_str = json.dumps(prop) if isinstance(prop, list) else json.dumps([prop])
        return bitarray(self.map_to_tt[as_str])

    def EvalS(self, prop):
        '''
        EvalS substitutes each free variable x in prop by Canonical(map_to_tt[x])

        Returns either:
          - a prop, where each free var is a Canonical prop
          - None, if any of the free vars cannot be rewritten into their canonical's using the given set of replacement rules.

        TODO: implement this function
          - I assume this fn will work like this:

              Given (x1 & x1) -> x2...

                Canonical(map_to_tt["'x1', '&', 'x1'"])      -> returns x1
                Canonical(map_to_tt["'x2'"])                 -> returns x2

                  return ['x1', '->', 'x2']

          - then, to fulfill the (ii) condition in the paper,
            we need to check that we can get from x1 & x1 to x1 using the given set of replacement rules.
        '''

        if len(prop) > 3:
            # not a valid prop
            return

        rebuilt_prop = []
        for freevar in prop:
            # print(f'((((( {freevar} -in- {prop}')
            as_str = json.dumps(freevar) if isinstance(freevar, list) else json.dumps([freevar])
            if 'x' in as_str:
                # var
                # tt = self.map_to_tt[json.dumps([freevar])]
                tt = self.map_to_tt[as_str]
                can_prop = self.map_to_canonical[tt]
                rebuilt_prop.append(can_prop)
            else:
                # connective
                rebuilt_prop.append(freevar)

        # TODO: we need to check that we can get from x1 & x1 to x1 using the given set of replacement rules.
        print(f'prop: {prop}  -  Reb: {rebuilt_prop}')
        return rebuilt_prop

    def Size(self, prop):
        '''
        Return the size of a proposition as an integer (the number of variable occurences in it)
        '''
        prop_str = json.dumps(prop)
        return prop_str.count('x')  # we're looking for all variable occurences, i.e., all 'x' in the string


def is_list_multi_element_valid(prop):
    '''
    Check if array contains all the same elements
    '''

    # return True

    valid = False

    if len(prop) <= 1:
        return True

    init = prop[0]
    # caught = []

    # checks for same elements:
    # for p in prop:
    #     if p != init:
    #         valid = True
    #         break

    valid = True
    caught = []

    for (i, p) in enumerate(prop):

        # if ('~' in p and p[1:] in caught) or ('~' not in p and f'~{p}' in caught) or (p in caught):
        # ^^^^^^^ definitely not correct! only creates 36/38 TTs with n=3 s=2

        # if ('~' in p and p[1:] in caught) or ('~' not in p and f'~{p}' in caught):
        # ^^^^^^^ definitely not correct! only creates 37/38 TTs with n=3 s=2

        if p in caught:

            # if i == 0 and '~' in p:
            # if False:
            valid = False
            break

        caught.append(p)

    return valid


def getSizeOfNestedList(listOfElem):
    ''' Get number of elements in a nested list'''
    count = 0
    # Iterate over the list
    for elem in listOfElem:
        # Check if type of element is list
        if isinstance(elem, list):
            # Again call this function to get the size of this element
            count += getSizeOfNestedList(elem)
        else:
            count += 1
    return count


def add_prop_with_connectives(prop_list=[], prop=[]):
    '''
    This function appends all the permutations of a given prop with connectives to prop_list.

    Returns a prop_list.
    '''
    # num_gaps = len(prop) - 1
    # print("prop")
    # print(prop)
    num_gaps = getSizeOfNestedList(prop) - 1

    connectives_options = ['&', '|', '->', '<->']
    # connectives_options = ['&', '|', '->']
    connective_permutations = itertools.product(connectives_options, repeat=num_gaps)

    for connectives in connective_permutations:
        new_perm = []
        connective_list = list(connectives)

        # current = prop[0]
        # while (type(current) is list):
        '''
        x1 ((x2 x3) x4)

        # x1 ((x2 x3) x4)


        ['~x3', ['~x3', 'x3']]
        ['&', '|']

        [['x1', '~x2'], 'x1']
        ['&', '&']

        [['x1', ['x1', 'x2']], 'x1']
        ['&', '&', '&']
        '''
        for (i, sub) in enumerate(prop):
            if isinstance(sub, list):
                # nested list #1
                list1 = []
                attach_conn_outside1 = False

                for (j, sub2) in enumerate(sub):
                    if isinstance(sub2, list):
                        # nested list #2
                        list2 = []
                        attach_conn_outside = False

                        for (h, sub3) in enumerate(sub2):
                            list2.append(sub3)
                            if len(connective_list) > 0:
                                if h == len(sub2) - 1:
                                    attach_conn_outside = True
                                else:
                                    list2.append(connective_list.pop(0))

                        list1.append(list2)
                        if attach_conn_outside and j != len(sub) - 1:
                            list1.append(connective_list.pop(0))
                    else:
                        # sub2 not a list
                        # new_perm.append(sub2)
                        list1.append(sub2)
                        if len(connective_list) > 0:
                            if j == len(sub) - 1:
                                attach_conn_outside1 = True
                            else:
                                list1.append(connective_list.pop(0))

                new_perm.append(list1)
                if attach_conn_outside1:
                    if len(connective_list) > 0:
                        new_perm.append(connective_list.pop(0))
            else:
                # not a list
                new_perm.append(sub)
                if len(connective_list) > 0:
                    new_perm.append(connective_list.pop(0))

        # for (i, var) in enumerate(prop):
        #     new_perm.append(var)
        #     if (i < len(connectives)):
        #         new_perm.append(connectives[i])
        # print(connective_list)
        # print(new_perm)

        counts[f'{num_gaps + 1}'] += 1
        counts['TOT'] += 1
        prop_list.append(new_perm)

    return


def parenthesize(prop):
    '''
    Gets all parentheses combinations for a prop (size<=5).

    Returns a list of lists (props)
    '''

    props = []

    if is_list_multi_element_valid(prop):
        props.append(prop)
        # add_prop_with_connectives(props, prop)

    for bite_size in range(len(prop) - 1, 1, -1):
        props += parse_s(prop, s=bite_size)

    prop_list = []

    # for (i, prop) in enumerate(props):
    #     # props[i] =

    for prop in props:
        # print(prop)
        add_prop_with_connectives(prop_list=prop_list, prop=prop)

    # if len(prop_list) > 0:
    #     print(prop_list)

    return prop_list


def parse_s(prop, s):
    '''
    Gets all s-element parentheses for s<=5.
    Note: does NOT get all parentheses. Use the parenthesize function for that.

    Returns a list of lists (props)
    '''
    props = []
    # get singles
    for i in range(len(prop) - (s - 1)):
        pre = []
        if i != 0:
            pre = prop[0:i]

        bite = prop[i:i + s]
        rest = prop[i + s:]

        # print("bite---------")
        # print(bite)

        # only add a list with valid elements
        if is_list_multi_element_valid(bite):
            props.append(pre + [bite] + rest)
            # p = pre + [bite] + rest
            # print("pre ======")
            # print(p)
            # add_prop_with_connectives(props, p)

        # print("bite---*-*-*-*-*--")
        # print(bite)

        for childS in range(s - 1, 1, -1):
            # get children
            children = parse_s(bite, childS)
            # print("children()()()()()")
            # print(children)
            for child in children:
                # only add a list with valid elements
                if is_list_multi_element_valid(child):
                    props.append(pre + [child] + rest)
                    # p = pre + [child] + rest
                    # print("pre*****")
                    # print(p)
                    # add_prop_with_connectives(props, p)

    # TODO: include this in above fn
    if s == 2:
        # get doubles
        for i in range(len(prop)):
            pre = []
            if i != 0:
                pre = prop[0:i]
            first_of_two = prop[i:i + 2]
            rest = prop[i + 2:]

            if len(rest) == 3:
                if is_list_multi_element_valid(first_of_two):
                    props.append(pre + [first_of_two] + [rest])
                    # add_prop_with_connectives(props, pre + [first_of_two] + [rest])
                for bite_size in range(len(rest) - 1, 1, -1):
                    singles3 = parse_s(prop=rest, s=bite_size)
                    for single in singles3:
                        if is_list_multi_element_valid(first_of_two):
                            props.append(pre + [first_of_two] + [single])
                            # add_prop_with_connectives(props, pre + [first_of_two] + [single])

            for j in range(len(rest) - 1):
                pre2 = []
                if j != 0:
                    pre2 = rest[0:j]
                second_of_two = rest[j:j + 2]

                p2 = pre + [first_of_two] + pre2 + [second_of_two] + rest[j + 2:]
                if is_list_multi_element_valid(first_of_two) and is_list_multi_element_valid(second_of_two):
                    props.append(p2)
                    # add_prop_with_connectives(props, p2)

    if s == 3:
        # get doubles
        for i in range(len(prop)):
            pre = []
            if i != 0:
                pre = prop[0:i]
            first_of_two = prop[i:i + s]
            rest = prop[i + s:]

            if len(rest) >= 2:
                if len(first_of_two) == 3:
                    if is_list_multi_element_valid(first_of_two):
                        props.append(pre + [first_of_two] + [rest])
                        # add_prop_with_connectives(props, pre + [first_of_two] + [rest])

                    for bite_size in range(len(first_of_two) - 1, 1, -1):
                        singles3 = parse_s(prop=first_of_two, s=bite_size)
                        for single in singles3:
                            if is_list_multi_element_valid(single):
                                props.append(pre + [single] + [rest])
                                # add_prop_with_connectives(props, pre + [single] + [rest])

                if len(rest) == 3:
                    if is_list_multi_element_valid(first_of_two):
                        props.append(pre + [first_of_two] + [rest])
                        # add_prop_with_connectives(props, pre + [first_of_two] + [rest])

                    for bite_size in range(len(rest) - 1, 1, -1):
                        singles3 = parse_s(prop=rest, s=bite_size)
                        for single in singles3:
                            if is_list_multi_element_valid(first_of_two) and is_list_multi_element_valid(single):
                                props.append(pre + [first_of_two] + [single])
                                # add_prop_with_connectives(props, pre + [first_of_two] + [single])

    return props


def do_binary_arithmetic(t1, t2, conn):
    '''
    Calculates the result of a propositional statement.

    Returns a Bool
    '''

    if conn == '&':
        return bool(t1) and bool(t2)

    if conn == '|':
        return bool(t1) or bool(t2)

    if conn == '->':
        return not bool(t1) or bool(t2)

    if conn == '<->':
        return (bool(t1) and bool(t2)) or (not bool(t1) and not bool(t2))

    print(f'ERR: what is this connective? {conn}')
    return


def calculate_prop(prop, mapping):
    '''
    Returns the computed boolean result of the given prop
    '''
    boolvals = []
    conns = []

    for var in prop:
        if isinstance(var, list):  # if this is a list...
            TorF = calculate_prop(prop=var, mapping=mapping)
            boolvals.append(TorF)
        else:
            if 'x' in var:
                boolvals.append(mapping[var])  # this is a variable
            else:
                conns.append(var)  # this is a connective

    order_of_precedence = ['&', '|', '->', '<->']
    while len(order_of_precedence) > 0:
        current_conn = order_of_precedence[0]

        for (i, conn) in enumerate(conns):
            if conn == current_conn:  # if the connective we're after is found...
                # we need to compute the boolean result of the vars that surround it
                first_var_i = i
                # second_var_i = len(boolvals) - 1 if i == len(conns) - 1 else i + 1
                second_var_i = i + 1
                boolean_result = do_binary_arithmetic(boolvals[first_var_i], boolvals[second_var_i], conn)
                # now replace the binary expression with its boolean result
                # we do this by replacing the first of the 2 boolvals we just
                # used with their result, and removing the second
                boolvals[first_var_i] = boolean_result
                boolvals.pop(second_var_i)  # remove this element
                conns.pop(i)  # remove this connective

        if current_conn not in conns:
            # TODO: remove all list.pop 's with more performant solutions
            order_of_precedence.pop(0)  # pop off, queen!

    # while (len(boolvals) > 1):
    #     current_bools = boolvals[:2]
    #     new_boolvals = boolvals[2:]
    #     # print("prop")
    #     # print(prop)
    #     # print("conns")
    #     # print(conns)
    #     '''
    #     TODO: follow BEDMAS / its equivalent for logical operators
    #           surely we are generating the wrong binary strings when there are 3+ vars in a set of parantheses

    #         DONE???????? I think so........
    #     '''
    #     res = do_binary_arithmetic(current_bools[0], current_bools[1], conns.pop(0))
    #     new_boolvals.insert(0, res)
    #     boolvals = new_boolvals

    # When we exit the loop, there should only be one boolean value in boolvals.
    # This is the value of the prop on this level (inside this set of parens)
    return boolvals[0]


def evaluate_props(props_with_parens):
    '''
    Generate a truth table for each prop in a list of props.

    Params:
      - props_with_parens: list of props

    Returns:
      - a list of unique truth tables as 32-bit integers
      - reverse mapping 'Canonical'


    3. ['x4', '&', ['~x3', '->', ['~x2', '<->', '~x1']]]
    2. ['~x3', '->', ['~x2', '<->', '~x1']]
    1. ['~x2', '<->', '~x1']
    '''
    n = 5
    binary_boolean_combinations = list(itertools.product([False, True], repeat=n))

    binary_strs = []
    # props = []

    for prop in props_with_parens:
        '''We need to substitute vars with truth table values'''

        binary_str = ''

        for combo in binary_boolean_combinations:

            '''The mapping maps each var to a boolean value'''
            mapping = {}
            for (i, boolval) in enumerate(combo):
                mapping[f'x{i+1}'] = boolval
                mapping[f'~x{i+1}'] = not boolval

            prop_result = calculate_prop(prop=prop, mapping=mapping)
            binary_str += '1' if prop_result else '0'

        '''TODO: nested brackets cannot be printed with .join'''
        # print(f'{" ".join(prop)} - {binary_str}')
        # print(f'heu')
        print(f'{prop} - {binary_str}')

        # if binary_str not in binary_strs:  # only if the string has not beed added already
        #     binary_strs.append(binary_str)
        binary_strs.append(binary_str)
        # props.append(prop)

    # print(f'{len(binary_strs)} discovered truth tables')
    return binary_strs


counts = {'TOT': 0}


def generate_node_set(Hypergraph=H()):

    vars = []
    for i in range(1, n + 1):
        vars.append(f'x{i}')
        vars.append(f'~x{i}')

    canonical = {}
    map_props_to_tt = {}

    binary_strs = []
    binary_strs_props = []
    total_binary_strs = []
    ones = 0
    zeros = 0
    identities = 0
    against_test = 0
    test_against = [
        '11111111111111111111111111111111',
        '00000000000000000000000000000000',

        '00000000000000001111111111111111',  # x1
        '11111111111111110000000000000000',  # ~x1

        '00000000111111110000000011111111',  # x2
        '11111111000000001111111100000000',  # ~x2

        '00001111000011110000111100001111',  # x3
        '11110000111100001111000011110000',  # ~x3


        # '00110011001100110011001100110011', #  x4
        # '11001100110011001100110011001100', # ~x4
    ]

    for prop_size in range(1, Hypergraph.size + 1):
        # Get all possible permutations of variables (with repetition)
        var_permutations = itertools.product(vars, repeat=prop_size)

        counts[f'{prop_size}'] = 0
        # counts['binary_strs'] = 0f

        for permutation in var_permutations:

            # print(permutation)

            permutation = list(permutation)

            '''Paranthesize'''
            # for bite_size in range(len(permutation) - 1, 1, -1):
            #     pass

            # x1 x2 x3 x4
            '''
            s=4
            x1 x2 x3 x4

            3 element steps
            (x1 x2 x3) x4
                ((x1 x2) x3) x4
                (x1 (x2 x3)) x4

            x1 (x2 x3 x4)
                x1 ((x2 x3) x4)
                x1 (x2 (x3 x4))

            2 element steps
            (x1 x2) (x3 x4)
            (x1 x2) x3 x4
            x1 (x2 x3) x4
            x1 x2 (x3 x4)
            '''

            # print(parenthesize(permutation))
            props_with_parens = parenthesize(permutation)

            # print(len(props_with_parans))

            binarys_strs = evaluate_props(props_with_parens=props_with_parens)

            # binary_strs += binarys_strs
            # total_binary_strs += binary_strs

            for (i, str) in enumerate(binarys_strs):
                # add prop->TruthTable map
                map_props_to_tt[json.dumps(props_with_parens[i])] = str

                total_binary_strs.append(str)
                if str == '11111111111111111111111111111111':
                    ones += 1
                elif str == '00000000000000000000000000000000':
                    zeros += 1

                if str in test_against:
                    against_test += 1

                if not str in binary_strs:  # not already added
                    binary_strs.append(str)  # add it
                    binary_strs_props.append(props_with_parens[i])  # add the relevant prop
                    canonical[str] = props_with_parens[i]  # canonical mapping

    print(counts)
    print(f'TTs: {len(binary_strs)}')
    # print(f'{len(total_binary_strs)}')
    # print(f'#0s: {zeros}  #1s: {ones}  against_test: {against_test}')
    print(f'n={int(len(vars)/2)}  s={Hypergraph.size}')

    # add the canonical mapping
    Hypergraph.set_attrs(map_to_tt=map_props_to_tt, map_to_canonical=canonical)
    # add the node set
    Hypergraph.add_node_set(binary_strs)
    # hypergraph.add_nodes(binary_strs)


def generate_edge_set(Hypergraph=H()):
    '''
    Generate the edge set of the hypergraph.

    state p maps props to truth tables
        p  =  {
          ...
          '["x1", "&", "x2"]': '00100100010001001001...',
          ...
        }
    '''

    Hypergraph.add_edges()
    pass


if __name__ == '__main__':
    n = 1  # num vars
    s = 4  # max size

    H_obj = H(n=n, s=s)

    generate_node_set(Hypergraph=H_obj)

    generate_edge_set(Hypergraph=H_obj)

    h_edge_set = H_obj.hypergraph.get_hyperedge_id_set()
    # print(h_edge_set)
    print(f'# Edges: {len(h_edge_set)}')

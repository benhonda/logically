
def parse_s_singles(prop, s):
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

        props.append(pre + [bite] + rest)

        for childS in range(s - 1, 1, -1):
            # get children
            children = parse_s(bite, childS)
            for child in children:
                props.append(pre + [child] + rest)

    return props


def parse4(prop):
    '''
    Gets all 4-element parentheses for s<=5

    Returns a list of lists (props)
    '''
    props = []
    # get singles
    for i in range(len(prop) - 3):
        pre = []
        if i != 0:
            pre = prop[0:i]

        bite = prop[i:i + 4]
        rest = prop[i + 4:]

        props.append(pre + [bite] + rest)

        # get 3s
        threes = parse3(bite)
        for three in threes:
            props.append(pre + [three] + rest)

        # get 2s
        twos = parse2(bite)
        for two in twos:
            props.append(pre + [two] + rest)

    return props


def parse3(prop):
    '''
    Gets all 3-element parentheses for s<=5

    Returns a list of lists (props)
    '''
    props = []
    # get singles
    for i in range(len(prop) - 2):
        pre = []
        if i != 0:
            pre = prop[0:i]

        bite = prop[i:i + 3]
        rest = prop[i + 3:]

        props.append(pre + [bite] + rest)

        # get 2s
        twos = parse2(bite)
        for two in twos:
            props.append(pre + [two] + rest)

    return props


def parse2(prop):
    '''
    Gets all 2-element parentheses for s<=5

    Returns a list of lists (props)
    '''
    props = []
    # get singles
    for i in range(len(prop) - 1):
        pre = []
        if i != 0:
            pre = prop[0:i]
        p = pre + [prop[i:i + 2]] + prop[i + 2:]
        props.append(p)

    # get doubles
    for i in range(len(prop)):
        pre = []
        if i != 0:
            pre = prop[0:i]
        first_of_two = prop[i:i + 2]
        rest = prop[i + 2:]

        for j in range(len(rest) - 1):
            pre2 = []
            if j != 0:
                pre2 = rest[0:j]
            second_of_two = rest[j:j + 2]

            p2 = pre + [first_of_two] + pre2 + [second_of_two] + rest[j + 2:]
            props.append(p2)

        # if len(rest) <= 2:
        #     break

    return props

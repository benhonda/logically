import itertools

def generate_propositions(variables):
  # Get all possible combinations of variables
  var_combinations = itertools.combinations_with_replacement(variables, 4)

  # Generate all possible propositions using the combinations of variables
  propositions = []
  for combination in var_combinations:
    for permutation in itertools.permutations(combination):
      proposition = ' '.join(permutation)
      propositions.append(proposition)

  # Add connectives to the propositions
  connectives = ['&', '|', '->', '<->']
  propositions_with_connectives = []
  for proposition in propositions:
    for i in range(len(proposition.split())):
      for connective in connectives:
        modified_proposition = proposition[:i] + connective + proposition[i:]
        propositions_with_connectives.append(modified_proposition)

  return propositions_with_connectives






if __name__ == '__main__':
    variables = ['A', '~A', 'B', '~B' 'C', 'D']
    propositions = generate_propositions(variables)
    print(propositions)

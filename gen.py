import random


def generate_proof(num_vars, num_steps):
    # Create a list of propositional variables
    variables = ['P' + str(i) for i in range(1, num_vars + 1)]

    # Choose a random conclusion for the proof
    # TODO: allow for more complex conclusions like ~PvQ
    conclusion = random.choice(variables)

    # Initialize the proof with the conclusion as the first line
    proof = [conclusion]

    # Keep generating premises until the proof has the desired number of steps
    while len(proof) < num_steps:
        # Choose a random rule of inference to apply
        rule = random.choice(['ca', 'da', 'conj', 'add'])

        # Apply the chosen rule of inference to generate a new premise
        if rule == 'hypothetical_syllogism':
            # Choose two random premises that imply the conclusion
            premise1, premise2 = random.sample([p for p in variables if p + ' → ' + conclusion in proof], 2)
            # Add the premise that is implied by the other two to the proof
            proof = [premise1 + ' → ' + premise2] + proof
        elif rule == 'disjunctive_syllogism':
            # Choose a random premise that is a disjunction of two other premises
            premise1 = random.choice([p for p in variables if p.startswith('(') and p.endswith(')')])
            # Extract the two disjuncts from the premise
            disjunct1, disjunct2 = premise1[1:-1].split(' ∨ ')
            # Choose one of the disjuncts as the premise to add to the proof
            premise2 = random.choice([disjunct1, disjunct2])
            # Add the negation of the other disjunct to the proof
            proof = ['~' + ('∨'.join([disjunct1, disjunct2]) == premise2) + premise2] + proof
        elif rule == 'conjunction':
            # Choose two random premises to conjunct
            premise1, premise2 = random.sample(variables, 2)
            # Add the conjunction of the two premises to the proof
            proof = [premise1 + ' ∧ ' + premise2] + proof
        elif rule == 'addition':
            # Choose a random premise to add to the proof
            premise1 = random


if __name__ == '__main__':
    generate_proof()

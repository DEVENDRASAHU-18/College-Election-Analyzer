def get_input():
    """
    Collects election data from the user.
    Returns: eligible_voters, candidates (list of dicts), invalid_votes
    """
    print("\n===== COLLEGE ELECTION RESULT ANALYZER =====\n")

    # Get eligible voters
    eligible = int(input("Enter total number of eligible voters: "))

    candidates = []
    print("\nEnter candidate details. Type 'done' when finished.")
    while True:
        name = input("Candidate name (or 'done' to stop): ").strip()
        if name.lower() == 'done':
            break
        if name == "":
            print("Name cannot be empty. Try again.")
            continue
        votes = int(input(f"Votes received by {name}: "))
        candidates.append({"name": name, "votes": votes})

    invalid = int(input("\nEnter total number of invalid votes: "))

    return eligible, candidates, invalid


def validate_data(eligible, candidates, invalid):
    """
    Checks mathematical consistency:
    - All vote counts non-negative
    - Sum of candidate votes equals total valid votes
    - Total votes (valid + invalid) <= eligible voters
    Returns: (is_valid, error_message)
    """
    # Check negative values
    if invalid < 0:
        return False, "Invalid votes cannot be negative."

    total_valid = 0
    for c in candidates:
        if c["votes"] < 0:
            return False, f"Votes for {c['name']} cannot be negative."
        total_valid += c["votes"]

    
    total_votes_cast = total_valid + invalid
    if total_votes_cast > eligible:
        return False, f"Total votes ({total_votes_cast}) exceed eligible voters ({eligible})."

    # Check that there is at least one candidate
    if len(candidates) == 0:
        return False, "At least one candidate must be entered."

    return True, ""


def calculate_results(eligible, candidates, invalid):
    """
    Computes rankings, percentages, participation rate, victory margin,
    and checks for ties.
    Returns a dictionary with all results.
    """
    total_valid = sum(c["votes"] for c in candidates)
    total_votes_cast = total_valid + invalid

    # Participation rate
    participation = (total_votes_cast / eligible) * 100 if eligible > 0 else 0

    # Sort candidates by votes descending
    sorted_candidates = sorted(candidates, key=lambda x: x["votes"], reverse=True)

    # Calculate percentages for each candidate
    for c in sorted_candidates:
        c["percentage"] = (c["votes"] / total_valid) * 100 if total_valid > 0 else 0

    # Determine winner and check for tie
    winner = None
    tie = False
    if len(sorted_candidates) > 0:
        top_votes = sorted_candidates[0]["votes"]
        # Count how many have the top votes
        top_count = sum(1 for c in sorted_candidates if c["votes"] == top_votes)
        if top_count > 1:
            tie = True
            # If tie, we can list all tied candidates
            tied_names = [c["name"] for c in sorted_candidates if c["votes"] == top_votes]
        else:
            winner = sorted_candidates[0]

    # Victory margin (difference between first and second)
    margin = 0
    if len(sorted_candidates) >= 2 and not tie:
        margin = sorted_candidates[0]["votes"] - sorted_candidates[1]["votes"]

    # Low participation threshold (e.g., 50%)
    low_participation = participation < 50

    # Build result dictionary
    results = {
        "eligible": eligible,
        "total_valid": total_valid,
        "invalid": invalid,
        "total_votes_cast": total_votes_cast,
        "participation_rate": participation,
        "low_participation": low_participation,
        "sorted_candidates": sorted_candidates,
        "winner": winner,
        "tie": tie,
        "tied_names": tied_names if tie else [],
        "margin": margin
    }
    return results


def display_summary(results):
    """
    Prints a clear summary explaining the outcome.
    """
    print("\n========== ELECTION RESULT SUMMARY ==========\n")

    # Participation
    print(f"Eligible voters: {results['eligible']}")
    print(f"Total votes cast: {results['total_votes_cast']} (Valid: {results['total_valid']}, Invalid: {results['invalid']})")
    print(f"Participation rate: {results['participation_rate']:.2f}%")
    if results['low_participation']:
        print("WARNING: Low participation! Less than 50% of eligible voters cast a vote.")

    # Rankings
    print("\n--- Candidate Rankings ---")
    rank = 1
    for c in results['sorted_candidates']:
        print(f"{rank}. {c['name']}: {c['votes']} votes ({c['percentage']:.2f}%)")
        rank += 1

    # Outcome
    print("\n--- Election Outcome ---")
    if results['tie']:
        tied = ", ".join(results['tied_names'])
        print(f"TIE between: {tied} with {results['sorted_candidates'][0]['votes']} votes each.")
        print("No single winner. A runoff election may be needed.")
    else:
        winner = results['winner']
        print(f"WINNER: {winner['name']} with {winner['votes']} votes ({winner['percentage']:.2f}%)")
        if len(results['sorted_candidates']) >= 2:
            second = results['sorted_candidates'][1]
            print(f"Victory margin over runner-up ({second['name']}): {results['margin']} votes")

    print("\n=============================================\n")


# ------------------------ MAIN PROGRAM ------------------------

def main():
    # Step 1: Input
    eligible, candidates, invalid = get_input()

    # Step 2: Validation
    valid, error = validate_data(eligible, candidates, invalid)
    if not valid:
        print(f"\nERROR: {error}")
        print("Please restart the program with valid data.")
        return

    # Step 3: Calculation
    results = calculate_results(eligible, candidates, invalid)

    # Step 4: Reporting
    display_summary(results)


# Run the program
if __name__ == "__main__":
    main()
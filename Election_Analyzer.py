"""
=============================================================================
COLLEGE ELECTION ANALYZER & DECISION SYSTEM
=============================================================================
A student-friendly Python program demonstrating:
  1. Vote-Entry Logic & Dictionaries
  2. Mathematical Consistency Checks & Validation
  3. Vote Aggregation, Percentages, Sorting & Tie Detection
  4. Cross-Department / Multi-Round Comparison
  5. Outcome-Driven Narrative Reporting
  6. Inbuilt Tkinter Graphical User Interface (GUI)
=============================================================================
"""

import tkinter as tk
from tkinter import messagebox


# =============================================================================
# 1. VOTE-ENTRY LOGIC (Nested Dictionary: {Candidate: {Dept: Votes}})
# =============================================================================
def create_empty_election():
    """Initializes and returns an empty election dictionary."""
    return {}


def add_vote_entry(election_data, candidate, department, votes):
    """
    Stores and updates candidate votes per department or round.
    Uses dictionary lookup and accumulation.
    """
    candidate = candidate.strip()
    department = department.strip()
    if candidate not in election_data:
        election_data[candidate] = {}
    election_data[candidate][department] = election_data[candidate].get(department, 0) + votes


# =============================================================================
# 2. VALIDATION LOGIC (Mathematical Consistency Checks)
# =============================================================================
def validate_election(eligible, valid, invalid, election_data):
    """
    Verifies that all election totals are mathematically possible.
    Returns (is_valid: bool, error_message: str).
    """
    # Rule 1: Non-zero positive eligible voters
    if eligible <= 0:
        return False, "Eligible voters must be greater than zero."

    # Rule 2: Non-negative vote counts
    if valid < 0 or invalid < 0:
        return False, "Vote numbers cannot be negative."

    # Rule 3: Must have candidate data entered
    if not election_data:
        return False, "Please enter at least one candidate vote record."

    # Rule 4: Total ballots cast cannot exceed total eligible voters
    total_cast = valid + invalid
    if total_cast > eligible:
        return False, f"Impossible turnout! Total votes cast ({total_cast}) exceeds eligible voters ({eligible})."

    # Rule 5: Sum of individual candidate votes must exactly balance valid votes
    candidate_sum = 0
    for cand, depts in election_data.items():
        for dept, count in depts.items():
            candidate_sum += count

    if candidate_sum != valid:
        diff = abs(candidate_sum - valid)
        word = "more" if candidate_sum > valid else "fewer"
        return False, f"Vote mismatch! Candidate votes ({candidate_sum}) is {diff} {word} than declared valid votes ({valid})."

    return True, "All mathematical checks passed."


# =============================================================================
# 3. CALCULATION & AGGREGATION LOGIC
# =============================================================================
def calculate_results(eligible, valid, invalid, election_data):
    """
    Calculates candidate rankings, vote share percentages, participation rate,
    victory margins, tie conditions, and departmental leader comparisons.
    """
    # 1. Total votes per candidate using dictionary loop
    candidate_totals = {}
    for cand, depts in election_data.items():
        candidate_totals[cand] = sum(depts.values())

    # 2. Sort candidates descending by total votes (Rankings)
    ranked = sorted(candidate_totals.items(), key=lambda item: item[1], reverse=True)

    # 3. Vote percentage per candidate
    percentages = {cand: round((v / valid) * 100, 2) for cand, v in ranked}

    # 4. Participation rate (Turnout %) and low turnout check (< 50%)
    total_cast = valid + invalid
    participation_rate = round((total_cast / eligible) * 100, 2)
    is_low_participation = participation_rate < 50.0

    # 5. Victory margin & Tie conditions
    top_votes = ranked[0][1]
    tied_leaders = [cand for cand, v in ranked if v == top_votes]
    is_tie = len(tied_leaders) > 1

    if is_tie:
        winner = None
        runner_up = None
        margin_pct = 0.0
        margin_votes = 0
    else:
        winner = ranked[0][0]
        runner_up = ranked[1][0] if len(ranked) > 1 else None
        runner_votes = ranked[1][1] if len(ranked) > 1 else 0
        margin_votes = top_votes - runner_votes
        margin_pct = round((margin_votes / valid) * 100, 2)

    # 6. Compare candidates across multiple departments / rounds
    all_depts = set()
    for depts in election_data.values():
        all_depts.update(depts.keys())

    dept_leaders = {}
    for d in sorted(all_depts):
        dept_scores = {c: depts.get(d, 0) for c, depts in election_data.items()}
        max_dept_vote = max(dept_scores.values())
        leaders = [c for c, v in dept_scores.items() if v == max_dept_vote]
        dept_leaders[d] = (leaders, max_dept_vote)

    return {
        "ranked": ranked,
        "percentages": percentages,
        "participation_rate": participation_rate,
        "is_low_participation": is_low_participation,
        "is_tie": is_tie,
        "tied_leaders": tied_leaders,
        "winner": winner,
        "runner_up": runner_up,
        "margin_votes": margin_votes,
        "margin_pct": margin_pct,
        "dept_leaders": dept_leaders
    }


# =============================================================================
# 4. FINAL REPORTING (Outcome-Focused Narrative Summary)
# =============================================================================
def generate_outcome_summary(res):
    """
    Produces a concise result summary explaining the outcome in plain language
    rather than simply dumping raw vote numbers.
    """
    lines = ["================ ELECTION OUTCOME SUMMARY ================"]

    # Outcome & Margin narrative
    if res["is_tie"]:
        tied_str = " and ".join(res["tied_leaders"])
        share = res["percentages"][res["tied_leaders"][0]]
        lines.append(f"⚖️ OUTCOME: DEAD HEAT / TIE DETECTED")
        lines.append(f"A tie occurred between {tied_str} with identical {share}% vote share.")
        lines.append("Decision: A runoff round is required to determine the winner.")
    else:
        lines.append(f"🏆 OUTCOME: {res['winner'].upper()} ELECTED")
        if res["runner_up"]:
            lines.append(
                f"{res['winner']} won the election with {res['percentages'][res['winner']]}% of the valid votes, "
                f"defeating runner-up {res['runner_up']} by a margin of {res['margin_pct']}% ({res['margin_votes']} votes)."
            )
        else:
            lines.append(f"{res['winner']} ran unopposed, securing 100% of the vote share.")

    # Participation narrative
    if res["is_low_participation"]:
        lines.append(
            f"\n⚠️ PARTICIPATION ALERT: Low student turnout ({res['participation_rate']}%). "
            f"Turnout fell below the 50% benchmark, suggesting voter apathy."
        )
    else:
        lines.append(
            f"\n🗳️ PARTICIPATION: Healthy student turnout ({res['participation_rate']}%). "
            f"Sufficient quorum achieved for representative legitimacy."
        )

    # Department / Round comparison narrative
    lines.append("\n🏛️ DEPARTMENT / ROUND COMPARISON:")
    for dept, (leaders, top_v) in res["dept_leaders"].items():
        leader_names = " & ".join(leaders)
        if len(leaders) > 1:
            lines.append(f"  • {dept}: Tie between {leader_names} ({top_v} votes each)")
        else:
            lines.append(f"  • {dept}: Won by {leader_names} ({top_v} votes)")

    # Final candidate rankings table
    lines.append("\n📊 FINAL RANKINGS:")
    for rank, (cand, votes) in enumerate(res["ranked"], 1):
        lines.append(f"  {rank}. {cand} — {res['percentages'][cand]}% ({votes} votes)")

    lines.append("==========================================================")
    return "\n".join(lines)


# =============================================================================
# 5. INBUILT GUI (Minimal, Clean Tkinter Interface)
# =============================================================================
class ElectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Election Analyzer")
        self.root.geometry("640x660")
        self.root.resizable(False, False)
        self.election_data = create_empty_election()

        # Title Header
        tk.Label(root, text="🎓 College Election Result Analyzer", font=("Arial", 14, "bold"), fg="#1e3a8a").pack(pady=8)

        # 1. Quotas Frame
        frame_q = tk.LabelFrame(root, text=" 1. Election Control Totals ", padx=10, pady=6)
        frame_q.pack(fill="x", padx=12, pady=3)

        self.ent_eligible = self._add_field(frame_q, "Eligible Voters:", 0)
        self.ent_valid = self._add_field(frame_q, "Declared Valid Votes:", 1)
        self.ent_invalid = self._add_field(frame_q, "Invalid / Blank Votes:", 2)

        # 2. Candidate & Department Entry Frame
        frame_e = tk.LabelFrame(root, text=" 2. Candidate Vote Entry (Per Department / Round) ", padx=10, pady=6)
        frame_e.pack(fill="x", padx=12, pady=3)

        self.ent_cand = self._add_field(frame_e, "Candidate Name:", 0)
        self.ent_dept = self._add_field(frame_e, "Department / Round:", 1)
        self.ent_votes = self._add_field(frame_e, "Votes Received:", 2)

        # Entry Control Buttons
        btn_bar = tk.Frame(frame_e)
        btn_bar.grid(row=3, column=0, columnspan=2, pady=6)
        tk.Button(btn_bar, text="➕ Add Entry", command=self.add_entry, bg="#e2e8f0", width=12).pack(side="left", padx=4)
        tk.Button(btn_bar, text="⚡ Load Sample", command=self.load_sample, bg="#fef08a", width=12).pack(side="left", padx=4)
        tk.Button(btn_bar, text="🔄 Clear All", command=self.clear_all, bg="#fee2e2", width=12).pack(side="left", padx=4)

        # Added Records Listbox
        self.lst_entries = tk.Listbox(root, height=4, font=("Consolas", 9))
        self.lst_entries.pack(fill="x", padx=12, pady=3)

        # 3. Analyze Action Button
        tk.Button(
            root, text="📊 Run Election Analysis", command=self.analyze,
            bg="#2563eb", fg="white", font=("Arial", 10, "bold"), pady=4
        ).pack(fill="x", padx=12, pady=5)

        # 4. Result Outcome Summary Box
        self.txt_result = tk.Text(root, height=13, font=("Consolas", 9), padx=8, pady=8, bg="#f8fafc", relief="solid", bd=1)
        self.txt_result.pack(fill="both", expand=True, padx=12, pady=6)
        self.txt_result.insert("1.0", "Click 'Load Sample' or enter values, then click 'Run Election Analysis'.")
        self.txt_result.config(state="disabled")

    def _add_field(self, parent, label_text, row):
        tk.Label(parent, text=label_text).grid(row=row, column=0, sticky="w", pady=2)
        ent = tk.Entry(parent, width=28)
        ent.grid(row=row, column=1, sticky="e", pady=2)
        return ent

    def add_entry(self):
        c, d, v = self.ent_cand.get().strip(), self.ent_dept.get().strip(), self.ent_votes.get().strip()
        if not c or not d or not v.isdigit():
            messagebox.showerror("Input Error", "Please provide Candidate, Department/Round, and non-negative Votes.")
            return

        add_vote_entry(self.election_data, c, d, int(v))
        self.lst_entries.insert(tk.END, f"{c:15} | {d:15} | {v:>4} votes")
        self.ent_cand.delete(0, tk.END)
        self.ent_dept.delete(0, tk.END)
        self.ent_votes.delete(0, tk.END)

    def load_sample(self):
        """Loads realistic sample college election data across 3 departments."""
        self.clear_all()
        self.ent_eligible.insert(0, "1000")
        self.ent_valid.insert(0, "750")
        self.ent_invalid.insert(0, "30")

        samples = [
            ("Aarav", "Engineering", 150), ("Aarav", "Commerce", 100), ("Aarav", "Arts", 110),
            ("Priya", "Engineering", 110), ("Priya", "Commerce", 160), ("Priya", "Arts", 120)
        ]
        for c, d, v in samples:
            add_vote_entry(self.election_data, c, d, v)
            self.lst_entries.insert(tk.END, f"{c:15} | {d:15} | {v:>4} votes")

    def clear_all(self):
        self.election_data.clear()
        self.lst_entries.delete(0, tk.END)
        for ent in (self.ent_eligible, self.ent_valid, self.ent_invalid, self.ent_cand, self.ent_dept, self.ent_votes):
            ent.delete(0, tk.END)
        self.txt_result.config(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.config(state="disabled")

    def analyze(self):
        """Validates, calculates, and prints outcome summary."""
        try:
            el = int(self.ent_eligible.get().strip())
            va = int(self.ent_valid.get().strip())
            inv = int(self.ent_invalid.get().strip())
        except ValueError:
            messagebox.showerror("Input Error", "Eligible, Valid, and Invalid counts must be valid integers.")
            return

        is_valid, msg = validate_election(el, va, inv, self.election_data)
        if not is_valid:
            messagebox.showerror("Validation Failed", msg)
            return

        res = calculate_results(el, va, inv, self.election_data)
        summary = generate_outcome_summary(res)

        self.txt_result.config(state="normal")
        self.txt_result.delete("1.0", tk.END)
        self.txt_result.insert("1.0", summary)
        self.txt_result.config(state="disabled")


# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    app_root = tk.Tk()
    app = ElectionApp(app_root)
    app_root.mainloop()
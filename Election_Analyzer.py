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
  6. Interactive Tkinter Graphical User Interface (GUI)
=============================================================================
"""

import tkinter as tk
from tkinter import ttk, messagebox


# =============================================================================
# MODULE 1: VOTE-ENTRY LOGIC & DATA STRUCTURES
# =============================================================================
# We store candidate votes per department using a nested dictionary:
# {
#     "Candidate Name": {"Department Name": vote_count, ...}
# }

def create_empty_election():
    """Returns a new, empty dictionary to store election records."""
    return {}


def add_vote_entry(election_records, candidate_name, department, votes):
    """
    Adds or updates vote counts for a candidate within a specific department.
    Uses dictionary lookup and accumulation.
    """
    candidate_name = candidate_name.strip()
    department = department.strip()

    if candidate_name not in election_records:
        election_records[candidate_name] = {}

    current_votes = election_records[candidate_name].get(department, 0)
    election_records[candidate_name][department] = current_votes + votes


# =============================================================================
# MODULE 2: VALIDATION LOGIC (Mathematical Consistency Checks)
# =============================================================================
def validate_election_data(eligible_voters, declared_valid_votes, invalid_votes, election_records):
    """
    Performs rigorous mathematical checks on election figures:
      1. Eligible voters must be strictly positive.
      2. Valid and invalid votes cannot be negative.
      3. At least one candidate must be entered.
      4. Sum of all candidate votes must EXACTLY equal declared valid votes.
      5. Total ballots cast (valid + invalid) cannot exceed eligible voters.

    Returns: (is_valid: bool, error_message: str, check_details: dict)
    """
    details = {}

    # Check 1: Basic numeric feasibility
    if eligible_voters <= 0:
        return False, "Eligible voters must be greater than zero.", details

    if declared_valid_votes < 0 or invalid_votes < 0:
        return False, "Vote counts cannot be negative numbers.", details

    if not election_records:
        return False, "Please add at least one candidate record before analyzing.", details

    # Calculate actual candidate vote sum using nested loops
    actual_candidate_sum = 0
    for candidate, depts in election_records.items():
        for dept, count in depts.items():
            actual_candidate_sum += count

    total_cast = declared_valid_votes + invalid_votes

    # Record check values for the report
    details["actual_candidate_sum"] = actual_candidate_sum
    details["declared_valid_votes"] = declared_valid_votes
    details["invalid_votes"] = invalid_votes
    details["total_cast"] = total_cast
    details["eligible_voters"] = eligible_voters

    # Check 2: Candidate votes sum vs declared valid votes
    if actual_candidate_sum != declared_valid_votes:
        diff = actual_candidate_sum - declared_valid_votes
        direction = "more" if diff > 0 else "fewer"
        msg = (
            f"Mathematical Inconsistency Detected!\n"
            f"The sum of all candidate votes ({actual_candidate_sum}) is {abs(diff)} votes "
            f"{direction} than the declared Valid Votes total ({declared_valid_votes}).\n"
            f"Votes must balance exactly."
        )
        return False, msg, details

    # Check 3: Total cast cannot exceed eligible voters
    if total_cast > eligible_voters:
        surplus = total_cast - eligible_voters
        msg = (
            f"Mathematically Impossible Total!\n"
            f"Total votes cast ({total_cast} = {declared_valid_votes} valid + {invalid_votes} invalid) "
            f"exceeds the eligible voters list ({eligible_voters}) by {surplus} ballots."
        )
        return False, msg, details

    return True, "All mathematical consistency checks passed.", details


# =============================================================================
# MODULE 3: CALCULATION & AGGREGATION LOGIC
# =============================================================================
def calculate_election_results(eligible_voters, declared_valid_votes, invalid_votes, election_records):
    """
    Aggregates votes, calculates percentages, rankings, victory margin,
    tie conditions, and cross-department comparisons.
    """
    # 1. Candidate Total Votes using loops over the nested dictionary
    candidate_totals = {}
    for candidate, depts in election_records.items():
        total = 0
        for dept, votes in depts.items():
            total += votes
        candidate_totals[candidate] = total

    # 2. Rankings: Sort candidates descending by total votes
    ranked_candidates = sorted(candidate_totals.items(), key=lambda item: item[1], reverse=True)

    # 3. Calculate vote percentages for each candidate
    candidate_percentages = {}
    for candidate, votes in ranked_candidates:
        pct = (votes / declared_valid_votes * 100) if declared_valid_votes > 0 else 0.0
        candidate_percentages[candidate] = round(pct, 2)

    # 4. Turnout (Participation Rate)
    total_cast = declared_valid_votes + invalid_votes
    participation_rate = round((total_cast / eligible_voters * 100), 2)
    is_low_participation = participation_rate < 50.0

    # 5. Victory Margin & Tie Conditions
    top_votes = ranked_candidates[0][1]
    # Check if multiple candidates share the #1 spot
    tied_for_first = [cand for cand, votes in ranked_candidates if votes == top_votes]
    is_tie = len(tied_for_first) > 1

    if is_tie:
        winner = None
        runner_up = None
        margin_votes = 0
        margin_pct = 0.0
    else:
        winner = ranked_candidates[0][0]
        runner_up = ranked_candidates[1][0] if len(ranked_candidates) > 1 else None
        runner_up_votes = ranked_candidates[1][1] if len(ranked_candidates) > 1 else 0
        margin_votes = top_votes - runner_up_votes
        margin_pct = round((margin_votes / declared_valid_votes * 100), 2) if declared_valid_votes > 0 else 0.0

    # 6. Cross-Department / Multi-Round Comparison
    # Collect all unique departments
    all_departments = set()
    for depts in election_records.values():
        all_departments.update(depts.keys())

    department_summary = {}
    for dept in sorted(all_departments):
        # Tally candidate votes in this specific department
        dept_scores = {}
        dept_total_votes = 0
        for cand, depts in election_records.items():
            votes_in_dept = depts.get(dept, 0)
            dept_scores[cand] = votes_in_dept
            dept_total_votes += votes_in_dept

        # Sort to find department leader
        sorted_dept = sorted(dept_scores.items(), key=lambda x: x[1], reverse=True)
        dept_top_votes = sorted_dept[0][1] if sorted_dept else 0
        dept_leaders = [c for c, v in sorted_dept if v == dept_top_votes]

        dept_summary[dept] = {
            "total_votes": dept_total_votes,
            "leaders": dept_leaders,
            "leader_votes": dept_top_votes,
            "is_dept_tie": len(dept_leaders) > 1,
            "scores": dept_scores
        }

    return {
        "ranked_candidates": ranked_candidates,
        "candidate_percentages": candidate_percentages,
        "participation_rate": participation_rate,
        "is_low_participation": is_low_participation,
        "is_tie": is_tie,
        "tied_for_first": tied_for_first,
        "winner": winner,
        "runner_up": runner_up,
        "margin_votes": margin_votes,
        "margin_pct": margin_pct,
        "department_summary": department_summary,
        "total_cast": total_cast,
        "declared_valid_votes": declared_valid_votes,
        "invalid_votes": invalid_votes,
        "eligible_voters": eligible_voters
    }


# =============================================================================
# MODULE 4: FINAL REPORTING (Outcome-Focused Narrative Summary)
# =============================================================================
def generate_outcome_summary(results):
    """
    Produces a concise result summary explaining the outcome in easy English
    instead of just printing raw numbers.
    """
    lines = []

    # 1. Election Outcome Narrative
    if results["is_tie"]:
        tied_names = " and ".join(results["tied_for_first"])
        top_share = results["candidate_percentages"][results["tied_for_first"][0]]
        lines.append("⚖️ OUTCOME: DEAD HEAT / TIE DETECTED")
        lines.append(
            f"The election concluded without a single winner because {tied_names} "
            f"secured an identical vote share of {top_share}%. "
            f"Under campus election bylaws, a run-off round is required between the tied candidates."
        )
    else:
        winner = results["winner"]
        win_share = results["candidate_percentages"][winner]
        margin_pct = results["margin_pct"]
        margin_votes = results["margin_votes"]

        if margin_pct >= 15.0:
            margin_desc = "a commanding landslide lead"
        elif margin_pct >= 6.0:
            margin_desc = "a decisive victory margin"
        else:
            margin_desc = "a razor-thin victory margin"

        lines.append(f"🏆 OUTCOME: {winner.upper()} ELECTED")
        if results["runner_up"]:
            runner_up = results["runner_up"]
            ru_share = results["candidate_percentages"][runner_up]
            lines.append(
                f"{winner} has won the election with {win_share}% of the valid vote, "
                f"establishing {margin_desc} of {margin_pct}% ({margin_votes} votes) "
                f"over runner-up {runner_up} ({ru_share}%)."
            )
        else:
            lines.append(f"{winner} ran unopposed, capturing 100% of the vote share.")

    lines.append("")

    # 2. Participation / Turnout Narrative
    turnout = results["participation_rate"]
    if results["is_low_participation"]:
        lines.append("⚠️ LOW PARTICIPATION ALERT:")
        lines.append(
            f"Campus voter participation was critically low at {turnout}% (under the 50% benchmark). "
            f"Because fewer than half of eligible students cast ballots, the student council "
            f"should investigate voter apathy or lack of election awareness."
        )
    else:
        lines.append("🗳️ PARTICIPATION EVALUATION:")
        lines.append(
            f"Campus engagement was healthy with a robust turnout of {turnout}%. "
            f"This confirms strong quorum and provides the incoming representative a legitimate mandate."
        )

    lines.append("")

    # 3. Departmental Comparison Narrative
    lines.append("🏛️ DEPARTMENTAL DYNAMICS:")
    dept_insights = []
    for dept, info in results["department_summary"].items():
        if info["is_dept_tie"]:
            leaders_str = " & ".join(info["leaders"])
            dept_insights.append(f"• {dept}: Dead heat between {leaders_str} ({info['leader_votes']} votes each).")
        else:
            leader = info["leaders"][0]
            share = round((info["leader_votes"] / info["total_votes"] * 100), 1) if info["total_votes"] > 0 else 0
            dept_insights.append(f"• {dept}: Won by {leader} with {share}% of the department's ballots.")

    lines.extend(dept_insights)

    return "\n".join(lines)


# =============================================================================
# MODULE 5: INTERACTIVE GRAPHICAL USER INTERFACE (Tkinter GUI)
# =============================================================================
class CollegeElectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("College Election Result Analyzer & Decision System")
        self.root.geometry("980x720")
        self.root.minsize(920, 640)

        # In-memory election data dictionary: {candidate: {dept: votes}}
        self.election_data = create_empty_election()

        # Build styles
        self._setup_styles()
        # Build UI layout
        self._build_ui()

    def _setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Configure nice fonts & colors
        style.configure(".", font=("Segoe UI", 9))
        style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"), foreground="#1e293b")
        style.configure("SubHeader.TLabel", font=("Segoe UI", 10, "bold"), foreground="#334155")
        style.configure("CardTitle.TLabel", font=("Segoe UI", 10, "bold"), foreground="#0f172a")

        style.configure("Action.TButton", font=("Segoe UI", 9, "bold"), padding=5)
        style.configure("Primary.TButton", background="#2563eb", foreground="#ffffff")
        style.map("Primary.TButton", background=[("active", "#1d4ed8")])

        style.configure("Success.TButton", background="#16a34a", foreground="#ffffff")
        style.map("Success.TButton", background=[("active", "#15803d")])

        style.configure("Demo.TButton", background="#f59e0b", foreground="#ffffff")
        style.map("Demo.TButton", background=[("active", "#d97706")])

    def _build_ui(self):
        # Header banner
        header_frame = tk.Frame(self.root, bg="#1e293b", padx=16, pady=12)
        header_frame.pack(fill="x")

        title = tk.Label(
            header_frame,
            text="🎓 College Election Result Analyzer",
            font=("Segoe UI", 16, "bold"),
            fg="#ffffff",
            bg="#1e293b"
        )
        title.pack(anchor="w")

        subtitle = tk.Label(
            header_frame,
            text="Validation, Aggregation, Cross-Department Comparison & Outcome Analysis",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#1e293b"
        )
        subtitle.pack(anchor="w")

        # Main split container
        main_paned = ttk.PanedWindow(self.root, orient="horizontal")
        main_paned.pack(fill="both", expand=True, padx=12, pady=10)

        # ---------------- LEFT PANEL: Inputs & Management ----------------
        left_frame = ttk.Frame(main_paned, padding=8)
        main_paned.add(left_frame, weight=4)

        # 1. Total Quotas Box
        quota_group = ttk.LabelFrame(left_frame, text=" 1. Election Control Totals ", padding=10)
        quota_group.pack(fill="x", pady=4)

        ttk.Label(quota_group, text="Eligible Voters:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_eligible = ttk.Entry(quota_group, width=14)
        self.entry_eligible.grid(row=0, column=1, sticky="e", pady=3)

        ttk.Label(quota_group, text="Declared Valid Votes:").grid(row=1, column=0, sticky="w", pady=3)
        self.entry_valid = ttk.Entry(quota_group, width=14)
        self.entry_valid.grid(row=1, column=1, sticky="e", pady=3)

        ttk.Label(quota_group, text="Invalid / Blank Votes:").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_invalid = ttk.Entry(quota_group, width=14)
        self.entry_invalid.grid(row=2, column=1, sticky="e", pady=3)

        # 2. Candidate & Department Entry Box
        cand_group = ttk.LabelFrame(left_frame, text=" 2. Candidate & Department Votes ", padding=10)
        cand_group.pack(fill="x", pady=6)

        ttk.Label(cand_group, text="Candidate Name:").grid(row=0, column=0, sticky="w", pady=3)
        self.entry_candidate = ttk.Entry(cand_group, width=18)
        self.entry_candidate.grid(row=0, column=1, sticky="ew", pady=3)

        ttk.Label(cand_group, text="Department / Round:").grid(row=1, column=0, sticky="w", pady=3)
        self.combo_dept = ttk.Combobox(
            cand_group,
            values=["Engineering", "Arts & Humanities", "Commerce", "Science", "Round 1", "Round 2"],
            width=16
        )
        self.combo_dept.set("Engineering")
        self.combo_dept.grid(row=1, column=1, sticky="ew", pady=3)

        ttk.Label(cand_group, text="Votes Received:").grid(row=2, column=0, sticky="w", pady=3)
        self.entry_votes = ttk.Entry(cand_group, width=18)
        self.entry_votes.grid(row=2, column=1, sticky="ew", pady=3)

        btn_add = ttk.Button(cand_group, text="➕ Add / Update Entry", command=self.add_entry)
        btn_add.grid(row=3, column=0, columnspan=2, sticky="ew", pady=6)

        # 3. Entries Table (Treeview)
        list_group = ttk.LabelFrame(left_frame, text=" Entered Vote Records ", padding=6)
        list_group.pack(fill="both", expand=True, pady=4)

        columns = ("candidate", "department", "votes")
        self.tree_entries = ttk.Treeview(list_group, columns=columns, show="headings", height=6)
        self.tree_entries.heading("candidate", text="Candidate")
        self.tree_entries.heading("department", text="Department / Round")
        self.tree_entries.heading("votes", text="Votes")

        self.tree_entries.column("candidate", width=120)
        self.tree_entries.column("department", width=120)
        self.tree_entries.column("votes", width=60, anchor="center")

        tree_scroll = ttk.Scrollbar(list_group, orient="vertical", command=self.tree_entries.yview)
        self.tree_entries.configure(yscrollcommand=tree_scroll.set)

        self.tree_entries.pack(side="left", fill="both", expand=True)
        tree_scroll.pack(side="right", fill="y")

        btn_remove = ttk.Button(left_frame, text="🗑️ Remove Selected Entry", command=self.remove_entry)
        btn_remove.pack(fill="x", pady=2)

        # Action Buttons
        btn_frame = ttk.Frame(left_frame, padding=4)
        btn_frame.pack(fill="x", pady=6)

        btn_demo = ttk.Button(btn_frame, text="⚡ Load Demo Data", command=self.load_demo_data)
        btn_demo.pack(fill="x", pady=2)

        btn_calc = ttk.Button(btn_frame, text="📊 Run Election Analysis", command=self.analyze_election)
        btn_calc.pack(fill="x", pady=2)

        btn_reset = ttk.Button(btn_frame, text="🔄 Reset All Fields", command=self.reset_all)
        btn_reset.pack(fill="x", pady=2)

        # ---------------- RIGHT PANEL: Results & Reporting ----------------
        right_frame = ttk.Frame(main_paned, padding=8)
        main_paned.add(right_frame, weight=6)

        # Notebook (Tabs) for Results
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill="both", expand=True)

        # Tab 1: Narrative Summary (Explains outcome without raw counts)
        self.tab_summary = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_summary, text="📝 Outcome Narrative")

        ttk.Label(
            self.tab_summary,
            text="Executive Outcome Summary (Natural Language)",
            style="CardTitle.TLabel"
        ).pack(anchor="w", pady=(0, 6))

        self.txt_summary = tk.Text(
            self.tab_summary,
            wrap="word",
            font=("Segoe UI", 10),
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
            bg="#f8fafc"
        )
        self.txt_summary.pack(fill="both", expand=True)
        self.txt_summary.insert("1.0", "Click 'Run Election Analysis' or 'Load Demo Data' to view the outcome summary.")
        self.txt_summary.config(state="disabled")

        # Tab 2: Rankings & Percentage Share
        self.tab_ranks = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_ranks, text="🏆 Rankings & Vote Shares")

        self.tree_ranks = ttk.Treeview(
            self.tab_ranks,
            columns=("rank", "candidate", "votes", "share", "status"),
            show="headings",
            height=8
        )
        self.tree_ranks.heading("rank", text="Rank")
        self.tree_ranks.heading("candidate", text="Candidate")
        self.tree_ranks.heading("votes", text="Total Votes")
        self.tree_ranks.heading("share", text="Vote Share (%)")
        self.tree_ranks.heading("status", text="Outcome Status")

        self.tree_ranks.column("rank", width=50, anchor="center")
        self.tree_ranks.column("candidate", width=140)
        self.tree_ranks.column("votes", width=80, anchor="center")
        self.tree_ranks.column("share", width=90, anchor="center")
        self.tree_ranks.column("status", width=130)
        self.tree_ranks.pack(fill="both", expand=True)

        # Tab 3: Department Breakdown
        self.tab_dept = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_dept, text="🏛️ Department Breakdown")

        self.tree_dept = ttk.Treeview(
            self.tab_dept,
            columns=("dept", "winner", "votes", "total", "dominance"),
            show="headings",
            height=8
        )
        self.tree_dept.heading("dept", text="Department / Round")
        self.tree_dept.heading("winner", text="Department Winner")
        self.tree_dept.heading("votes", text="Winner Votes")
        self.tree_dept.heading("total", text="Total Cast")
        self.tree_dept.heading("dominance", text="Winner Share")

        self.tree_dept.column("dept", width=130)
        self.tree_dept.column("winner", width=130)
        self.tree_dept.column("votes", width=80, anchor="center")
        self.tree_dept.column("total", width=80, anchor="center")
        self.tree_dept.column("dominance", width=90, anchor="center")
        self.tree_dept.pack(fill="both", expand=True)

        # Tab 4: Validation & Math Audit
        self.tab_audit = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_audit, text="🔍 Mathematical Audit")

        self.txt_audit = tk.Text(
            self.tab_audit,
            wrap="word",
            font=("Consolas", 9),
            padx=10,
            pady=10,
            relief="solid",
            borderwidth=1,
            bg="#f1f5f9"
        )
        self.txt_audit.pack(fill="both", expand=True)
        self.txt_audit.insert("1.0", "Mathematical verification report will appear here.")
        self.txt_audit.config(state="disabled")

    # ---------------- GUI Event Handlers ----------------

    def add_entry(self):
        cand = self.entry_candidate.get().strip()
        dept = self.combo_dept.get().strip()
        votes_str = self.entry_votes.get().strip()

        if not cand:
            messagebox.showerror("Input Error", "Please provide a candidate name.")
            return

        if not dept:
            messagebox.showerror("Input Error", "Please specify a department or round.")
            return

        if not votes_str.isdigit():
            messagebox.showerror("Input Error", "Votes must be a non-negative whole number.")
            return

        votes = int(votes_str)
        add_vote_entry(self.election_data, cand, dept, votes)

        # Update Treeview
        self._refresh_entries_tree()

        # Clear inputs
        self.entry_candidate.delete(0, tk.END)
        self.entry_votes.delete(0, tk.END)

    def remove_entry(self):
        selected = self.tree_entries.selection()
        if not selected:
            messagebox.showinfo("Select Item", "Please select a row in the table to remove.")
            return

        for item_id in selected:
            values = self.tree_entries.item(item_id, "values")
            cand, dept = values[0], values[1]
            if cand in self.election_data and dept in self.election_data[cand]:
                del self.election_data[cand][dept]
                if not self.election_data[cand]:
                    del self.election_data[cand]

        self._refresh_entries_tree()

    def _refresh_entries_tree(self):
        for item in self.tree_entries.get_children():
            self.tree_entries.delete(item)

        for cand, depts in self.election_data.items():
            for dept, count in depts.items():
                self.tree_entries.insert("", tk.END, values=(cand, dept, count))

    def load_demo_data(self):
        """Loads realistic sample college election data across 3 departments."""
        self.reset_all()

        self.entry_eligible.insert(0, "1000")
        self.entry_valid.insert(0, "750")
        self.entry_invalid.insert(0, "30")

        demo_votes = [
            ("Aarav Sharma", "Engineering", 150),
            ("Aarav Sharma", "Commerce", 100),
            ("Aarav Sharma", "Arts & Humanities", 110),
            ("Priya Patel", "Engineering", 110),
            ("Priya Patel", "Commerce", 160),
            ("Priya Patel", "Arts & Humanities", 120),
        ]

        for cand, dept, count in demo_votes:
            add_vote_entry(self.election_data, cand, dept, count)

        self._refresh_entries_tree()
        messagebox.showinfo("Demo Loaded", "College election demo data loaded successfully! Click 'Run Election Analysis'.")

    def reset_all(self):
        self.election_data.clear()
        self._refresh_entries_tree()

        self.entry_eligible.delete(0, tk.END)
        self.entry_valid.delete(0, tk.END)
        self.entry_invalid.delete(0, tk.END)
        self.entry_candidate.delete(0, tk.END)
        self.entry_votes.delete(0, tk.END)

        for tree in (self.tree_ranks, self.tree_dept):
            for row in tree.get_children():
                tree.delete(row)

        self._set_text(self.txt_summary, "Click 'Run Election Analysis' to view outcome summary.")
        self._set_text(self.txt_audit, "Mathematical audit log will appear here.")

    def _set_text(self, widget, text):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)
        widget.insert("1.0", text)
        widget.config(state="disabled")

    def analyze_election(self):
        """Validates, calculates, and updates all report tabs."""
        # 1. Parse quotas
        e_str = self.entry_eligible.get().strip()
        v_str = self.entry_valid.get().strip()
        i_str = self.entry_invalid.get().strip()

        if not (e_str.isdigit() and v_str.isdigit() and i_str.isdigit()):
            messagebox.showerror(
                "Input Error",
                "Eligible Voters, Valid Votes, and Invalid Votes must all be valid whole numbers."
            )
            return

        eligible = int(e_str)
        valid = int(v_str)
        invalid = int(i_str)

        # 2. Mathematical Validation & Consistency Check
        is_valid, msg, audit_details = validate_election_data(eligible, valid, invalid, self.election_data)

        # Update audit tab regardless of pass/fail
        self._update_audit_tab(is_valid, msg, audit_details)

        if not is_valid:
            messagebox.showerror("Mathematical Verification Failed", msg)
            self.notebook.select(self.tab_audit)
            return

        # 3. Calculation & Aggregation
        results = calculate_election_results(eligible, valid, invalid, self.election_data)

        # 4. Narrative Summary
        summary_text = generate_outcome_summary(results)
        self._set_text(self.txt_summary, summary_text)

        # 5. Populate Rankings Tab
        for row in self.tree_ranks.get_children():
            self.tree_ranks.delete(row)

        for rank, (cand, votes) in enumerate(results["ranked_candidates"], 1):
            share = results["candidate_percentages"][cand]
            if results["is_tie"] and cand in results["tied_for_first"]:
                status = "Tie (1st Place)"
            elif rank == 1:
                status = "Winner"
            elif rank == 2:
                status = "Runner-Up"
            else:
                status = f"Rank {rank}"

            self.tree_ranks.insert("", tk.END, values=(rank, cand, votes, f"{share}%", status))

        # 6. Populate Department Tab
        for row in self.tree_dept.get_children():
            self.tree_dept.delete(row)

        for dept, info in results["department_summary"].items():
            leaders = ", ".join(info["leaders"])
            share = round((info["leader_votes"] / info["total_votes"] * 100), 1) if info["total_votes"] > 0 else 0
            self.tree_dept.insert("", tk.END, values=(dept, leaders, info["leader_votes"], info["total_votes"], f"{share}%"))

        # Switch to summary tab
        self.notebook.select(self.tab_summary)
        messagebox.showinfo("Analysis Complete", "Election analysis completed successfully!")

    def _update_audit_tab(self, is_valid, msg, details):
        audit_lines = [
            "============================================================",
            "             MATHEMATICAL CONSISTENCY AUDIT LOG",
            "============================================================",
            f"Overall Status: {'PASSED ✓' if is_valid else 'FAILED ✗'}",
            f"Audit Message : {msg}",
            "------------------------------------------------------------",
        ]
        if details:
            audit_lines.extend([
                f"• Registered Eligible Voters : {details.get('eligible_voters')}",
                f"• Declared Valid Votes       : {details.get('declared_valid_votes')}",
                f"• Sum of Candidate Votes     : {details.get('actual_candidate_sum')}",
                f"  -> Match Check             : {'BALANCED ✓' if details.get('actual_candidate_sum') == details.get('declared_valid_votes') else 'MISMATCH ✗'}",
                f"• Invalid / Blank Ballots    : {details.get('invalid_votes')}",
                f"• Total Ballots Cast         : {details.get('total_cast')} (Valid + Invalid)",
                f"  -> Capacity Check          : {'WITHIN ELIGIBLE LIMIT ✓' if details.get('total_cast') <= details.get('eligible_voters') else 'EXCEEDS CAPACITY ✗'}",
                "============================================================"
            ])
        self._set_text(self.txt_audit, "\n".join(audit_lines))


# =============================================================================
# PROGRAM ENTRY POINT
# =============================================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = CollegeElectionApp(root)
    root.mainloop()
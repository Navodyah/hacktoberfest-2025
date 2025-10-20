import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
import webbrowser
import os
from Contribute_Checker import ProjectTracker
from Contribute_Checker.metrics_visualizer import MetricsVisualizer

class HacktoberfestDesktopUI:
    def __init__(self):
        self.tracker = ProjectTracker()
        self.setup_window()
        self.create_menu()
        self.create_notebook()
        self.load_initial_data()

    def setup_window(self):
        self.root = tk.Tk()
        self.root.title("Hacktoberfest 2025 Tracker")
        self.root.geometry("900x600")
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure("Title.TLabel", font=("Helvetica", 16, "bold"))
        self.style.configure("Header.TLabel", font=("Helvetica", 12, "bold"))
        self.style.configure("Stats.TLabel", font=("Helvetica", 10))
        # Primary button style (modern blue)
        # Note: ttk on Windows uses native theme; to ensure color works we'll set relief and focuscolor where supported
        primary_bg = "#1f6feb"
        primary_fg = "#ffffff"
        self.style.configure("Primary.TButton",
                             background=primary_bg,
                             foreground=primary_fg,
                             relief="flat",
                             padding=6)
        # Map active and pressed states to slightly different shades
        self.style.map("Primary.TButton",
                       background=[('active', '#155ed1'), ('pressed', '#134fb3')],
                       foreground=[('disabled', '#dddddd')])
        
    def create_menu(self):
        from menu_system import MenuSystem
        self.menu_system = MenuSystem(self.root, self.tracker)

    def create_notebook(self):
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.dashboard_tab = ttk.Frame(self.notebook)
        self.contributors_tab = ttk.Frame(self.notebook)
        self.leaderboard_tab = ttk.Frame(self.notebook)
        self.add_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.dashboard_tab, text="Dashboard")
        self.notebook.add(self.contributors_tab, text="Contributors")
        self.notebook.add(self.leaderboard_tab, text="Leaderboard")
        self.notebook.add(self.add_tab, text="Add New")
        
        self.setup_dashboard()
        self.setup_contributors_view()
        self.setup_leaderboard()
        self.setup_add_forms()

    def setup_dashboard(self):
        # Main container with padding
        main_frame = ttk.Frame(self.dashboard_tab, padding="10 5 10 10")
        main_frame.pack(fill='both', expand=True)

        # Welcome message with current date
        welcome_frame = ttk.Frame(main_frame)
        welcome_frame.pack(fill='x', pady=(0, 10))
        
        welcome_msg = ttk.Label(
            welcome_frame,
            text="Hacktoberfest 2025",
            style="Title.TLabel"
        )
        welcome_msg.pack(side='left')
        
        date_label = ttk.Label(
            welcome_frame,
            text=datetime.now().strftime("%B %d, %Y"),
            style="Stats.TLabel"
        )
        date_label.pack(side='right')

        # Stats cards in a row
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=(0, 10))
        
        # Configure styles for stats cards
        self.style.configure(
            "Card.TFrame",
            background="#f6f8fa",
            relief="solid",
            borderwidth=1
        )
        
        # Create metric cards
        self.stats_vars = {
            'contributors': tk.StringVar(value="0"),
            'contributions': tk.StringVar(value="0"),
            'completion': tk.StringVar(value="0%")
        }
        
        # Metric cards with icons
        cards_data = [
            ("👥", "Contributors", 'contributors'),
            ("📝", "Contributions", 'contributions'),
            ("🎯", "Completion", 'completion')
        ]
        
        for i, (icon, label, var_key) in enumerate(cards_data):
            card = ttk.Frame(stats_frame, style="Card.TFrame")
            card.grid(row=0, column=i, padx=5, sticky='nsew')
            stats_frame.grid_columnconfigure(i, weight=1)
            
            ttk.Label(
                card,
                text=f"{icon} {label}",
                style="Header.TLabel"
            ).pack(pady=(8, 2))
            
            ttk.Label(
                card,
                textvariable=self.stats_vars[var_key],
                style="Stats.TLabel"
            ).pack(pady=(0, 8))
        
        # Recent activity (small size)
        activity_frame = ttk.LabelFrame(main_frame, text="Recent Activity")
        activity_frame.pack(fill='both', expand=True)
        
        # Compact activity list
        self.activity_tree = ttk.Treeview(
            activity_frame,
            columns=("Time", "Activity"),
            show="headings",
            height=5  # Show only 5 rows
        )
        
        # Configure columns
        self.activity_tree.heading("Time", text="Time")
        self.activity_tree.heading("Activity", text="Activity")
        
        self.activity_tree.column("Time", width=100)
        self.activity_tree.column("Activity", width=300)
        
        scrollbar = ttk.Scrollbar(
            activity_frame,
            orient="vertical",
            command=self.activity_tree.yview
        )
        self.activity_tree.configure(yscrollcommand=scrollbar.set)
        
        self.activity_tree.pack(side='left', fill='both', expand=True, padx=(5, 0), pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)

    def setup_contributors_view(self):
        # Search frame
        search_frame = ttk.Frame(self.contributors_tab)
        search_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side='left', padx=5)
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.filter_contributors)
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side='left', fill='x', expand=True, padx=5)
        
        # Contributors list
        self.contributors_tree = ttk.Treeview(
            self.contributors_tab,
            columns=("Username", "Name", "Email", "Contributions", "Status"),
            show="headings"
        )
        
        self.contributors_tree.heading("Username", text="Username")
        self.contributors_tree.heading("Name", text="Name")
        self.contributors_tree.heading("Email", text="Email")
        self.contributors_tree.heading("Contributions", text="Contributions")
        self.contributors_tree.heading("Status", text="Status")
        
        scrollbar = ttk.Scrollbar(
            self.contributors_tab,
            orient="vertical",
            command=self.contributors_tree.yview
        )
        self.contributors_tree.configure(yscrollcommand=scrollbar.set)
        
        self.contributors_tree.pack(side='left', fill='both', expand=True, padx=10, pady=5)
        scrollbar.pack(side='right', fill='y')
        
        self.contributors_tree.bind('<Double-1>', self.show_contributor_details)

    def setup_leaderboard(self):
        # Main container
        main_frame = ttk.Frame(self.leaderboard_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Header frame with title and controls
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=(5, 15))
        
        # Title with trophy emoji
        title = ttk.Label(
            header_frame,
            text="🏆 Hacktoberfest Champions",
            style="Title.TLabel"
        )
        title.pack(side='left', pady=10)
        
        # Sort controls
        sort_frame = ttk.Frame(header_frame)
        sort_frame.pack(side='right', pady=10)
        
        ttk.Label(sort_frame, text="Sort by:").pack(side='left', padx=(0, 5))
        self.sort_var = tk.StringVar(value="score")
        sort_combo = ttk.Combobox(
            sort_frame,
            textvariable=self.sort_var,
            values=["score", "streak", "contributions"],
            width=12,
            state="readonly"
        )
        sort_combo.pack(side='left')
        sort_combo.bind('<<ComboboxSelected>>', self.sort_leaderboard)
        
        # Stats cards frame
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Configure stats card style
        self.style.configure(
            "Stats.TFrame",
            background="#f6f8fa",
            relief="solid",
            borderwidth=1
        )
        
        # Add stat cards
        self.top_contributor_var = tk.StringVar(value="Loading...")
        self.longest_streak_var = tk.StringVar(value="Loading...")
        self.most_badges_var = tk.StringVar(value="Loading...")
        
        self.create_stat_card(
            stats_frame,
            "👑 Top Contributor",
            self.top_contributor_var,
            0
        )
        self.create_stat_card(
            stats_frame,
            "🔥 Longest Streak",
            self.longest_streak_var,
            1
        )
        self.create_stat_card(
            stats_frame,
            "🎖️ Most Badges",
            self.most_badges_var,
            2
        )
        
        # Enhanced leaderboard table
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill='both', expand=True)
        
        # Leaderboard table with more columns
        self.leaderboard_tree = ttk.Treeview(
            table_frame,
            columns=(
                "Rank",
                "Username",
                "Score",
                "Contributions",
                "Streak",
                "Active Days",
                "Badges"
            ),
            show="headings",
            selectmode="browse"
        )
        
        # Configure column headings and widths
        columns = [
            ("Rank", "#", 50),
            ("Username", "Username", 150),
            ("Score", "Engagement Score", 120),
            ("Contributions", "Contributions", 100),
            ("Streak", "Streak", 80),
            ("Active Days", "Active Days", 100),
            ("Badges", "Badges", 100)
        ]
        
        for col, heading, width in columns:
            self.leaderboard_tree.heading(col, text=heading)
            self.leaderboard_tree.column(col, width=width, anchor='center')
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.leaderboard_tree.yview
        )
        self.leaderboard_tree.configure(yscrollcommand=scrollbar.set)
        
        self.leaderboard_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bind double-click to show detailed stats
        self.leaderboard_tree.bind('<Double-1>', self.show_detailed_stats)

    def setup_add_forms(self):
        notebook = ttk.Notebook(self.add_tab)
        notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Add Contributor Form
        contributor_frame = ttk.Frame(notebook)
        notebook.add(contributor_frame, text="Add Contributor")
        
        ttk.Label(contributor_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5)
        self.name_var = tk.StringVar()
        ttk.Entry(contributor_frame, textvariable=self.name_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(contributor_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5)
        self.username_var = tk.StringVar()
        ttk.Entry(contributor_frame, textvariable=self.username_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(contributor_frame, text="Email:").grid(row=2, column=0, padx=5, pady=5)
        self.email_var = tk.StringVar()
        ttk.Entry(contributor_frame, textvariable=self.email_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(
            contributor_frame,
            text="Add Contributor",
            command=self.add_contributor,
            style="Primary.TButton"
        ).grid(row=3, column=0, columnspan=2, pady=20)
        
        # Add Contribution Form
        contribution_frame = ttk.Frame(notebook)
        notebook.add(contribution_frame, text="Add Contribution")
        
        ttk.Label(contribution_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5)
        self.contrib_username_var = tk.StringVar()
        ttk.Entry(contribution_frame, textvariable=self.contrib_username_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(contribution_frame, text="Repository:").grid(row=1, column=0, padx=5, pady=5)
        self.repo_var = tk.StringVar()
        ttk.Entry(contribution_frame, textvariable=self.repo_var).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(contribution_frame, text="Type:").grid(row=2, column=0, padx=5, pady=5)
        self.type_var = tk.StringVar()
        type_combo = ttk.Combobox(
            contribution_frame,
            textvariable=self.type_var,
            values=["bug-fix", "feature", "documentation", "test", "other"]
        )
        type_combo.grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(contribution_frame, text="Description:").grid(row=3, column=0, padx=5, pady=5)
        self.description_var = tk.StringVar()
        ttk.Entry(contribution_frame, textvariable=self.description_var).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(contribution_frame, text="PR Number:").grid(row=4, column=0, padx=5, pady=5)
        self.pr_var = tk.StringVar()
        ttk.Entry(contribution_frame, textvariable=self.pr_var).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Button(
            contribution_frame,
            text="Add Contribution",
            command=self.add_contribution,
            style="Primary.TButton"
        ).grid(row=5, column=0, columnspan=2, pady=20)

    def load_initial_data(self):
        # Update dashboard statistics
        metrics = self.tracker.get_project_performance_metrics()
        self.update_dashboard_stats(metrics)
        
        # Load contributors
        self.refresh_contributors_list()
        
        # Update leaderboard
        self.refresh_leaderboard()

    def update_dashboard_stats(self, metrics):
        self.stats_vars['contributors'].set(str(metrics['total_contributors']))
        self.stats_vars['contributions'].set(str(metrics['total_contributions']))
        self.stats_vars['completion'].set(f"{metrics['hacktoberfest_completion_rate']:.0f}%")
        
        # Clear existing activities
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        # Add recent activities (last 5)
        recent_activities = [
            ("Just now", "New contribution added by @user1"),
            ("2h ago", "Badge earned: 🔥 3-day streak by @user2"),
            ("5h ago", "New contributor joined: @user3"),
            ("1d ago", "Hacktoberfest completed by @user4"),
            ("2d ago", "New contribution added by @user5")
        ]
        
        for time, activity in recent_activities:
            self.activity_tree.insert("", "end", values=(time, activity))

    def refresh_contributors_list(self):
        # Clear existing items
        for item in self.contributors_tree.get_children():
            self.contributors_tree.delete(item)
        
        # Add contributors
        for contributor in self.tracker.get_all_contributors():
            metrics = self.tracker.get_contributor_metrics(contributor.username)
            status = "✅" if metrics['hacktoberfest_complete'] else "🔄"
            
            self.contributors_tree.insert(
                "",
                "end",
                values=(
                    contributor.username,
                    contributor.name,
                    contributor.email,
                    metrics['total_contributions'],
                    status
                )
            )

    def create_stat_card(self, parent, title, value_var, position):
        """Creates a statistics card widget"""
        card = ttk.Frame(parent, style="Stats.TFrame")
        card.grid(row=0, column=position, padx=5, sticky='nsew')
        parent.grid_columnconfigure(position, weight=1)
        
        ttk.Label(
            card,
            text=title,
            style="Header.TLabel"
        ).pack(pady=(10, 5))
        
        ttk.Label(
            card,
            textvariable=value_var,
            style="Stats.TLabel"
        ).pack(pady=(0, 10))
        
    def refresh_leaderboard(self):
        # Clear existing items
        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)
        
        # Get rankings based on sort criteria
        rankings = self.tracker.get_contributors_ranking()
        
        # Update stat cards
        if rankings:
            top_contributor = rankings[0]
            self.top_contributor_var.set(
                f"{top_contributor['username']}\n{top_contributor['engagement_score']:.1f} pts"
            )
            
            # Find longest streak
            max_streak = 0
            streak_holder = ""
            for rank in rankings:
                metrics = self.tracker.get_contributor_metrics(rank['username'])
                if metrics['contribution_streak'] > max_streak:
                    max_streak = metrics['contribution_streak']
                    streak_holder = rank['username']
            
            self.longest_streak_var.set(
                f"{streak_holder}\n{max_streak} days"
            )
            
            # Find most badges
            max_badges = 0
            badge_holder = ""
            for rank in rankings:
                metrics = self.tracker.get_contributor_metrics(rank['username'])
                badges = 0
                if metrics['hacktoberfest_complete']:
                    badges += 1
                if metrics['contribution_streak'] >= 3:
                    badges += 1
                if badges > max_badges:
                    max_badges = badges
                    badge_holder = rank['username']
            
            self.most_badges_var.set(
                f"{badge_holder}\n{max_badges} badges"
            )
        
        # Populate table
        for rank in rankings:
            metrics = self.tracker.get_contributor_metrics(rank['username'])
            
            # Calculate badges
            badges = []
            if metrics['hacktoberfest_complete']:
                badges.append("🏆")
            if metrics['contribution_streak'] >= 3:
                badges.append("🔥")
            if metrics['total_contributions'] >= 10:
                badges.append("⭐")
            
            self.leaderboard_tree.insert(
                "",
                "end",
                values=(
                    rank['rank'],
                    rank['username'],
                    f"{rank['engagement_score']:.1f}",
                    metrics['total_contributions'],
                    f"{metrics['contribution_streak']} days",
                    metrics['days_active'],
                    " ".join(badges)
                )
            )

    def filter_contributors(self, *args):
        search_text = self.search_var.get().lower()
        
        for item in self.contributors_tree.get_children():
            values = self.contributors_tree.item(item)['values']
            if (search_text in str(values[0]).lower() or  # username
                search_text in str(values[1]).lower() or  # name
                search_text in str(values[2]).lower()):   # email
                self.contributors_tree.reattach(item, "", "end")
            else:
                self.contributors_tree.detach(item)

    def add_contributor(self):
        name = self.name_var.get().strip()
        username = self.username_var.get().strip()
        email = self.email_var.get().strip()
        
        if not all([name, username, email]):
            messagebox.showerror("Error", "All fields are required")
            return
        
        try:
            contributor = self.tracker.add_contributor(name, username, email)
            messagebox.showinfo("Success", f"Added contributor: {contributor.name}")
            
            # Clear form
            self.name_var.set("")
            self.username_var.set("")
            self.email_var.set("")
            
            # Refresh views
            self.refresh_contributors_list()
            
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_contribution(self):
        username = self.contrib_username_var.get().strip()
        repo = self.repo_var.get().strip()
        contrib_type = self.type_var.get()
        description = self.description_var.get().strip()
        pr_number = self.pr_var.get().strip()
        
        if not all([username, repo, contrib_type, description]):
            messagebox.showerror("Error", "Required fields are missing")
            return
        
        try:
            success = self.tracker.add_contribution(
                username, repo, contrib_type, description,
                pr_number if pr_number else None
            )
            
            if success:
                messagebox.showinfo("Success", "Contribution added successfully")
                
                # Clear form
                self.contrib_username_var.set("")
                self.repo_var.set("")
                self.type_var.set("")
                self.description_var.set("")
                self.pr_var.set("")
                
                # Refresh views
                self.refresh_contributors_list()
                self.refresh_leaderboard()
                
            else:
                messagebox.showerror("Error", "Failed to add contribution")
                
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def sort_leaderboard(self, event=None):
        """Sort the leaderboard based on selected criteria"""
        sort_by = self.sort_var.get()
        
        # Get all items
        items = []
        for item_id in self.leaderboard_tree.get_children():
            values = self.leaderboard_tree.item(item_id)['values']
            items.append(values)
        
        # Sort based on criteria
        if sort_by == "score":
            items.sort(key=lambda x: float(x[2]), reverse=True)
        elif sort_by == "streak":
            items.sort(key=lambda x: int(x[4].split()[0]), reverse=True)
        elif sort_by == "contributions":
            items.sort(key=lambda x: int(x[3]), reverse=True)
        
        # Clear and repopulate
        for item in self.leaderboard_tree.get_children():
            self.leaderboard_tree.delete(item)
        
        # Update ranks and reinsert
        for i, values in enumerate(items, 1):
            values = list(values)
            values[0] = i  # Update rank
            self.leaderboard_tree.insert("", "end", values=values)
    
    def show_detailed_stats(self, event):
        """Show detailed statistics for selected contributor"""
        item = self.leaderboard_tree.selection()[0]
        username = self.leaderboard_tree.item(item)['values'][1]
        metrics = self.tracker.get_contributor_metrics(username)
        
        # Create stats window
        stats_window = tk.Toplevel(self.root)
        stats_window.title(f"Detailed Stats - {username}")
        stats_window.geometry("400x500")
        
        # Main frame
        main_frame = ttk.Frame(stats_window, padding="20 20 20 20")
        main_frame.pack(fill='both', expand=True)
        
        # Header
        ttk.Label(
            main_frame,
            text=f"Statistics for {username}",
            style="Title.TLabel"
        ).pack(pady=(0, 20))
        
        # Create stats grid
        stats_frame = ttk.Frame(main_frame)
        stats_frame.pack(fill='both', expand=True)
        
        # Detailed statistics
        stats = [
            ("🎯 Total Contributions", metrics['total_contributions']),
            ("🔥 Current Streak", f"{metrics['contribution_streak']} days"),
            ("📅 Days Active", metrics['days_active']),
            ("📊 Engagement Score", f"{metrics['engagement_score']:.1f}"),
            ("⌛ Avg. Days Between", f"{metrics['average_days_between_contributions']:.1f}"),
            ("📆 Most Active Day", metrics['most_active_day'] or "N/A"),
            ("🎖️ Hacktoberfest Status", "Completed ✅" if metrics['hacktoberfest_complete'] else "In Progress ⏳")
        ]
        
        for i, (label, value) in enumerate(stats):
            ttk.Label(
                stats_frame,
                text=label,
                style="Header.TLabel"
            ).grid(row=i, column=0, sticky='w', pady=5)
            
            ttk.Label(
                stats_frame,
                text=str(value),
                style="Stats.TLabel"
            ).grid(row=i, column=1, sticky='e', pady=5)
            
        # Progress bars frame
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill='x', pady=(20, 0))
        
        # Hacktoberfest progress
        ttk.Label(
            progress_frame,
            text="Hacktoberfest Progress",
            style="Header.TLabel"
        ).pack(anchor='w')
        
        progress = ttk.Progressbar(
            progress_frame,
            length=200,
            mode='determinate'
        )
        progress.pack(fill='x', pady=(5, 10))
        
        # Calculate and set progress
        completion = (metrics['total_contributions'] / 4) * 100
        progress['value'] = min(completion, 100)
        
        ttk.Label(
            progress_frame,
            text=f"{metrics['total_contributions']}/4 contributions",
            style="Stats.TLabel"
        ).pack(anchor='e')

    def show_contributor_details(self, event):
        item = self.contributors_tree.selection()[0]
        username = self.contributors_tree.item(item)['values'][0]
        
        # Create detail window
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Contributor Details - {username}")
        detail_window.geometry("500x400")
        
        # Get metrics
        metrics = self.tracker.get_contributor_metrics(username)
        contributor = self.tracker.get_contributor(username)
        
        # Display information
        ttk.Label(
            detail_window,
            text=f"{contributor.name} (@{username})",
            style="Title.TLabel"
        ).pack(pady=10)
        
        details_frame = ttk.Frame(detail_window)
        details_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        details = [
            ("Email", contributor.email),
            ("Total Contributions", metrics['total_contributions']),
            ("Contribution Streak", f"{metrics['contribution_streak']} days"),
            ("Days Active", metrics['days_active']),
            ("Average Days Between Contributions", f"{metrics['average_days_between_contributions']:.1f}"),
            ("Hacktoberfest Complete", "Yes ✅" if metrics['hacktoberfest_complete'] else "No ❌"),
            ("Most Active Day", metrics['most_active_day'] or "N/A")
        ]
        
        for i, (label, value) in enumerate(details):
            ttk.Label(details_frame, text=f"{label}:", style="Header.TLabel").grid(
                row=i, column=0, sticky='w', padx=5, pady=2
            )
            ttk.Label(details_frame, text=str(value)).grid(
                row=i, column=1, sticky='w', padx=5, pady=2
            )



    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = HacktoberfestDesktopUI()
    app.run()
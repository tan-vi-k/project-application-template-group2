from typing import List
import matplotlib.pyplot as plt
import pandas as pd
import os
from datetime import datetime
from data_loader import DataLoader
from model import Issue


class ContributorActivityAnalysis:
    """
    Contributor Activity Analysis
    ---------------------------------
    - Uses the 'creator' field (string username) from the dataset.
    - Counts how many issues each contributor created.
    - Optionally filters by year.
    - Displays and saves a bar chart of the top contributors.
    - Each run saves a uniquely named output chart (not overwritten).
    """

    def __init__(self):
        os.makedirs("output/charts", exist_ok=True)

    def run(self):
        issues: List[Issue] = DataLoader().get_issues()

        if not issues:
            print("\n No issues found in dataset.\n")
            return

        records = []
        for issue in issues:
            creator = getattr(issue, "creator", None)
            created_date = getattr(issue, "created_date", None)

            if isinstance(creator, str) and creator.strip():
                records.append({
                    "user": creator.strip(),
                    "created_date": created_date
                })

        if not records:
            print("\n No contributor usernames found in dataset.\n")
            return

        df = pd.DataFrame.from_records(records)

        # --- Convert created_date safely (handles both datetime + string) ---
        def normalize_date(value):
            """Convert mixed datetime/string values safely."""
            if isinstance(value, datetime):
                return value.replace(tzinfo=None)
            if isinstance(value, str):
                try:
                    return datetime.fromisoformat(value.replace("Z", "+00:00")).replace(tzinfo=None)
                except Exception:
                    try:
                        return pd.to_datetime(value, utc=True).to_pydatetime().replace(tzinfo=None)
                    except Exception:
                        return pd.NaT
            return pd.NaT

        df["created_date"] = df["created_date"].apply(normalize_date)
        df = df.dropna(subset=["created_date"])

        if df.empty:
            print("\n No valid created_date entries after normalization. Please verify dataset format.\n")
            print("Example raw value from dataset:", getattr(issues[0], "created_date", None))
            return

        df["year"] = df["created_date"].dt.year
        years = sorted(int(y) for y in df["year"].dropna().unique())
        if years:
            print("Detected years in dataset:", ", ".join(str(y) for y in years))
        else:
            print("Detected years in dataset: None found")

        # --- Year filter ---
        year_input = input("\nEnter a year to filter by (or press Enter to analyze all years): ").strip()
        year_filter = int(year_input) if year_input else None

        if year_filter:
            df = df[df["year"] == year_filter]
            if df.empty:
                print(f"\nNo contributor activity found for year {year_filter}.\n")
                return
            summary = df.groupby("user").size().reset_index(name="issue_count")
            print(f"\nShowing contributor activity for year {year_filter}\n")
        else:
            summary = df.groupby("user").size().reset_index(name="issue_count")
            print("\nShowing overall contributor activity (all years)\n")

        summary = summary.sort_values("issue_count", ascending=False).head(10)

        if summary.empty:
            print("\n No contributor data to visualize.\n")
            return

        # --- Visualization ---
        plt.figure(figsize=(12, 6))
        plt.bar(summary["user"], summary["issue_count"], color="teal")
        plt.title(
            f"Top 10 Contributors {'in ' + str(year_filter) if year_filter else '(All Years)'}",
            fontsize=14
        )
        plt.xlabel("Contributor (Username)")
        plt.ylabel("Number of Issues Created")
        plt.xticks(rotation=45, ha="right")
        plt.grid(axis="y", linestyle="--", alpha=0.5)
        plt.tight_layout()

        # --- Unique file naming ---
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        year_label = str(year_filter) if year_filter else "all"
        chart_filename = f"contributor_activity_{year_label}_{timestamp}.png"
        chart_path = os.path.join("output/charts", chart_filename)

        plt.savefig(chart_path, bbox_inches="tight")
        plt.show()

        # --- Summary ---
        total_contributors = len(df["user"].unique())
        total_issues = len(df)
        avg_issues = summary["issue_count"].mean() if not summary.empty else 0

        print("\nContributor Activity Summary")
        print("-" * 40)
        print(f"Total contributors analyzed: {total_contributors}")
        print(f"Total issues created: {total_issues}")
        print(f"Average issues per contributor: {avg_issues:.2f}")

        if not summary.empty:
            top_user = summary.iloc[0]
            print(f"Most active contributor: {top_user['user']} ({int(top_user['issue_count'])} issues)")

        if not df.empty:
            first_date = df["created_date"].min().strftime("%Y-%m-%d")
            last_date = df["created_date"].max().strftime("%Y-%m-%d")
            print(f"Issue data range: {first_date} → {last_date}")

        print(f"Chart saved to: {chart_path}")
        print("-" * 40)


if __name__ == "__main__":
    ContributorActivityAnalysis().run()

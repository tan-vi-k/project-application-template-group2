"""
Domain model definitions for GitHub issue data.
This module defines Python classes that represent the entities
and relationships found in the Poetry issues dataset.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional


class User:
    def __init__(self, data: Dict[str, Any]):
        self.id: Optional[int] = data.get("id")
        self.login: Optional[str] = data.get("login")
        self.type: Optional[str] = data.get("type")
        self.site_admin: bool = data.get("site_admin", False)


class Label:
    def __init__(self, data):
        # Handle both dict-based and string-based label representations
        if isinstance(data, dict):
            self.name = data.get("name")
        elif isinstance(data, str):
            self.name = data
        else:
            self.name = None



class Comment:
    def __init__(self, data: Dict[str, Any]):
        self.id: Optional[int] = data.get("id")
        self.issue_id: Optional[int] = data.get("issue_id")
        self.event_id: Optional[int] = data.get("event_id")

        # Author may be a nested dict
        author_data = data.get("author") or {}
        if isinstance(author_data, dict):
            self.author_id = author_data.get("id")
            self.author_login = author_data.get("login")
        else:
            self.author_id = data.get("author_id")
            self.author_login = None

        self.comment: Optional[str] = data.get("body") or data.get("comment")
        self.created_date: Optional[datetime] = None
        if data.get("created_at"):
            try:
                self.created_date = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            except Exception:
                pass


class Event:
    def __init__(self, data: Dict[str, Any]):
        self.id: Optional[int] = data.get("id")
        self.event_type: Optional[str] = data.get("event") or data.get("event_type")
        self.issue_id: Optional[int] = data.get("issue_id")
        self.comment_id: Optional[int] = data.get("comment_id")

        author_data = data.get("actor") or data.get("author") or {}
        if isinstance(author_data, dict):
            self.author_id = author_data.get("id")
            self.author_login = author_data.get("login")
        else:
            self.author_id = data.get("author_id")
            self.author_login = None

        self.label_name: Optional[str] = None
        if isinstance(data.get("label"), dict):
            self.label_name = data["label"].get("name")

        self.event_date: Optional[datetime] = None
        if data.get("created_at"):
            try:
                self.event_date = datetime.fromisoformat(
                    data["created_at"].replace("Z", "+00:00")
                )
            except Exception:
                pass


class IssueLabel:
    def __init__(self, issue_number: int, label_name: str):
        self.issue_number = issue_number
        self.label_name = label_name


class IssueAssignee:
    def __init__(self, issue_number: int, assignee_id: int):
        self.issue_number = issue_number
        self.assignee_id = assignee_id


class Issue:
    def __init__(self, data: Dict[str, Any]):
        self.number: Optional[int] = data.get("number")
        self.title: Optional[str] = data.get("title")
        self.state: Optional[str] = data.get("state")
        self.url: Optional[str] = data.get("url")
        self.timeline_url: Optional[str] = data.get("timeline_url")
        self.text: Optional[str] = data.get("body")

        # --- Creator info ---
        # --- Creator info ---
        creator_data = data.get("user") or data.get("creator")

        # Case 1: creator is a nested dict
        if isinstance(creator_data, dict):
            self.creator_id = creator_data.get("id")
            self.creator_login = creator_data.get("login")
            self.creator = creator_data.get("login") or creator_data.get("id")

        # Case 2: creator is a string (username)
        elif isinstance(creator_data, str):
            self.creator_id = None
            self.creator_login = creator_data
            self.creator = creator_data

        # Case 3: missing
        else:
            self.creator_id = None
            self.creator_login = None
            self.creator = None

         # --- Dates ---
        self.created_date: Optional[datetime] = None
        self.updated_date: Optional[datetime] = None

        # Handle both "created_date" and "created_at" keys
        raw_created = data.get("created_date") or data.get("created_at")
        raw_updated = data.get("updated_date") or data.get("updated_at")

        try:
            if raw_created:
                self.created_date = datetime.fromisoformat(
                    str(raw_created).replace("Z", "+00:00")
                )
        except Exception:
            self.created_date = None

        try:
            if raw_updated:
                self.updated_date = datetime.fromisoformat(
                    str(raw_updated).replace("Z", "+00:00")
                )
        except Exception:
            self.updated_date = None

        
        # --- Comments ---
        self.comments: List[Comment] = []
        if "comments" in data and isinstance(data["comments"], list):
            self.comments = [Comment(c) for c in data["comments"]]

        # --- Events ---
        self.events: List[Event] = []
        if "events" in data and isinstance(data["events"], list):
            self.events = [Event(e) for e in data["events"]]

        # --- Labels ---
        self.labels: List[Label] = []
        if "labels" in data and isinstance(data["labels"], list):
            self.labels = []
            for l in data.get("labels", []):
                 self.labels.append(Label(l))



# Optional convenience list (if needed elsewhere)
__all__ = [
    "Issue",
    "User",
    "Comment",
    "Event",
    "Label",
    "IssueLabel",
    "IssueAssignee",
]

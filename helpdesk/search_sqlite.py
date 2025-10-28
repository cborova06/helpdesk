# Copyright (c) 2025, Frappe Technologies Pvt. Ltd. and Contributors
# MIT License. See license.txt

import frappe
from frappe.search.sqlite_search import SQLiteSearch, SQLiteSearchIndexMissingError


class HelpdeskSearchIndexMissingError(SQLiteSearchIndexMissingError):
    pass


class HelpdeskSearch(SQLiteSearch):
    INDEX_NAME = "helpdesk_search.db"

    INDEX_SCHEMA = {
        "metadata_fields": [
            "agent_group",
            "customer",
            "status",
            "priority",
            "owner",
            "reference_doctype",
            "reference_name",
            "reference_ticket",
        ],
        "tokenizer": "unicode61 remove_diacritics 2 tokenchars '-_'",
    }

    INDEXABLE_DOCTYPES = {
        "HD Ticket": {
            "fields": [
                "name",
                {"title": "subject"},
                {"content": "description"},
                "modified",
                "agent_group",
                "status",
                "priority",
                "raised_by",
                "owner",
            ],
        },
        "HD Ticket Comment": {
            "fields": [
                "name",
                "content",
                "modified",
                "reference_ticket",
                "commented_by",
                "owner",
            ],
        },
        "Communication": {
            "fields": [
                "name",
                "content",
                "modified",
                "reference_doctype",
                "reference_name",
                "sender",
                "owner",
            ],
            "filters": {"reference_doctype": "HD Ticket"},
        },
    }

    def get_search_filters(self):
        """Return permission filters based on accessible tickets."""
        accessible_tickets = self._get_accessible_tickets()
        return {"reference_ticket": accessible_tickets}

    def _get_accessible_tickets(self):
        """Get tickets accessible to current user based on helpdesk permissions."""
        return frappe.get_list("HD Ticket", pluck="name")

    def prepare_document(self, doc):
        """Prepare a document for indexing with helpdesk-specific handling."""
        document = super().prepare_document(doc)
        if not document:
            return None

        if doc.doctype == "HD Ticket Comment":
            # For comments, resolve the ticket for permissions
            document["reference_ticket"] = int(doc.reference_ticket)

        if doc.doctype == "Communication":
            # For communications, ensure reference fields are set
            document["reference_doctype"] = doc.reference_doctype
            document["reference_ticket"] = int(doc.reference_name)

        if doc.doctype == "HD Ticket":
            document["reference_ticket"] = int(doc.name)

        # Map commented_by to owner for HD Ticket Comment
        if doc.doctype == "HD Ticket Comment":
            document["owner"] = doc.commented_by

        # Map sender to owner for Communication
        if doc.doctype == "Communication":
            document["owner"] = doc.sender

        return document

    def get_filter_options(self):
        """Get available filter options for search interface."""
        if not self.index_exists():
            return {
                "teams": {},
                "statuses": {},
                "priorities": {},
                "customers": {},
                "doctypes": {},
            }

        # Get accessible tickets first
        accessible_tickets = self._get_accessible_tickets()
        if not accessible_tickets:
            return {
                "teams": {},
                "statuses": {},
                "priorities": {},
                "customers": {},
                "doctypes": {},
            }

        # Query the search index for available options
        sql = """
			SELECT
				agent_group,
				status,
				priority,
				customer,
				doctype,
				COUNT(*) as count
			FROM search_fts
			WHERE (name IN ({placeholders}) OR reference_name IN ({placeholders}) OR reference_ticket IN ({placeholders}))
			GROUP BY agent_group, status, priority, customer, doctype
		""".format(
            placeholders=",".join(["?" for _ in accessible_tickets])
        )

        params = accessible_tickets * 3
        results = self.sql(sql, params, read_only=True)

        # Aggregate the results
        teams = {}
        statuses = {}
        priorities = {}
        customers = {}
        doctypes = {}

        for row in results:
            if row["agent_group"]:
                teams[row["agent_group"]] = (
                    teams.get(row["agent_group"], 0) + row["count"]
                )
            if row["status"]:
                statuses[row["status"]] = statuses.get(row["status"], 0) + row["count"]
            if row["priority"]:
                priorities[row["priority"]] = (
                    priorities.get(row["priority"], 0) + row["count"]
                )
            if row["customer"]:
                customers[row["customer"]] = (
                    customers.get(row["customer"], 0) + row["count"]
                )
            if row["doctype"]:
                doctypes[row["doctype"]] = (
                    doctypes.get(row["doctype"], 0) + row["count"]
                )

        return {
            "teams": teams,
            "statuses": statuses,
            "priorities": priorities,
            "customers": customers,
            "doctypes": doctypes,
        }


def build_index():
    """Build search index - called by background job."""
    search = HelpdeskSearch()
    search.build_index()


# Compatibility wrappers referenced by hooks
def build_index_if_not_exists():
    """Delegate to core sqlite_search build_index_if_not_exists using hooks-registered classes."""
    from frappe.search.sqlite_search import build_index_if_not_exists as _core_build_if_missing

    return _core_build_if_missing()


def update_doc_index(doc, method=None):
    """Update single document in index (hook: after_insert, on_update)."""
    from frappe.search.sqlite_search import update_doc_index as _core_update

    return _core_update(doc, method)


def delete_doc_index(doc, method=None):
    """Remove single document from index (hook: on_trash)."""
    from frappe.search.sqlite_search import delete_doc_index as _core_delete

    return _core_delete(doc, method)


# Hooks API (compatibility with doc_events in hooks.py)
def update_doc_index(doc, method=None):
    """Index a single document after insert/update."""
    try:
        search = HelpdeskSearch()
        if search.index_exists():
            search.index_doc(doc.doctype, doc.name)
    except Exception:
        frappe.log_error(title="helpdesk.search_sqlite.update_doc_index failed", message=frappe.get_traceback())


def delete_doc_index(doc, method=None):
    """Remove a single document from the index on delete/trash."""
    try:
        search = HelpdeskSearch()
        if search.index_exists():
            search.remove_doc(doc.doctype, doc.name)
    except Exception:
        frappe.log_error(title="helpdesk.search_sqlite.delete_doc_index failed", message=frappe.get_traceback())


def build_index_if_not_exists():
    """Ensure index exists; if not, build it."""
    try:
        search = HelpdeskSearch()
        if not search.index_exists():
            search.build_index()
    except Exception:
        frappe.log_error(title="helpdesk.search_sqlite.build_index_if_not_exists failed", message=frappe.get_traceback())

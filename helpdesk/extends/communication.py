"""
Extension for Communication doctype to publish real-time updates
when new communications are added to HD Tickets.
"""

import frappe


def after_insert(doc, method=None):
    """
    Publish real-time event when a new communication is created
    for an HD Ticket to notify all connected clients.
    """
    if doc.reference_doctype == "HD Ticket" and doc.reference_name:
        # Get ticket to find all related users
        ticket = frappe.get_doc("HD Ticket", doc.reference_name)
        
        # Publish event to ALL users involved with this ticket
        # (agent, customer, and anyone viewing the ticket)
        frappe.publish_realtime(
            "helpdesk:ticket-update",
            message={"ticket_id": doc.reference_name},
            room=frappe.local.site,  # Broadcast to entire site
            after_commit=True,
        )
        
        # Also send refetch_resource event for cached data
        # Send to both agent and customer
        users_to_notify = []
        if ticket.raised_by:
            users_to_notify.append(ticket.raised_by)
        if ticket._assign:
            users_to_notify.append(ticket._assign)
        
        for user in users_to_notify:
            if user:
                frappe.publish_realtime(
                    "refetch_resource",
                    message={"cache_key": f"Ticket:{doc.reference_name}"},
                    user=user,
                    after_commit=True,
                )

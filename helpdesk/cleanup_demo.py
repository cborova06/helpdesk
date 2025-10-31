import frappe

def execute():
    """Delete all demo tickets created by seeding (IDs 315-333)."""
    
    # Get tickets created during seeding (approximately last 20 tickets)
    tickets = frappe.db.sql("""
        SELECT name, subject 
        FROM `tabHD Ticket` 
        WHERE creation >= '2025-10-31 10:00:00'
        ORDER BY name
    """, as_dict=True)
    
    print(f"Found {len(tickets)} demo tickets to delete")
    
    deleted_count = 0
    failed_count = 0
    
    for ticket in tickets:
        try:
            ticket_id = ticket.name
            
            # Delete linked Communications first
            comms = frappe.get_all("Communication", 
                                   filters={"reference_doctype": "HD Ticket", "reference_name": ticket_id},
                                   pluck="name")
            for comm_id in comms:
                frappe.delete_doc("Communication", comm_id, force=True, ignore_permissions=True)
            
            # Delete the ticket (on_trash will handle activities and comments)
            frappe.delete_doc("HD Ticket", ticket_id, force=True, ignore_permissions=True)
            deleted_count += 1
            print(f"✓ Deleted ticket {ticket_id}: {ticket.subject[:40]}")
            
        except Exception as e:
            failed_count += 1
            print(f"✗ Failed to delete {ticket_id}: {str(e)}")
    
    frappe.db.commit()
    print(f"\nSummary: {deleted_count} deleted, {failed_count} failed")

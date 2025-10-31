import frappe

def execute():
    """Delete ALL tickets and related data again."""
    
    # Get all tickets
    tickets = frappe.get_all("HD Ticket", pluck="name")
    
    print(f"Found {len(tickets)} tickets to delete")
    
    deleted_count = 0
    
    for ticket_id in tickets:
        try:
            # Delete linked Communications
            comms = frappe.get_all("Communication", 
                                   filters={"reference_doctype": "HD Ticket", "reference_name": ticket_id},
                                   pluck="name")
            for comm_id in comms:
                try:
                    frappe.delete_doc("Communication", comm_id, force=True, ignore_permissions=True)
                except:
                    pass
            
            # Delete the ticket
            frappe.delete_doc("HD Ticket", ticket_id, force=True, ignore_permissions=True)
            deleted_count += 1
            
            if deleted_count % 5 == 0:
                print(f"Deleted {deleted_count}/{len(tickets)} tickets...")
            
        except Exception as e:
            print(f"Failed to delete {ticket_id}: {str(e)}")
    
    frappe.db.commit()
    print(f"\n✓ Deleted {deleted_count} tickets")

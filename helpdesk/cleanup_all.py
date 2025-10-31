import frappe

def execute():
    """Delete ALL tickets and related data."""
    
    # Get all tickets
    tickets = frappe.get_all("HD Ticket", pluck="name")
    
    print(f"Found {len(tickets)} tickets to delete")
    
    deleted_count = 0
    failed_count = 0
    
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
            
            # Delete linked HD Ticket Activities
            activities = frappe.get_all("HD Ticket Activity", {"ticket": ticket_id}, pluck="name")
            for activity_id in activities:
                try:
                    frappe.delete_doc("HD Ticket Activity", activity_id, force=True, ignore_permissions=True)
                except:
                    pass
            
            # Delete linked HD Ticket Comments
            comments = frappe.get_all("HD Ticket Comment", {"reference_ticket": ticket_id}, pluck="name")
            for comment_id in comments:
                try:
                    frappe.delete_doc("HD Ticket Comment", comment_id, force=True, ignore_permissions=True)
                except:
                    pass
            
            # Delete the ticket
            frappe.delete_doc("HD Ticket", ticket_id, force=True, ignore_permissions=True)
            deleted_count += 1
            
            if deleted_count % 5 == 0:
                print(f"Deleted {deleted_count}/{len(tickets)} tickets...")
            
        except Exception as e:
            failed_count += 1
            print(f"✗ Failed to delete {ticket_id}: {str(e)}")
    
    frappe.db.commit()
    print(f"\n✓ Summary: {deleted_count} deleted, {failed_count} failed")
    print(f"Remaining tickets: {len(frappe.get_all('HD Ticket'))}")

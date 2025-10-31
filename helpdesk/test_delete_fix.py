import frappe

def execute():
    """Test deleting a ticket to identify issues."""
    
    ticket_id = "332"
    
    try:
        ticket = frappe.get_doc("HD Ticket", ticket_id)
        print(f"Found ticket: {ticket.name} - {ticket.subject}")
        
        # Check if there are any linked documents
        comms = frappe.get_all("Communication", 
                               filters={"reference_doctype": "HD Ticket", "reference_name": ticket_id},
                               fields=["name", "communication_type"])
        print(f"Found {len(comms)} linked Communications: {[c.name for c in comms]}")
        
        activities = frappe.get_all("HD Ticket Activity", {"ticket": ticket_id})
        print(f"Found {len(activities)} linked Ticket Activities")
        
        comments = frappe.get_all("HD Ticket Comment", {"reference_ticket": ticket_id})
        print(f"Found {len(comments)} linked Ticket Comments")
        
        # Try to delete
        print(f"\nAttempting to delete ticket {ticket_id}...")
        frappe.delete_doc("HD Ticket", ticket_id, force=True)
        print("✓ Successfully deleted ticket")
        frappe.db.commit()
        
    except Exception as e:
        print(f"\n✗ Error deleting ticket: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        frappe.db.rollback()

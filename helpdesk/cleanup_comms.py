import frappe

def execute():
    """Delete all Communications related to HD Ticket."""
    
    comms = frappe.get_all("Communication", 
                          filters={"reference_doctype": "HD Ticket"},
                          pluck="name")
    
    print(f"Found {len(comms)} Communications to delete")
    
    deleted = 0
    for comm_id in comms:
        try:
            frappe.delete_doc("Communication", comm_id, force=True, ignore_permissions=True)
            deleted += 1
            if deleted % 20 == 0:
                print(f"Deleted {deleted}/{len(comms)}...")
        except Exception as e:
            print(f"Failed to delete {comm_id}: {str(e)}")
    
    frappe.db.commit()
    
    remaining = len(frappe.get_all("Communication", filters={"reference_doctype": "HD Ticket"}))
    print(f"\n✓ Deleted {deleted} Communications, {remaining} remaining")

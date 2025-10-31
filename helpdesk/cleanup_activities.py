import frappe

def execute():
    activities = frappe.get_all("HD Ticket Activity", pluck="name")
    print(f"Deleting {len(activities)} activities...")
    
    for activity_id in activities:
        frappe.db.delete("HD Ticket Activity", {"name": activity_id})
    
    frappe.db.commit()
    print(f"✓ Deleted all activities")

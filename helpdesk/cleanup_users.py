import frappe

def execute():
    """Delete test users except whitelisted ones."""
    
    # Whitelist - keep these users
    keep_users = ['Administrator', 'Guest', 'borovacihan@gmail.com', 'john@example.com']
    
    # Get all users
    all_users = frappe.get_all("User", 
                               filters={"name": ["not in", keep_users]},
                               fields=["name", "email", "full_name"])
    
    print(f"Found {len(all_users)} users to potentially delete")
    
    deleted_count = 0
    for user in all_users:
        try:
            email = user.get("email") or user.get("name")
            print(f"Deleting user: {email} ({user.get('full_name')})")
            
            # Delete related HD Agent if exists
            if frappe.db.exists("HD Agent", email):
                frappe.delete_doc("HD Agent", email, force=True, ignore_permissions=True)
                print(f"  - Deleted HD Agent: {email}")
            
            # Delete user
            frappe.delete_doc("User", user.name, force=True, ignore_permissions=True)
            deleted_count += 1
            
        except Exception as e:
            print(f"  ✗ Failed to delete {user.name}: {str(e)}")
    
    frappe.db.commit()
    print(f"\n✓ Deleted {deleted_count} users")
    
    # Show remaining users
    remaining = frappe.get_all("User", fields=["name", "email", "full_name"])
    print(f"\nRemaining users ({len(remaining)}):")
    for u in remaining:
        print(f"  - {u.get('email') or u.name}: {u.full_name}")

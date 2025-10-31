import frappe

def execute():
    """Force delete all users except Administrator, Guest, and borovacihan@gmail.com."""
    
    # Keep only these users
    keep_users = ['Administrator', 'Guest', 'borovacihan@gmail.com']
    
    # Get all HD Agents first
    all_agents = frappe.get_all("HD Agent", fields=["name", "user"])
    print(f"Found {len(all_agents)} HD Agent records")
    
    for agent in all_agents:
        if agent.user not in keep_users:
            try:
                frappe.db.delete("HD Agent", {"name": agent.name})
                print(f"✓ Deleted HD Agent: {agent.user}")
            except Exception as e:
                print(f"✗ Failed to delete agent {agent.user}: {str(e)}")
    
    # Get all users
    all_users = frappe.get_all("User", fields=["name", "email", "full_name"])
    print(f"\nFound {len(all_users)} User records")
    
    for user in all_users:
        if user.name not in keep_users:
            try:
                # Use db.delete to bypass permissions and validations
                frappe.db.delete("User", {"name": user.name})
                email = user.email or user.name
                print(f"✓ Deleted User: {email} ({user.full_name})")
            except Exception as e:
                print(f"✗ Failed to delete {user.name}: {str(e)}")
    
    frappe.db.commit()
    
    # Show remaining users
    remaining_users = frappe.get_all("User", fields=["name", "email", "full_name"])
    print(f"\n=== Remaining Users ({len(remaining_users)}) ===")
    for u in remaining_users:
        print(f"  {u.email or u.name}: {u.full_name}")
    
    # Show remaining agents
    remaining_agents = frappe.get_all("HD Agent", fields=["name", "user", "agent_name"])
    print(f"\n=== Remaining Agents ({len(remaining_agents)}) ===")
    for a in remaining_agents:
        print(f"  {a.user}: {a.agent_name or 'N/A'}")

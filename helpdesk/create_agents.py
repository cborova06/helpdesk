import frappe

def execute():
    """Create HD Agents for valid users."""
    
    agents_to_create = [
        {"email": "admin@example.com", "name": "Administrator"},
        {"email": "borovacihan@gmail.com", "name": "Test Kullanıcısı"}
    ]
    
    for agent_info in agents_to_create:
        email = agent_info["email"]
        
        # Delete if exists first
        if frappe.db.exists("HD Agent", email):
            frappe.db.delete("HD Agent", {"name": email})
            print(f"Deleted existing HD Agent: {email}")
        
        # Create new
        try:
            agent = frappe.get_doc({
                "doctype": "HD Agent",
                "name": email,
                "user": email,
                "agent_name": agent_info["name"]
            })
            agent.insert(ignore_permissions=True)
            print(f"✓ Created HD Agent: {email} - {agent_info['name']}")
        except Exception as e:
            print(f"✗ Failed to create agent {email}: {str(e)}")
    
    frappe.db.commit()
    
    # Verify
    agents = frappe.get_all("HD Agent", fields=["name", "user", "agent_name"])
    print(f"\n=== HD Agents ({len(agents)}) ===")
    for a in agents:
        print(f"  {a.user}: {a.agent_name}")

def generate_email(input_data):
    recipient = input_data.get("recipient", "there")
    purpose = input_data.get("purpose", "your request")
    key_points = input_data.get("key_points", [])

    subject = f"Regarding {purpose.capitalize()}"
    greeting = f"Dear {recipient},\n\n"
    intro = f"I hope you're doing well. I'm reaching out to {purpose}.\n\n"

    bullet_body = ""
    for point in key_points:
        bullet_body += f"- {point}\n"
    
    closing = "\nPlease let me know if you have any questions.\n\nBest regards,\n[Your Name]"

    full_body = greeting + intro + bullet_body + closing

    return {
        "subject": subject,
        "body": full_body
    }

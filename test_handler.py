from app.lagu_request_handler import handle_request_input

user_id = "user001"
user_message = "request lagu taylor swift"

response, lagu_info = handle_request_input(user_id, user_message)

print("🔎 Response:", response)
print("🎵 Lagu Info:", lagu_info)

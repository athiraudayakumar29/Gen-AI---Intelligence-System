from memory.cosmos import save_message, get_session_history

test_session = "test-session-001"

save_message(test_session, "user", "Hello, this is a test message")
save_message(test_session, "assistant", "Hi! This is a test reply")

history = get_session_history(test_session)
print("Messages found:", len(history))
for m in history:
    print(f"  [{m['role']}] {m['content']}")
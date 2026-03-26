from imapclient import IMAPClient
import pyzmail
import time

# 🔐 YOUR DETAILS
EMAIL = "rasamallaviraj0@gmail.com"
PASSWORD = "sfcp dplc safo yhwn"

# ⚙️ SETTINGS
TRUSTED_SENDERS = ["rasamallaviraj@gmail.com"]
MAX_EMAILS = 10

# 🧠 CLASSIFIER
def classify(text):
    text = text.lower()

    spam_words = ["offer", "discount", "sale", "buy now", "limited time", "claim", "premium"]
    important_words = ["meeting", "project", "deadline", "exam", "interview", "assignment"]

    if any(word in text for word in spam_words):
        return "spam"

    if any(word in text for word in important_words):
        return "important"

    if "linkedin" in text or "notification" in text:
        return "spam"

    return "normal"

# 📢 SUMMARIZER
def summarize(text):
    return text[:80].replace("\n", " ") + "..."

# 🤖 MAIN BOT FUNCTION
def run_bot():
    print("\n🚀 Running Email Bot...\n")

    processed = set()  # prevent duplicates

    with IMAPClient('imap.gmail.com') as server:
        server.login(EMAIL, PASSWORD)
        server.select_folder('INBOX')

        # ✅ ONLY NEW EMAILS (no duplicates)
        messages = server.search(['UNSEEN'])
        messages = messages[-MAX_EMAILS:]

        print(f"📊 Processing {len(messages)} emails...\n")

        for i, uid in enumerate(messages, 1):

            if uid in processed:
                continue
            processed.add(uid)

            raw = server.fetch([uid], ['BODY[]'])
            message = pyzmail.PyzMessage.factory(raw[uid][b'BODY[]'])

            subject = message.get_subject()
            from_ = message.get_addresses('from')

            sender_email = from_[0][1] if from_ else "unknown"

            body = ""
            if message.text_part:
                body = message.text_part.get_payload().decode(errors='ignore')

            category = classify(body)
            action = "none"

            # 🛡️ SAFETY CHECK
            if sender_email not in TRUSTED_SENDERS:

                if category == "spam" and "unsubscribe" in body.lower():
                    server.delete_messages(uid)
                    action = "🗑️ DELETED (spam detected)"

                elif category == "important":
                    server.add_flags(uid, ['\\Flagged'])
                    action = "⭐ MARKED IMPORTANT"

            else:
                action = "🛡️ SKIPPED (trusted sender)"

            # 📺 CLEAN OUTPUT
            print(f"📧 Email #{i}")
            print(f"Subject   : {subject}")
            print(f"From      : {sender_email}")
            print(f"Category  : {category.upper()}")
            print(f"Summary   : {summarize(body)}")
            print(f"Action    : {action}")
            print("-" * 60)

        print("\n✅ Cycle completed.\n")


# 🔁 AUTO RUN LOOP
while True:
    run_bot()

    print("⏳ Waiting 1 hour before next check...\n")
    time.sleep(3600)
    
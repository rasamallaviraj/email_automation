from imapclient import IMAPClient
import pyzmail
import time
import smtplib
from email.mime.text import MIMEText
# 🔐 YOUR DETAILS
EMAIL = "rasamallaviraj0@gmail.com"
PASSWORD = "sfcp dplc safo yhwn"

# ⚙️ SETTINGS
TRUSTED_SENDERS = ["rasamallaviraj@gmail.com"]
MAX_EMAILS = 10
import requests

NEWS_API_KEY = "f91db2a781c04281bb9fbd9f5d94bba2"

def get_news():
    url = f"https://newsapi.org/v2/everything?q=India&sortBy=publishedAt&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()

    articles = response.get("articles", [])[:5]

    news_list = []
    for a in articles:
        title = a["title"]
        desc = a["description"] or ""
        news_list.append(f"{title} - {desc}")

    return news_list

def summarize_news(news_list):
    summary = "📰 TODAY'S NEWS:\n\n"
    for i, news in enumerate(news_list, 1):
        summary += f"{i}. {news[:100]}...\n\n"
    return summary
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
def run_news_bot():
    print("\n📰 Fetching News...\n")

    news = get_news()
    summary = summarize_news(news)

    print(summary)

    send_email(summary)
def send_email(content):
    msg = MIMEText(content)
    msg['Subject'] = "📰 News Update"
    msg['From'] = EMAIL
    msg['To'] = EMAIL

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(EMAIL, PASSWORD)
        server.send_message(msg)

    print("📩 News Email Sent!")
# 🔁 AUTO RUN LOOP
while True:
    run_bot()        # email cleaner
    run_news_bot()   # news feature

    print("⏳ Waiting 1 hour before next check...\n")
    time.sleep(3600)

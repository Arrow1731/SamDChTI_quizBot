from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import fitz 
import re
import asyncio

TOKEN = "8150813899:AAHX_DHOUXqtp_wR6-dYhrV1dBkvfXuOWyE"

def extract_quiz_questions(text):
    blocks = re.split(r"\n\s*\d+\.", text)
    questions = []
    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) >= 5:
            question = lines[0].strip()
            options = [line.strip()[3:] for line in lines[1:5]]
            if len(options) == 4:
                questions.append({
                    "question": question,
                    "options": options,
                    "correct_option_id": 0 
                })
    return questions

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Send a PDF file with quiz questions (format: A is the correct answer).")

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = update.message.document
    if file.mime_type != "application/pdf":
        await update.message.reply_text("⚠️ Only PDF files are supported.")
        return

    await update.message.reply_text("🔄 Processing your PDF file...")

    file_info = await file.get_file()
    file_bytes = await file_info.download_as_bytearray()
    doc = fitz.open(stream=file_bytes, filetype="pdf")

    text = ""
    for page in doc:
        text += page.get_text()

    questions = extract_quiz_questions(text)
    if not questions:
        await update.message.reply_text("❌ No valid questions found. Please check your file format.")
        return

    await update.message.reply_text(f"✅ Found {len(questions)} questions. Sending them one by one...")

    for i, q in enumerate(questions, start=1):
        try:
            await update.message.reply_poll(
                question=f"Q{i}. {q['question']}",
                options=q["options"],
                type='quiz',
                correct_option_id=q["correct_option_id"],
                is_anonymous=False,
                open_period=10 
            )
            await asyncio.sleep(11) 
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error sending quiz: {str(e)}")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.Document.PDF, handle_file))
    app.run_polling()

if __name__ == "__main__":
    main()



    
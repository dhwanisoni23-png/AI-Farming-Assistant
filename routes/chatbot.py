from flask import Blueprint, render_template, request, session, redirect, url_for
from services.chatbot_service import get_ai_response

chatbot_bp = Blueprint("chatbot", __name__)


def initialize_chat():
    """
    Initialize chat session if it doesn't exist.
    """
    if "messages" not in session:
        session["messages"] = [
            {
                "role": "assistant",
                "text": (
                    "👋 Hello!\n\n"
                    "I'm your AI Farming Assistant.\n\n"
                    "How can I help you today?"
                ),
            }
        ]
        session.modified = True


@chatbot_bp.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    initialize_chat()

    if request.method == "POST":

        question = request.form.get("message", "").strip()

        if question:

            # Save user message
            session["messages"].append(
                {
                    "role": "user",
                    "text": question,
                }
            )

            try:
                ai_reply = get_ai_response(question)

            except Exception as e:
                print(f"[Chatbot Error] {e}")

                ai_reply = (
                    "⚠️ Sorry, I'm currently unable to process your request. "
                    "Please try again in a few moments."
                )

            # Save AI response
            session["messages"].append(
                {
                    "role": "assistant",
                    "text": ai_reply,
                }
            )

            session.modified = True

        return redirect(url_for("chatbot.chatbot"))

    return render_template(
        "chatbot.html",
        messages=session["messages"],
    )


@chatbot_bp.route("/chatbot/clear")
def clear_chat():
    """
    Clear chat history.
    """

    session.pop("messages", None)

    return redirect(url_for("chatbot.chatbot"))
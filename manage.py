import sys
import os

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "train_chatbot":
        os.system("python energy/management/commands/train_chatbot.py")
    else:
        print("This is a proxy to emulate Django manage.py command.")
        print("Usage: python manage.py train_chatbot")

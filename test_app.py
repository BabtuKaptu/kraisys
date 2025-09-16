#!/usr/bin/env python3
"""Test script to check app initialization"""

import sys
import traceback
from PyQt6.QtWidgets import QApplication

def main():
    try:
        print("Starting application...")
        app = QApplication(sys.argv)

        print("Connecting to database...")
        from database.connection import DatabaseConnection
        db = DatabaseConnection()
        conn = db.get_connection()
        if conn:
            print("✓ Database connected successfully")
        else:
            print("✗ Failed to connect to database")
            return 1

        print("Loading ModelsTableFullWidget...")
        from ui.references.models_view_full import ModelsTableFullWidget
        widget = ModelsTableFullWidget()
        print("✓ ModelsTableFullWidget loaded successfully")

        print("Showing widget...")
        widget.show()

        print("Application started successfully!")
        return app.exec()

    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
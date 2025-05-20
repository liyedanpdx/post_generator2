#!/usr/bin/env python
"""
Simple script to run the Post Auto Editor API
"""
import os
import sys

def main():
    """Run the application"""
    print("Starting LinkedIn Post Auto Editor API...")
    
    # Check if the required directories exist
    if not os.path.exists('templates'):
        print("Error: 'templates' directory not found. Make sure you're running this script from the post_generator directory.")
        sys.exit(1)
    
    # Create generated_images directory if it doesn't exist
    if not os.path.exists('generated_images'):
        os.makedirs('generated_images')
        print("Created 'generated_images' directory.")
    
    # Run the Flask application
    from app import app
    app.run(debug=True, host='0.0.0.0', port=5000)

if __name__ == "__main__":
    main() 
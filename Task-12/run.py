"""
Run the Hadith Search Engine Flask Application

Usage:
    python run.py                    # Run in development mode
    python run.py --production       # Run in production mode
    python run.py --port 8000       # Run on custom port
    python run.py --host 0.0.0.0    # Listen on all interfaces
"""

import sys
import os
from app import app
from config import get_config


def main():
    """Main entry point for the application"""
    
    # Parse command line arguments
    port = 5000
    host = '127.0.0.1'
    debug = True
    env = 'development'
    
    for arg in sys.argv[1:]:
        if arg == '--production':
            debug = False
            env = 'production'
            host = '0.0.0.0'
        elif arg == '--debug':
            debug = True
            env = 'development'
        elif arg.startswith('--port'):
            try:
                port = int(arg.split('=')[1]) if '=' in arg else int(sys.argv[sys.argv.index(arg) + 1])
            except (ValueError, IndexError):
                print("Error: Invalid port number")
                sys.exit(1)
        elif arg.startswith('--host'):
            host = arg.split('=')[1] if '=' in arg else sys.argv[sys.argv.index(arg) + 1]
        elif arg in ['--help', '-h']:
            print(__doc__)
            sys.exit(0)
    
    # Set environment
    os.environ['FLASK_ENV'] = env
    
    # Load configuration
    config = get_config(env)
    app.config.from_object(config)
    
    # Display startup information
    print("\n" + "="*60)
    print("🕌 HADITH SEARCH ENGINE - Starting Up")
    print("="*60)
    print(f"Environment: {env.upper()}")
    print(f"Debug Mode: {debug}")
    print(f"Server: http://{host}:{port}")
    print(f"Process ID: {os.getpid()}")
    print("="*60 + "\n")
    
    # Load data
    print("Loading data...")
    from app import load_data
    load_data()
    
    # Run the application
    try:
        app.run(
            host=host,
            port=port,
            debug=debug,
            use_reloader=debug,
            use_debugger=debug
        )
    except KeyboardInterrupt:
        print("\n\n" + "="*60)
        print("⛔ Server stopped by user")
        print("="*60 + "\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error running server: {e}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

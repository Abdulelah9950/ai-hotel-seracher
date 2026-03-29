# Main Flask Application

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import FLASK_CONFIG
from api.routes import api_bp
import os


def create_app():
    """Create and configure the Flask application"""
    
    # Initialize Flask app with template and static folders pointing to frontend
    # Get the parent directory (project root)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    frontend_path = os.path.join(project_root, 'frontend')
    
    app = Flask(__name__,
                static_folder=frontend_path,
                static_url_path='')
    
    # Load configuration
    app.config['DEBUG'] = FLASK_CONFIG['DEBUG']
    
    # Enable CORS (still useful for development)
    CORS(app)
    
    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Root endpoint - Serve the chatbot HTML
    @app.route('/')
    def index():
        """Serve the main chatbot page"""
        return send_from_directory(frontend_path, 'chatbot.html')
    
    # Serve CSS files
    @app.route('/css/<path:filename>')
    def serve_css(filename):
        return send_from_directory(os.path.join(frontend_path, 'css'), filename)
    
    # Serve JS files
    @app.route('/js/<path:filename>')
    def serve_js(filename):
        return send_from_directory(os.path.join(frontend_path, 'js'), filename)
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return jsonify({
            'message': 'Hotel Booking AI API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'chat': '/api/chat [POST]',
                'hotels': '/api/hotels',
                'hotel_details': '/api/hotels/<id>',
                'nearby_hotels': '/api/hotels/nearby [POST]',
                'landmarks': '/api/landmarks'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # Check if it's an API request
        if '/api/' in str(error):
            return jsonify({'error': 'API endpoint not found'}), 404
        # Otherwise, serve the chatbot page (SPA fallback)
        return send_from_directory(frontend_path, 'chatbot.html')
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    app = create_app()
    
    print("\n" + "=" * 60)
    print("Hotel Booking AI API Starting...")
    print("=" * 60)
    print(f"Server running at: http://{FLASK_CONFIG['HOST']}:{FLASK_CONFIG['PORT']}")
    print("Available endpoints:")
    print("  - GET  /")
    print("  - GET  /api/health")
    print("  - POST /api/chat")
    print("  - GET  /api/hotels")
    print("  - GET  /api/hotels/<id>")
    print("  - POST /api/hotels/nearby")
    print("  - GET  /api/landmarks")
    print("=" * 60 + "\n")
    
    app.run(
        host=FLASK_CONFIG['HOST'],
        port=FLASK_CONFIG['PORT'],
        debug=FLASK_CONFIG['DEBUG']
    )
# This is the entry point for the backend server

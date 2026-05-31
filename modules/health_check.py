"""
Health Check Endpoint
Provides HTTP endpoint to check monitor status
Useful for load balancers and monitoring services
"""
from flask import Flask, jsonify
from datetime import datetime
from threading import Thread
from config import get_logger
import time

logger = get_logger(__name__)


class HealthCheckServer:
    """Simple health check HTTP server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        """
        Initialize health check server
        
        Args:
            host: Server host (0.0.0.0 = accessible from outside)
            port: Server port
        """
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.last_check_time = None
        self.last_check_status = None
        self.is_running = False
        
        # Setup routes
        self._setup_routes()
        
        logger.info(f"✓ Health Check Server initialized (http://{host}:{port})")
    
    def _setup_routes(self):
        """Setup Flask routes"""
        
        @self.app.route('/health', methods=['GET'])
        def health():
            """General health check endpoint"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'uptime': time.time(),
                'version': '1.0.0'
            }), 200
        
        @self.app.route('/health/detailed', methods=['GET'])
        def health_detailed():
            """Detailed health check with last check info"""
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'monitor': {
                    'last_check_time': self.last_check_time.isoformat() if self.last_check_time else None,
                    'last_check_status': self.last_check_status
                }
            }), 200
        
        @self.app.route('/health/ready', methods=['GET'])
        def ready():
            """Readiness check - returns 200 when monitor is ready"""
            if self.is_running:
                return jsonify({'ready': True}), 200
            else:
                return jsonify({'ready': False}), 503
        
        @self.app.route('/health/live', methods=['GET'])
        def live():
            """Liveness check - returns 200 if process is alive"""
            return jsonify({'live': True}), 200
        
        @self.app.errorhandler(404)
        def not_found(error):
            """Handle 404 errors"""
            return jsonify({'error': 'Endpoint not found'}), 404
    
    def update_status(self, last_check_time: datetime, status: dict):
        """
        Update monitor status (called by main monitor)
        
        Args:
            last_check_time: Timestamp of last check
            status: Dict with check results
        """
        self.last_check_time = last_check_time
        self.last_check_status = status
    
    def mark_ready(self):
        """Mark monitor as ready"""
        self.is_running = True
        logger.info("✓ Monitor marked as ready for checks")
    
    def run(self, debug: bool = False):
        """
        Run the health check server (blocks)
        
        Args:
            debug: Flask debug mode
        """
        try:
            # Suppress Flask logging for cleaner output
            import logging
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            
            logger.info(f"🏥 Health Check Server starting on http://{self.host}:{self.port}")
            self.app.run(
                host=self.host,
                port=self.port,
                debug=debug,
                use_reloader=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Health check server error: {e}")
    
    def start_async(self, debug: bool = False):
        """
        Start health check server in background thread
        
        Args:
            debug: Flask debug mode
        
        Returns:
            Thread object
        """
        thread = Thread(target=self.run, args=(debug,), daemon=True)
        thread.start()
        logger.info("✓ Health Check Server started in background")
        return thread

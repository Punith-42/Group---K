"""
Web Activity Tracking Flask Application.
This application provides APIs to store and retrieve web activity data.
"""

from flask import Flask, request, jsonify
import pymysql
from datetime import datetime, date
import logging
from dotenv import load_dotenv
from config import Config, DATABASE_CONFIG

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

def get_db_connection():
    """Get database connection with error handling."""
    try:
        conn = pymysql.connect(
            host=DATABASE_CONFIG['host'],
            database=DATABASE_CONFIG['database'],
            user=DATABASE_CONFIG['user'],
            password=DATABASE_CONFIG['password'],
            port=int(DATABASE_CONFIG['port']),
            charset='utf8mb4'
        )
        return conn
    except pymysql.Error as e:
        logger.error(f"Database connection error: {e}")
        raise

def validate_web_activity_data(data):
    """Validate web activity data."""
    required_fields = ['user_id', 'website_name', 'time_spent']
    
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate data types
    try:
        user_id = int(data['user_id'])
        time_spent = int(data['time_spent'])
        
        if user_id <= 0:
            return False, "user_id must be a positive integer"
        if time_spent < 0:
            return False, "time_spent must be non-negative"
        if not data['website_name'].strip():
            return False, "website_name cannot be empty"
            
    except (ValueError, TypeError):
        return False, "Invalid data types for user_id or time_spent"
    
    return True, None

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/api/store_web_activity', methods=['POST'])
def store_web_activity():
    """Store web activity data."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate data
        is_valid, error_msg = validate_web_activity_data(data)
        if not is_valid:
            return jsonify({"error": error_msg}), 400
        
        # Extract and prepare data
        user_id = int(data['user_id'])
        website_name = data['website_name'].strip()
        time_spent = int(data['time_spent'])
        activity_date = data.get('activity_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Validate date format
        try:
            datetime.strptime(activity_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO web_activity (user_id, website_name, time_spent, activity_date) 
            VALUES (%s, %s, %s, %s)
        ''', (user_id, website_name, time_spent, activity_date))
        
        # Get the last inserted ID and created_at
        inserted_id = cursor.lastrowid
        cursor.execute("SELECT created_at FROM web_activity WHERE id = %s", (inserted_id,))
        result = cursor.fetchone()
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Stored activity for user {user_id}: {website_name} - {time_spent} minutes")
        
        return jsonify({
            "message": "Activity stored successfully!",
            "id": inserted_id,
            "created_at": result[0].isoformat()
        }), 201
        
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/get_activity', methods=['GET'])
def get_activity():
    """Get web activity data for a specific user and date."""
    try:
        user_id = request.args.get('user_id')
        activity_date = request.args.get('date')
        
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        if not activity_date:
            activity_date = datetime.now().strftime('%Y-%m-%d')
        
        # Validate user_id
        try:
            user_id = int(user_id)
            if user_id <= 0:
                return jsonify({"error": "user_id must be a positive integer"}), 400
        except ValueError:
            return jsonify({"error": "user_id must be a valid integer"}), 400
        
        # Validate date format
        try:
            datetime.strptime(activity_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Query database
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT website_name, SUM(time_spent) as total_time_spent, COUNT(*) as visit_count
            FROM web_activity 
            WHERE user_id = %s AND activity_date = %s 
            GROUP BY website_name
            ORDER BY total_time_spent DESC
        ''', (user_id, activity_date))
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Convert to list of dictionaries
        activities = []
        total_time = 0
        
        for row in result:
            activity = {
                'website_name': row['website_name'],
                'total_time_spent': row['total_time_spent'],
                'visit_count': row['visit_count']
            }
            activities.append(activity)
            total_time += row['total_time_spent']
        
        return jsonify({
            "user_id": user_id,
            "date": activity_date,
            "total_time_spent": total_time,
            "activities": activities,
            "count": len(activities)
        }), 200
        
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/get_user_stats', methods=['GET'])
def get_user_stats():
    """Get user statistics for a date range."""
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        # Validate user_id
        try:
            user_id = int(user_id)
            if user_id <= 0:
                return jsonify({"error": "user_id must be a positive integer"}), 400
        except ValueError:
            return jsonify({"error": "user_id must be a valid integer"}), 400
        
        # Set default date range if not provided
        if not start_date:
            start_date = (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Validate date formats
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Query database
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT 
                website_name,
                SUM(time_spent) as total_time_spent,
                COUNT(*) as visit_count,
                activity_date
            FROM web_activity 
            WHERE user_id = %s AND activity_date BETWEEN %s AND %s
            GROUP BY website_name, activity_date
            ORDER BY activity_date DESC, total_time_spent DESC
        ''', (user_id, start_date, end_date))
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Process results
        stats = []
        total_time = 0
        
        for row in result:
            stat = {
                'website_name': row['website_name'],
                'total_time_spent': row['total_time_spent'],
                'visit_count': row['visit_count'],
                'date': row['activity_date'].strftime('%Y-%m-%d')
            }
            stats.append(stat)
            total_time += row['total_time_spent']
        
        return jsonify({
            "user_id": user_id,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_time_spent": total_time,
            "total_visits": len(result),
            "stats": stats
        }), 200
        
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/store_github_activity', methods=['POST'])
def store_github_activity():
    """Store GitHub activity data."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'github_username', 'activity_type']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Extract and prepare data
        user_id = int(data['user_id'])
        github_username = data['github_username'].strip()
        activity_type = data['activity_type'].strip()
        repository_name = data.get('repository_name', '').strip()
        activity_description = data.get('activity_description', '').strip()
        commit_count = int(data.get('commit_count', 0))
        activity_date = data.get('activity_date', datetime.now().strftime('%Y-%m-%d'))
        
        # Validate activity_type
        valid_types = ['commit', 'pull_request', 'issue', 'push', 'repository']
        if activity_type not in valid_types:
            return jsonify({"error": f"Invalid activity_type. Must be one of: {valid_types}"}), 400
        
        # Validate date format
        try:
            datetime.strptime(activity_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Store in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO github_activity (user_id, github_username, activity_type, repository_name, activity_description, commit_count, activity_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, github_username, activity_type, repository_name, activity_description, commit_count, activity_date))
        
        # Get the last inserted ID
        inserted_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Stored GitHub activity for user {user_id}: {activity_type} - {repository_name}")
        
        return jsonify({
            "message": "GitHub activity stored successfully!",
            "id": inserted_id,
            "activity_type": activity_type,
            "repository_name": repository_name
        }), 201
        
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/get_github_activity', methods=['GET'])
def get_github_activity():
    """Get GitHub activity data for a specific user and date."""
    try:
        user_id = request.args.get('user_id')
        activity_date = request.args.get('date')
        
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        if not activity_date:
            activity_date = datetime.now().strftime('%Y-%m-%d')
        
        # Validate user_id
        try:
            user_id = int(user_id)
            if user_id <= 0:
                return jsonify({"error": "user_id must be a positive integer"}), 400
        except ValueError:
            return jsonify({"error": "user_id must be a valid integer"}), 400
        
        # Validate date format
        try:
            datetime.strptime(activity_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Query database
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT 
                activity_type,
                repository_name,
                activity_description,
                commit_count,
                created_at
            FROM github_activity 
            WHERE user_id = %s AND activity_date = %s 
            ORDER BY created_at DESC
        ''', (user_id, activity_date))
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Process results
        activities = []
        total_commits = 0
        activity_summary = {}
        
        for row in result:
            activity = {
                'activity_type': row['activity_type'],
                'repository_name': row['repository_name'],
                'activity_description': row['activity_description'],
                'commit_count': row['commit_count'],
                'created_at': row['created_at'].isoformat()
            }
            activities.append(activity)
            total_commits += row['commit_count']
            
            # Count by activity type
            activity_type = row['activity_type']
            activity_summary[activity_type] = activity_summary.get(activity_type, 0) + 1
        
        return jsonify({
            "user_id": user_id,
            "date": activity_date,
            "total_activities": len(activities),
            "total_commits": total_commits,
            "activity_summary": activity_summary,
            "activities": activities
        }), 200
        
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route('/api/get_github_stats', methods=['GET'])
def get_github_stats():
    """Get GitHub statistics for a user over a date range."""
    try:
        user_id = request.args.get('user_id')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        if not user_id:
            return jsonify({"error": "user_id parameter is required"}), 400
        
        # Validate user_id
        try:
            user_id = int(user_id)
            if user_id <= 0:
                return jsonify({"error": "user_id must be a positive integer"}), 400
        except ValueError:
            return jsonify({"error": "user_id must be a valid integer"}), 400
        
        # Set default date range if not provided
        if not start_date:
            start_date = (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')
        
        # Validate date formats
        try:
            datetime.strptime(start_date, '%Y-%m-%d')
            datetime.strptime(end_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        
        # Query database
        conn = get_db_connection()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        
        cursor.execute('''
            SELECT 
                activity_type,
                repository_name,
                SUM(commit_count) as total_commits,
                COUNT(*) as activity_count,
                activity_date
            FROM github_activity 
            WHERE user_id = %s AND activity_date BETWEEN %s AND %s
            GROUP BY activity_type, repository_name, activity_date
            ORDER BY activity_date DESC, total_commits DESC
        ''', (user_id, start_date, end_date))
        
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Process results
        stats = []
        total_commits = 0
        total_activities = 0
        
        for row in result:
            stat = {
                'activity_type': row['activity_type'],
                'repository_name': row['repository_name'],
                'total_commits': row['total_commits'],
                'activity_count': row['activity_count'],
                'date': row['activity_date'].strftime('%Y-%m-%d')
            }
            stats.append(stat)
            total_commits += row['total_commits']
            total_activities += row['activity_count']
        
        return jsonify({
            "user_id": user_id,
            "date_range": {
                "start_date": start_date,
                "end_date": end_date
            },
            "total_commits": total_commits,
            "total_activities": total_activities,
            "stats": stats
        }), 200
        
    except pymysql.Error as e:
        logger.error(f"Database error: {e}")
        return jsonify({"error": "Database error occurred"}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle 405 errors."""
    return jsonify({"error": "Method not allowed"}), 405

if __name__ == '__main__':
    logger.info("Starting Web Activity Tracking API...")
    logger.info(f"Database: {DATABASE_CONFIG['database']} on {DATABASE_CONFIG['host']}")
    
    app.run(
        host=Config.API_HOST,
        port=Config.API_PORT,
        debug=True
    )

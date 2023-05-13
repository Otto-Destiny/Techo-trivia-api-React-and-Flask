import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    
    CORS(app, resources={r"/*": {"origins":"*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, PUT, POST, DELETE, OPTIONS')
        return response
    
    
    # Paginates a list of questions based on the current page number.
    def paginate(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page-1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        
        questions = [question.format() for question in selection]
        current_questions = questions[start:end]
        
        return current_questions

    
    @app.route('/questions', methods=['GET'])
    def get_all_questions():
            selection = Question.query.all()
            formatted_questions = paginate(request, selection)
            if len(formatted_questions) == 0:
                abort(404)
            
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'categories': [category.format() for category in Category.query.all()],
                'current_category': "ALL"
            })

    
    # An endpoint to handle GET requests for all available categories.
    @app.route('/categories', methods=['GET'])
    def categories():
        try:
            with app.app_context():
                selection = Category.query.all()
            if selection == 0:
                return jsonify({
                    'success': True,
                    'categories': [],
                    'No_of_categories': 0
                })
            formatted_categories = [category.format() for category in selection]
            return jsonify({
                'success': True,
                'categories': formatted_categories,
                'total_categories': len(selection)
            })
        except:
            abort(500)

    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """

    @app.route('/categories/<int:id>/questions', methods=['GET'])
    def get_questions_by_category(id):
        category_id = id #request.args.get('category', 0, type=int)
        with app.app_context():
            if category_id == 0:
                selection = Question.query.all()
            else:
                selection = Question.query.filter(Question.category==category_id).all()
            if selection is None:
                abort(404, "Category does not exist")
            formatted_questions = paginate(request, selection)
            
            category = Category.query.get(category_id)
            if category is None:
                abort(404, "Category does not exist")
            else:
                if category_id == 0:
                    selected_category = "All"
                else:
                    selected_category = category.format()         
            
            if len(selection) == 0:
                abort(404)
            if len(formatted_questions) == 0:
                return jsonify({
                    'success': True,
                    'questions': [],
                    'total_questions': 0,
                    'current_category': selected_category,
                    'categories': [category.format() for category in Category.query.all()]
                })
            return jsonify({
                'success': True,
                'questions': formatted_questions,
                'total_questions': len(formatted_questions),
                'current_category': selected_category,
                'categories': [category.format() for category in Category.query.all()]
                }), 200
        
    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            with app.app_context():
                question = Question.query.get(question_id)
                question.delete()
                
                selection = Question.query.all()
                formatted_questions = paginate(request, selection)
                # category_id = request.args.get('category', 1, type=int)
                # selected_category =  Category.query.get(category_id)
                
                if len(formatted_questions) == 0:
                    abort(404)
                
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': formatted_questions,
                'total_questions': len(selection),
                #'current_category': selected_category.format(),
                'categories': [category.format() for category in Category.query.all()]
                }), 200
        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question, which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, the form will clear and the question will 
    appear at the end of the last page of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        question = request.json.get('question')
        answer = request.json.get('answer')
        category = request.json.get('category')
        difficulty = request.json.get('difficulty')
        #if not (question and answer and category and difficulty):
        if not all([question, answer, category, difficulty]):
            abort(400, description= "missing required fields")
        try:
            with app.app_context():
                New_question = Question(question=question, answer=answer, category=category, difficulty=difficulty)
                New_question.insert()
                
                print(f"New Question created with id = {New_question.id}")
                
                selection = Question.query.all()
                formatted_questions = paginate(request, selection)
                category_id = request.args.get('category', type=int)
                if category_id is None:
                    selected_category = "All"
                else:
                    selected_category =  Category.query.get(category_id)
                
                if len(formatted_questions) == 0:
                    abort(404)

            return jsonify({
                'success': True,
                'created': New_question.id,
                'questions': formatted_questions,
                'total_questions': len(selection),
                'current_category': selected_category.format(),
                'categories': [category.format() for category in Category.query.all()]
                }), 201
        except Exception as e:
            print(f"Error creating new question: {e}")
            abort(500, description="Error creating new question") 
            
    '''
    Create a POST endpoint to get questions based on a search term. It should return any questions for whom the 
    search term is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include only question that include that string 
    within their question. Try using the word "title" to start.
    '''
    
    @app.route('/questions/search', methods=['GET'])
    def search_questions():
        query = request.args.get('search_term', '')
        if not query:
            abort(400, description='missing search_term parameter')
        search_results = []
        with app.app_context():
            questions = Question.query.filter(Question.question.ilike(f'%{query}%')).all()
            for question in questions:
                search_results.append(question)
            formatted_results = paginate(request, search_results)
            category_id = request.args.get('category', type=int)
            selected_category =  Category.query.get(category_id)
            
            current_category = selected_category.format() if selected_category is not None else None
                
            return jsonify({
                'success': True,
                'search_results': formatted_results,
                'total_questions': len(formatted_results),
                'current_category': current_category,
                'categories': [category.format() for category in Category.query.all()]
                }), 200


    """
    Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous 
    question parameters and return a random questions within the given category, if provided, and that is not 
    one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('category', None)
        print(quiz_category)
        try:
            if quiz_category is None or quiz_category['id'] == 0:
                questions = Question.query.all()
            else:
                questions = Question.query.filter_by(category=quiz_category['id']).all()
            
            available_questions = [question for question in questions if question.id not in previous_questions]
            if len(available_questions) > 0:
                question = random.choice(available_questions)
                return jsonify({
                    'success': True,
                    'question': question.format()
                })
            else:
                return jsonify({
                    'success': True,
                    'question': None
                })
        except:
            abort(422)
 
    """
    Create error handlers for all expected errors including 404 and 422.
    """
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "Resource Not Found"
        }), 404
        
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422
        
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400
    
    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
            "success": False,
            "error": 405,
            "message": "method not allowed"
        }), 405
  
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success": False,
            "error": 500,
            "message": "Internal Server Error"
        }), 500

  
    return app


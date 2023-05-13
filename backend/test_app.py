import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from unittest.mock import patch, Mock

from app import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgresql://{}:{}@{}/{}".format(
            "student", "student", "localhost:5432", self.database_name
        )

        # # binds the app to the current context
        # with self.app.app_context():
        #     self.db = SQLAlchemy()
        #     self.db.init_app(self.app)
        #     # create all tables
        #     self.db.create_all()
        
        self.new_question = {"question": "What year did World War I start?",
                              "answer": "1914",
                              "category": 4,
                              "difficulty": 3
                              }
        self.new_question2 = {"question": "What year did World War II start?",
                             "answer": "1914",
                            #  "category": ,
                             "difficulty": 3
                             }
    
    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_paginated_questions(self):
        """
        Test retrieving paginated questions from the database
        Sends a GET request to the '/questions' endpoint to retrieve paginated questions from the database.
        Asserts that the status code is 200, success is True, the response contains questions and total number of questions, 
        current_category is set to 'ALL', and there are 6 categories.
        """
        res = self.client().get("/questions")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], 'ALL')
        self.assertEqual(len(data['categories']), 6)
        

    def test_404_requesting_beyond_valid_page(self):
        """
        Test error handling when requesting beyond the valid page
        Sends a GET request to the '/questions' endpoint with an invalid page number to test error handling.
        Asserts that the status code is 404, success is False, and the message is 'Resource Not Found'.
        """
        res = self.client().get("/questions?page=100")#, json={'rating':1})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "Resource Not Found")
        
        
    def test_get_search_with_results(self):
        """
        Test searching the database and retrieving results
        Sends a GET request to the '/questions/search' endpoint with a search term that exists in the database.
        Asserts that the status code is 200, success is True, the response contains search results and the total number of questions, 
        current_category is set to None, and there are 6 categories.
        """
        res = self.client().get("/questions/search?search_term=which")#, json={'search': "Novel"})
        data = json.loads(res.data)
        #print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['search_results']), 7)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category'], None)
        self.assertEqual(len(data['categories']), 6)
        
                
    def test_get_search_without_results(self):
        """
        Test the GET '/questions/search' endpoint when no results are found
        Sends a GET request to the '/questions/search' endpoint with a search term that does not exist in the database.
        Asserts that the status code is 200, success is True, the response contains no search results, the total number of questions is 0, 
        current_category is set to None, and there are 6 categories.
        """
        res = self.client().get("/questions/search?search_term=Rocky")#, json={"search": "apple_jack"})
        data = json.loads(res.data)
        #print(data['questions'])
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertEqual(len(data["search_results"]), 0)
        self.assertEqual(data["total_questions"], 0)
        self.assertEqual(data['current_category'], None)
        self.assertEqual(len(data['categories']), 6)
        
    
    def test_get_categories(self):
        """"
        Test the GET '/categories' endpoint.
        Sends a GET request to '/categories' endpoint and checks the response.
        Asserts that the status code is 200, success is True, the number of categories is 6, and total_categories is True.
        """
        res = self.client().get("/categories")#, json={'search': "Novel"})
        data = json.loads(res.data)
        #print(data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['categories']), 6)
        self.assertTrue(data['total_categories'])
    
    def test_categories_invalid_endpoint(self):
        """
        Test the GET '/categories' endpoint with an invalid endpoint.
        Sends a GET request to '/categories/5' endpoint and checks the response.
        Asserts that the status code is 404, success is False, and the message is 'Resource Not Found'.
        """
        res = self.client().get('/categories/5')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')
        

    def test_get_questions_by_category(self):
        """
        Test getting questions by category.
        Sends a GET request to '/categories/2/questions' endpoint and checks the response.
        Asserts that the status code is 200, success is True, the number of questions is 4, total_questions is True,
        current_category ID is 2, and the number of categories is 6.
        """
        res = self.client().get('/categories/2/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 4)
        self.assertTrue(data['total_questions'])
        self.assertEqual(data['current_category']['id'], 2)
        self.assertEqual(len(data['categories']), 6)
        
    def test_404_get_questions_by_category(self):
        """
        Test getting questions by category with invalid category ID.
        Sends a GET request to '/categories/21/questions' endpoint and checks the response.
        Asserts that the status code is 404, success is False, and the message is 'Resource Not Found'.
        """
        res = self.client().get('/categories/21/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_create_new_questions(self):
        """
        Test creating a new question.
        It tests that the endpoint '/questions' can create a new question using the
        POST method. It also checks if the response contains the expected data after
        a question has been created.
        """
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(data['total_questions'], 30) #adjust this number by adding 1 before you run test each time
        self.assertEqual(data['current_category'], "All")
        self.assertEqual(len(data['categories']), 6)
        
    def test_fail_to_create_new_question_missing_fields(self):
        """
        Test creating a new question with missing fields that results in a bad request error.
        It tests that the endpoint '/questions' returns a 400 bad request error when a
        new question is created with missing fields.
        """
        res = self.client().post("/questions", json=self.new_question2)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')      
    

    def test_delete_question(self):
        """
        Test deleting a question and verifying its deletion.
        It tests that the endpoint '/questions/<int:question_id>' can delete a question
        using the DELETE method. It also checks if the response contains the expected
        data after a question has been deleted.
        """
        res = self.client().delete("/questions/28") #change this number before you run test each time
        data = json.loads(res.data)
        with self.app.app_context():
            question = Question.query.filter(Question.id == 28).one_or_none()
            
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 28)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)
        self.assertEqual(len(data['categories']), 6)
        
    def test_fail_to_delete_because_question_doesnt_exist(self):
        """
        Test deleting a question that doesn't exist and receiving an unprocessable entity error.
        It tests that the endpoint '/questions/<int:question_id>' returns a 422 unprocessable
        entity error when trying to delete a question that doesn't exist.
        """
        res = self.client().delete("/questions/1000")
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
        
    def test_get_quiz_questions(self):
        """
        Tests getting a new quiz question.
        Sends a POST request to '/quizzes' endpoint with previous questions and a category to get a new quiz question.
        Asserts that the status code is 200, success is True, and the response contains a new question.
        """
        res = self.client().post('/quizzes', json={'previous_questions': [30, 31, 32], "category":{'id':3}})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question'])
        
    def test_404_get_quiz_questions(self):
        """
        Tests getting a new quiz question with an invalid category.
        Sends a POST request to '/quizzes' endpoint with previous questions and an invalid category to get a new quiz question.
        Asserts that the status code is 422, success is False, and the message is 'unprocessable'.
        """
        res = self.client().post('/quizzes', json={'previous_questions': [1,4,7], 'category':'uty'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')



# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
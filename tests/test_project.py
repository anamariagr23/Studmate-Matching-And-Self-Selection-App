import json
from db_app import db
from werkzeug.security import generate_password_hash

def test_login_endpoint(test_client, init_database):
    #arrange
    from models.user import UserModel
    user = UserModel(email='test@example.com', password=generate_password_hash('password123'), id_role = 3)
    db.session.add(user)
    db.session.commit()
    
    #act
    response = test_client.get('/users')
    
    #assert
    assert len(json.loads(response.data)) == 1
    assert response.status_code == 200

def test_login_successful(test_client, init_database):
    #arrange
    from models.user import UserModel
    user = UserModel(email='test@example.com', password=generate_password_hash('password123'), id_role = 3)
    db.session.add(user)
    db.session.commit()
    
    login_data = {
        'email': 'test@example.com',
        'password':'password123'
    }

    #act
    response = test_client.post('/login', data=json.dumps(login_data), content_type='application/json')
    response_data = json.loads(response.data)

    #assert
    assert response.status_code == 200
    assert response_data['message'] == "Successfully fetched auth token"

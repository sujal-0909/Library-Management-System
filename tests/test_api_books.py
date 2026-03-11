import pytest
from src.models import db
from src.models.book import Book

@pytest.fixture
def sample_book(test_app):
    with test_app.app_context():
        book = Book(
            title="Clean Code",
            author="Robert C. Martin",
            isbn="9780132350884",
            category="Programming",
            publisher="Prentice Hall",
            publication_year=2008,
            total_copies=5,
            available_copies=5,
            shelf_location="A1"
        )
        db.session.add(book)
        db.session.commit()
        db.session.refresh(book)
        yield book

def test_get_all_books(client, sample_book, user_token):
    response = client.get('/api/books/', headers={
        'Authorization': f'Bearer {user_token}'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['total'] >= 1
    assert data['books'][0]['title'] == "Clean Code"

def test_admin_add_book(client, admin_token, test_app):
    response = client.post('/api/books/', 
    headers={
        'Authorization': f'Bearer {admin_token}'
    },
    json={
        "title": "Design Patterns",
        "author": "Erich Gamma",
        "isbn": "9780201633610",
        "category": "Programming",
        "publisher": "Addison-Wesley",
        "publication_year": 1994,
        "total_copies": 3,
        "shelf_location": "B2"
    })
    
    assert response.status_code == 201
    
    with test_app.app_context():
        book = Book.query.filter_by(isbn="9780201633610").first()
        assert book is not None
        assert book.title == "Design Patterns"

def test_regular_user_cannot_add_book(client, user_token):
    response = client.post('/api/books/', 
    headers={
        'Authorization': f'Bearer {user_token}'
    },
    json={
        "title": "Hacking Book",
        "author": "Hacker",
        "isbn": "0000000000",
        "category": "Hacking",
        "publisher": "Underground",
        "publication_year": 2024,
        "total_copies": 1,
        "shelf_location": "N/A"
    })
    
    assert response.status_code == 403
    assert 'Admin access required' in response.get_json()['error']

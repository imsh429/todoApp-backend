from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, Todo, User, Category
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'your-secret-key'

db.init_app(app)
jwt = JWTManager(app)

# ----------------------------
# 🔧 날짜 파싱 유틸
# ----------------------------
def parse_date(date_str):
    if date_str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
        except Exception as e:
            print(f"❌ 날짜 파싱 실패: {e}")
    return None

# ----------------------------
# ✅ To-do API
# ----------------------------

@app.route('/todos', methods=['GET'])
@jwt_required()
def get_todos():
    user_id = int(get_jwt_identity())
    category = request.args.get('category')

    query = Todo.query.filter_by(user_id=user_id)
    if category and category != '전체':
        query = query.filter_by(category=category)

    todos = query.all()
    return jsonify([
        {
            "id": t.id,
            "content": t.content,
            "is_done": t.is_done,
            "category": t.category,
            "start_date": str(t.start_date) if t.start_date else None,
            "deadline": str(t.deadline) if t.deadline else None
        } for t in todos
    ])


@app.route('/todos', methods=['POST'])
@jwt_required()
def create_todo():
    user_id = int(get_jwt_identity())
    data = request.json
    content = data.get('content')
    category = data.get('category', '전체')
    start_date = parse_date(data.get('start_date'))
    deadline = parse_date(data.get('deadline'))

    try:
        todo = Todo(
            content=content,
            user_id=user_id,
            category=category,
            start_date=start_date,
            deadline=deadline,
        )
        db.session.add(todo)
        db.session.commit()
        return jsonify({
            "id": todo.id,
            "content": todo.content,
            "is_done": todo.is_done,
            "category": todo.category,
            "start_date": str(todo.start_date),
            "deadline": str(todo.deadline)
        }), 201
    except Exception as e:
        db.session.rollback()
        print(f"🚨 Todo 저장 중 오류: {e}")
        return jsonify({'error': '할 일 추가 실패', 'detail': str(e)}), 500

@app.route('/todos/<int:todo_id>', methods=['PUT'])
@jwt_required()
def toggle_todo(todo_id):
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != user_id:
        return jsonify({'error': '권한이 없습니다'}), 403

    todo.is_done = not todo.is_done
    db.session.commit()
    return jsonify({
        "id": todo.id,
        "content": todo.content,
        "is_done": todo.is_done,
        "category": todo.category,
        "start_date": str(todo.start_date),
        "deadline": str(todo.deadline)
    })

@app.route('/todos/<int:todo_id>', methods=['DELETE'])
@jwt_required()
def delete_todo(todo_id):
    user_id = int(get_jwt_identity())
    todo = Todo.query.get_or_404(todo_id)
    if todo.user_id != user_id:
        return jsonify({'error': '권한이 없습니다'}), 403

    db.session.delete(todo)
    db.session.commit()
    return '', 204

# ----------------------------
# ✅ 카테고리 API
# ----------------------------

@app.route('/categories', methods=['GET'])
@jwt_required()
def get_categories():
    user_id = int(get_jwt_identity())
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([c.name for c in categories])

@app.route('/categories', methods=['POST'])
@jwt_required()
def add_category():
    user_id = int(get_jwt_identity())
    name = request.json.get('name')
    if not name:
        return jsonify({'error': '카테고리 이름은 필수입니다'}), 400

    if Category.query.filter_by(user_id=user_id, name=name).first():
        return jsonify({'error': '이미 존재하는 카테고리입니다'}), 409

    new_cat = Category(name=name, user_id=user_id)
    db.session.add(new_cat)
    db.session.commit()
    return jsonify({'name': new_cat.name}), 201

@app.route('/categories/<string:name>', methods=['DELETE'])
@jwt_required()
def delete_category(name):
    user_id = int(get_jwt_identity())
    cat = Category.query.filter_by(user_id=user_id, name=name).first()
    if not cat:
        return jsonify({'error': '존재하지 않는 카테고리'}), 404

    db.session.delete(cat)
    db.session.commit()
    return '', 204

# ----------------------------
# ✅ 인증 API
# ----------------------------

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': '이메일과 비밀번호는 필수입니다'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': '이미 가입된 이메일입니다'}), 409

    user = User(email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': '회원가입 성공'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': '이메일과 비밀번호는 필수입니다'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': '잘못된 이메일 또는 비밀번호입니다'}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        'accessToken': access_token,
        'user': {
            'id': user.id,
            'email': user.email
        }
    }), 200

# ----------------------------
# ✅ 실행
# ----------------------------

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

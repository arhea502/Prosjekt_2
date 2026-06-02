
from flask import (Flask, render_template, redirect,
                   url_for, request, flash, jsonify, abort)
from flask_sqlalchemy import SQLAlchemy
from flask_login import (LoginManager, UserMixin,
                         login_user, logout_user,
                         login_required, current_user)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import markdown as md
    

app = Flask(__name__)     
app.config['SECRET_KEY'] = '108158379'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))




# User model
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True,  nullable=False)
    password_hash = db.Column(db.String(200),                  nullable=False)
    ip_address    = db.Column(db.String(50))
    is_admin      = db.Column(db.Boolean, default=False) 

# Section model
class Section(db.Model):
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    emoji       = db.Column(db.String(10))
    topics      = db.relationship('Topic', backref='section', lazy=True,
                                  cascade='all, delete-orphan')

# Topic model   
class Topic(db.Model): 
    id         = db.Column(db.Integer, primary_key=True)
    title      = db.Column(db.String(100), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('section.id'), nullable=False)
    elements   = db.relationship('LearningElement', backref='topic', lazy=True,
                                 cascade='all, delete-orphan')

# LearningElement model
class LearningElement(db.Model):
    id             = db.Column(db.Integer, primary_key=True)
    topic_id       = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    type           = db.Column(db.String(20),  nullable=False)
    content        = db.Column(db.Text)
    question       = db.Column(db.Text)
    option_a       = db.Column(db.String(200))
    option_b       = db.Column(db.String(200))
    option_c       = db.Column(db.String(200)) 
    option_d       = db.Column(db.String(200))
    correct_answer = db.Column(db.String(1))
    answer_key     = db.Column(db.Text)

# Progress model
class Progress(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),             nullable=False)
    element_id = db.Column(db.Integer, db.ForeignKey('learning_element.id'), nullable=False)
    correct    = db.Column(db.Boolean)

# OpenAnswer model
class OpenAnswer(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),             nullable=False)
    element_id = db.Column(db.Integer, db.ForeignKey('learning_element.id'), nullable=False)
    answer     = db.Column(db.Text)

# TopicVisit model
class TopicVisit(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    user_id  = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)

with app.app_context():
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        db.session.add(User(
            username='admin',
            password_hash=generate_password_hash('admin123'),
            is_admin=True
        ))
        db.session.commit()

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form['username']).first()
        if user and check_password_hash(user.password_hash, request.form['password']):
            user.ip_address = request.remote_addr
            db.session.commit
            login_user(user)
            return redirect(url_for('index'))
        flash('Feil brukernavn eller passord', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.filter_by(username=username).first():
            flash('Brukernavnet er allerede tatt', 'error')
            return redirect(url_for('register'))
        db.session.add(User(
            username=username,
            password_hash=generate_password_hash(request.form['password']),
            is_admin=False,
            ip_address=request.remote_addr
        ))
        db.session.commit()
        login_user(User.query.filter_by(username=username).first())
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logg-ut')
@login_required
def logg_ut():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    sections = Section.query.all()
    return render_template('index.html', sections=sections)

@app.route('/section/<int:section_id>')
@login_required
def section(section_id):
    seksjon = Section.query.get_or_404(section_id)
    return render_template('section.html', section=seksjon)

@app.route('/topic/<int:topic_id>')
@login_required
def topic(topic_id):
    tema = Topic.query.get_or_404(topic_id)

    # Registrer første besøk
    if not TopicVisit.query.filter_by(user_id=current_user.id, topic_id=topic_id).first():
        db.session.add(TopicVisit(user_id=current_user.id, topic_id=topic_id))
        db.session.commit()

    # Sett av hvilke elementer brukeren har besvart
    answered_ids = {p.element_id for p in
                    Progress.query.filter_by(user_id=current_user.id).all()}
    open_answers = {a.element_id: a.answer for a in
                    OpenAnswer.query.filter_by(user_id=current_user.id).all()}

    # Konverter markdown til HTML
    elements_rendered = []
    for el in tema.elements:
        rendered = el.content
        if el.type == 'markdown':
            rendered = md.markdown(el.content or '',
                                   extensions=['fenced_code', 'tables'])
        elements_rendered.append((el, rendered))

    return render_template('topic.html',
        topic=tema,
        elements_rendered=elements_rendered,
        answered_ids=answered_ids,
        open_answers=open_answers)

@app.route('/profil')
@login_required
def profile():
    uid      = current_user.id
    answered = Progress.query.filter_by(user_id=uid).count()
    correct  = Progress.query.filter_by(user_id=uid, correct=True).count()
    visited  = TopicVisit.query.filter_by(user_id=uid).count()
    topic_stats = []
    for tema in Topic.query.all():
        total = len(tema.elements)
        if total == 0: continue
        done = Progress.query.filter_by(user_id=uid).join(LearningElement).filter(
            LearningElement.topic_id == tema.id).count()
        topic_stats.append({
            'topic': tema, 'done': done, 'total': total,
            'percent': int(done / total * 100)
        })
    return render_template('profile.html',
        answered=answered, correct=correct,
        visited=visited, topic_stats=topic_stats)

@app.route('/admin')
@admin_required
def admin_panel():
    sections = Section.query.all()
    topics   = Topic.query.all()
    return render_template('admin/panel.html', sections=sections, topics=topics)

@app.route('/admin/section/new', methods=['POST'])
@admin_required
def new_section():
    db.session.add(Section(title=request.form['title'],
                            description=request.form.get('description', ''),
                            emoji=request.form.get('emoji', '📚')))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/section/<int:sid>/delete', methods=['POST'])
@admin_required
def delete_section(sid):
    db.session.delete(Section.query.get_or_404(sid))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/topic/new', methods=['POST'])
@admin_required
def new_topic():
    db.session.add(Topic(title=request.form['title'],
                          section_id=request.form['section_id']))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/topic/<int:tid>/delete', methods=['POST'])
@admin_required
def delete_topic(tid):
    db.session.delete(Topic.query.get_or_404(tid))
    db.session.commit()
    return redirect(url_for('admin_panel'))
abcdefghijklmnopqrstuvwxyzæøå

@app.route('/admin/element/new', methods=['POST'])
@admin_required
def new_element():
    db.session.add(LearningElement(
        topic_id=request.form['topic_id'],
        type=request.form['type'],
        content=request.form.get('content', ''),
        question=request.form.get('question', ''),
        option_a=request.form.get('option_a', ''),
        option_b=request.form.get('option_b', ''),
        option_c=request.form.get('option_c', ''),
        option_d=request.form.get('option_d', ''),
        correct_answer=request.form.get('correct_answer', ''),
        answer_key=request.form.get('answer_key', '')
    ))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/element/<int:eid>/delete', methods=['POST'])
@admin_required
def delete_element(eid):
    db.session.delete(LearningElement.query.get_or_404(eid))
    db.session.commit()
    return redirect(url_for('admin_panel'))

@app.route('/admin/element/<int:eid>/answers')
@admin_required
def view_answers(eid):
    element = LearningElement.query.get_or_404(eid)
    if element.type == 'quiz':
        rows = [(User.query.get(p.user_id), p.correct)
                for p in Progress.query.filter_by(element_id=eid).all()]
    else:
        rows = [(User.query.get(a.user_id), a.answer)
                for a in OpenAnswer.query.filter_by(element_id=eid).all()]
    return render_template('admin/answers.html', element=element, rows=rows)

@app.route('/admin/setup', methods=['GET', 'POST'])
def admin_setup():
    if request.method == 'POST':
        admin = User.query.filter_by(is_admin=True).first()
        if admin:
            admin.username      = request.form['username']
            admin.password_hash = generate_password_hash(request.form['password'])
            db.session.commit()
            flash('Admin oppdatert!', 'success')
        return redirect(url_for('login'))
    return render_template('admin/setup.html')

if __name__ == '__main__':
    app.run(debug=True)



with app.app_context():
    Users = User.query.all()
    for u in Users:
        print(u.id, u.username, u.password_hash, u.is_admin, u.ip_address)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080,)
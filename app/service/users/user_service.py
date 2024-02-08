from app.models import User, Farmer, db

def register_user(user):
    test = User.query.filter_by(email=user.email).first()
    if test:
        return False, 'That email already exists.'
    else:
        db.session.add(user)
        db.session.commit()
        return True, 'Registration success!'
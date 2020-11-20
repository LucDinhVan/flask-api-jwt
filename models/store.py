from db import db


class StoreModel(db.Model):
    """
    Store model
    """
    __tablename__ = 'stores'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))

    # load các đối tượng liên quan
    items = db.relationship('ItemModel', lazy='dynamic')

    def __init__(self, name):
        """
        Ham khoi tao item
        """
        self.name = name

    def json(self):
        """
        Tra ve item json format
        """
        return {
            'id': self.id,
            'name': self.name,
            'items': [item.json() for item in self.items]
        }

    @classmethod
    def find_by_name(cls, name):
        # select * from tableName where name = name
        return cls.query.filter_by(name=name).first()

    @classmethod
    def find_all(cls):
        """
        Lấy hết các Stores
        """
        return cls.query.all()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

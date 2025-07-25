from flask import request, jsonify
from models.技术栈 import 技术栈

class 技术栈Controller:
    @staticmethod
    def create():
        data = request.get_json()
        new_技术栈 = 技术栈(**data)
        new_技术栈.save()
        return jsonify(new_技术栈.to_dict()), 201

    @staticmethod
    def get_all():
        技术栈s = 技术栈.query.all()
        return jsonify([技术栈.to_dict() for 技术栈 in 技术栈s])

    @staticmethod
    def get_one(id):
        技术栈 = 技术栈.query.get_or_404(id)
        return jsonify(技术栈.to_dict())

    @staticmethod
    def update(id):
        技术栈 = 技术栈.query.get_or_404(id)
        data = request.get_json()
        技术栈.update(**data)
        return jsonify(技术栈.to_dict())

    @staticmethod
    def delete(id):
        技术栈 = 技术栈.query.get_or_404(id)
        技术栈.delete()
        return jsonify({'message': '技术栈 deleted'})

from flask import request, jsonify
from models.数据模型 import 数据模型

class 数据模型Controller:
    @staticmethod
    def create():
        data = request.get_json()
        new_数据模型 = 数据模型(**data)
        new_数据模型.save()
        return jsonify(new_数据模型.to_dict()), 201

    @staticmethod
    def get_all():
        数据模型s = 数据模型.query.all()
        return jsonify([数据模型.to_dict() for 数据模型 in 数据模型s])

    @staticmethod
    def get_one(id):
        数据模型 = 数据模型.query.get_or_404(id)
        return jsonify(数据模型.to_dict())

    @staticmethod
    def update(id):
        数据模型 = 数据模型.query.get_or_404(id)
        data = request.get_json()
        数据模型.update(**data)
        return jsonify(数据模型.to_dict())

    @staticmethod
    def delete(id):
        数据模型 = 数据模型.query.get_or_404(id)
        数据模型.delete()
        return jsonify({'message': '数据模型 deleted'})

from flask import request, jsonify
from models.api 端点 import API 端点

class API 端点Controller:
    @staticmethod
    def create():
        data = request.get_json()
        new_api 端点 = API 端点(**data)
        new_api 端点.save()
        return jsonify(new_api 端点.to_dict()), 201

    @staticmethod
    def get_all():
        api 端点s = API 端点.query.all()
        return jsonify([api 端点.to_dict() for api 端点 in api 端点s])

    @staticmethod
    def get_one(id):
        api 端点 = API 端点.query.get_or_404(id)
        return jsonify(api 端点.to_dict())

    @staticmethod
    def update(id):
        api 端点 = API 端点.query.get_or_404(id)
        data = request.get_json()
        api 端点.update(**data)
        return jsonify(api 端点.to_dict())

    @staticmethod
    def delete(id):
        api 端点 = API 端点.query.get_or_404(id)
        api 端点.delete()
        return jsonify({'message': 'API 端点 deleted'})

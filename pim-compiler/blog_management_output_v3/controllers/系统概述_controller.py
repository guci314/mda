from flask import request, jsonify
from models.系统概述 import 系统概述

class 系统概述Controller:
    @staticmethod
    def create():
        data = request.get_json()
        new_系统概述 = 系统概述(**data)
        new_系统概述.save()
        return jsonify(new_系统概述.to_dict()), 201

    @staticmethod
    def get_all():
        系统概述s = 系统概述.query.all()
        return jsonify([系统概述.to_dict() for 系统概述 in 系统概述s])

    @staticmethod
    def get_one(id):
        系统概述 = 系统概述.query.get_or_404(id)
        return jsonify(系统概述.to_dict())

    @staticmethod
    def update(id):
        系统概述 = 系统概述.query.get_or_404(id)
        data = request.get_json()
        系统概述.update(**data)
        return jsonify(系统概述.to_dict())

    @staticmethod
    def delete(id):
        系统概述 = 系统概述.query.get_or_404(id)
        系统概述.delete()
        return jsonify({'message': '系统概述 deleted'})

from flask_restful import Resource
from models.survey import SurveyModel


class SurveyResource(Resource):
    def get(self, survey_id):
        survey = SurveyModel.query.get(survey_id)
        if not survey:
            return {"message": "Survey not found"}, 404

        survey_data = {
            "survey_id": survey.id,
            "title": survey.title,
            "questions": [
                {
                    "question_id": question.id,
                    "description": question.description,
                    "multiple_choice": question.multiple_choice,
                    "choices": [
                        {"choice_id": choice.id, "description": choice.description}
                        for choice in question.answer_choices
                    ]
                } for question in survey.questions
            ]
        }

        return survey_data


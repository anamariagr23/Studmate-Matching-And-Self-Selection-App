# from sentence_transformers import SentenceTransformer, util
# from models.category_student_self_description import CategoryStudentSelfDescriptionModel
# from models.student import StudentModel
#
#
# class CompatibilityCalculator:
#     def __init__(self):
#         self.model = SentenceTransformer('all-MiniLM-L6-v2')
#
#     def get_student_scores(self, user_id):
#         user_descriptions = CategoryStudentSelfDescriptionModel.query.filter_by(student_id=user_id).all()
#         user = StudentModel.query.filter_by(id=user_id).first()
#         # Retrieve other students' descriptions
#         other_students_descriptions = CategoryStudentSelfDescriptionModel.query.join(StudentModel).filter(
#             StudentModel.dorm_id == user.dorm_id,
#             StudentModel.id_sex == user.id_sex,
#             CategoryStudentSelfDescriptionModel.student_id != user_id
#         ).all()
#
#         # Prepare data for comparison
#         user_data = {desc.category_id: {'answer': desc.answer, 'importance': desc.importance_score}
#                      for desc in user_descriptions}
#         other_data = {}
#         for desc in other_students_descriptions:
#             if desc.student_id not in other_data:
#                 other_data[desc.student_id] = {}
#             other_data[desc.student_id][desc.category_id] = {'answer': desc.answer, 'importance': desc.importance_score}
#
#         # Compute compatibility scores
#         scores = {}
#         for other_id, categories in other_data.items():
#             if other_id not in scores:
#                 scores[other_id] = {}
#                 total_similarity = 0
#                 total_importance = 0
#             for category_id, other_info in categories.items():
#                 if category_id in user_data:
#                     # Compute the similarity using Sentence Transformers
#                     user_answer = user_data[category_id]['answer']
#                     other_answer = other_info['answer']
#                     user_embedding = self.model.encode(user_answer, convert_to_tensor=True)
#                     other_embedding = self.model.encode(other_answer, convert_to_tensor=True)
#                     similarity = util.pytorch_cos_sim(user_embedding, other_embedding).item()
#                     # Compute the score and update scores dictionary
#                     importance_diff = user_data[category_id]['importance'] - other_info['importance']
#                     adjusted_similarity = similarity * ((10 - 0.3 * (abs(importance_diff + 1 if importance_diff == 0 else importance_diff)))/10)
#                     scores[other_id][category_id] = adjusted_similarity
#                     # Accumulate total similarity and importance for weighted mean calculation
#                     total_similarity += adjusted_similarity * user_data[category_id]['importance']
#                     total_importance += user_data[category_id]['importance']
#             scores[other_id]['total_score'] = total_similarity / total_importance
#
#         return scores


from sentence_transformers import SentenceTransformer, util
from models.category_student_self_description import CategoryStudentSelfDescriptionModel
from models.student import StudentModel
from models.status import StatusModel
from models.major import MajorModel
from models.category import CategoryModel

class CompatibilityCalculator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_student_scores(self, user_id):
        # Retrieve the user's details
        user = StudentModel.query.filter_by(id=user_id).first()
        user_descriptions = CategoryStudentSelfDescriptionModel.query.filter_by(student_id=user_id).all()

        # Retrieve other students' descriptions who have the same dorm ID and sex
        other_students_descriptions = CategoryStudentSelfDescriptionModel.query.join(StudentModel).filter(
            StudentModel.dorm_id == user.dorm_id,
            StudentModel.id_sex == user.id_sex,
            CategoryStudentSelfDescriptionModel.student_id != user_id
        ).all()

        # Prepare data for comparison
        user_data = {desc.category_id: {'answer': desc.answer, 'importance': desc.importance_score}
                     for desc in user_descriptions}
        other_data = {}
        for desc in other_students_descriptions:
            if desc.student_id not in other_data:
                other_data[desc.student_id] = {}
            other_data[desc.student_id][desc.category_id] = {'answer': desc.answer, 'importance': desc.importance_score}

        # Compute compatibility scores
        scores = {}
        for other_id, categories in other_data.items():
            if other_id not in scores:
                scores[other_id] = {}
                total_similarity = 0
                total_importance = 0
            for category_id, other_info in categories.items():
                if category_id in user_data:
                    # Compute the similarity using Sentence Transformers
                    user_answer = user_data[category_id]['answer']
                    other_answer = other_info['answer']
                    user_embedding = self.model.encode(user_answer, convert_to_tensor=True)
                    other_embedding = self.model.encode(other_answer, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(user_embedding, other_embedding).item()
                    # Compute the score and update scores dictionary
                    importance_diff = user_data[category_id]['importance'] - other_info['importance']
                    adjusted_similarity = similarity * ((10 - 0.3 * (abs(importance_diff + 1 if importance_diff == 0 else importance_diff)))/10)
                    scores[other_id][category_id] = adjusted_similarity
                    # Accumulate total similarity and importance for weighted mean calculation
                    total_similarity += adjusted_similarity * user_data[category_id]['importance']
                    total_importance += user_data[category_id]['importance']
            scores[other_id]['total_score'] = total_similarity / total_importance if total_importance else 0

        # Retrieve all category names
        categories = CategoryModel.query.order_by(CategoryModel.id).all()
        category_dict = {category.id: category.title for category in categories}

        # Retrieve additional student details
        students_details = StudentModel.query.filter(StudentModel.id.in_(scores.keys())).all()
        student_scores_with_details = []
        for student in students_details:
            student_scores_with_details.append({
                'id': student.id,
                'firstname': student.firstname,
                'lastname': student.lastname,
                'status': student.status.name if student.status else None,
                'major': student.major.name if student.major else None,
                'year_of_study': student.year_of_study,
                'description': student.description,
                'avatar_link': student.avatar_link,
                'total_score': scores[student.id]['total_score'],
                'categories': [{'category': category_dict[cat_id], 'score': score} for cat_id, score in scores[student.id].items() if cat_id != 'total_score']
            })

        return student_scores_with_details


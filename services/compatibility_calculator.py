from sentence_transformers import SentenceTransformer, util
from models.category_student_self_description import CategoryStudentSelfDescriptionModel


class CompatibilityCalculator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')

    def get_student_scores(self, user_id):
        user_descriptions = CategoryStudentSelfDescriptionModel.query.filter_by(student_id=user_id).all()
        # Retrieve other students' descriptions
        other_students_descriptions = CategoryStudentSelfDescriptionModel.query.filter(
            CategoryStudentSelfDescriptionModel.student_id != user_id).all()

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
            scores[other_id]['total_score'] = total_similarity / total_importance

        return scores

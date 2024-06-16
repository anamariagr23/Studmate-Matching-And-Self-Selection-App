

from sentence_transformers import SentenceTransformer, util
from models.category_student_self_description import CategoryStudentSelfDescriptionModel
from models.student import StudentModel
from models.status import StatusModel
from models.major import MajorModel
from models.category import CategoryModel
from db_app import db  # Ensure this import is present
import re
from nltk.stem import PorterStemmer

class CompatibilityCalculator:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.stemmer = PorterStemmer()

    def _stem_and_split(self, text):
        """
        Helper function to stem and split text into words.
        """
        return [self.stemmer.stem(word) for word in re.findall(r'\b\w+\b', text.lower())]

    def _needs_context(self, answer, category_title):
        """
        Determines if the answer needs context by checking if it mentions stemmed keywords from the category title.
        """
        category_keywords = self._stem_and_split(category_title)
        answer_keywords = self._stem_and_split(answer)
        # Check if there's any overlap between stemmed category keywords and stemmed answer keywords
        return not any(keyword in answer_keywords for keyword in category_keywords)

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

        # Retrieve all category names
        categories = CategoryModel.query.order_by(CategoryModel.id).all()
        category_dict = {category.id: category.title for category in categories}

        # Prepare data for comparison (for score computation)
        user_data_computation = {desc.category_id: {'answer': f"{category_dict[desc.category_id]}: {desc.answer}" if self._needs_context(desc.answer, category_dict[desc.category_id]) else desc.answer, 'importance': desc.importance_score}
                     for desc in user_descriptions}
        other_data_computation = {}
        for desc in other_students_descriptions:
            if desc.student_id not in other_data_computation:
                other_data_computation[desc.student_id] = {}
            other_data_computation[desc.student_id][desc.category_id] = {'answer': f"{category_dict[desc.category_id]}: {desc.answer}" if self._needs_context(desc.answer, category_dict[desc.category_id]) else desc.answer, 'importance': desc.importance_score}

        # Compute compatibility scores
        scores = {}
        for other_id, categories in other_data_computation.items():
            if other_id not in scores:
                scores[other_id] = {}
                total_similarity = 0
                total_importance = 0
            for category_id, other_info in categories.items():
                if category_id in user_data_computation:
                    # Compute the similarity using Sentence Transformers
                    user_answer = user_data_computation[category_id]['answer']
                    other_answer = other_info['answer']
                    user_embedding = self.model.encode(user_answer, convert_to_tensor=True)
                    other_embedding = self.model.encode(other_answer, convert_to_tensor=True)
                    similarity = util.pytorch_cos_sim(user_embedding, other_embedding).item()
                    # Compute the score and update scores dictionary
                    importance_diff = user_data_computation[category_id]['importance'] - other_info['importance']
                    adjusted_similarity = similarity * ((10 - 0.3 * (abs(importance_diff + 1 if importance_diff == 0 else importance_diff)))/10)
                    scores[other_id][category_id] = adjusted_similarity
                    # Accumulate total similarity and importance for weighted mean calculation
                    total_similarity += adjusted_similarity * user_data_computation[category_id]['importance']
                    total_importance += user_data_computation[category_id]['importance']
            scores[other_id]['total_score'] = total_similarity / total_importance if total_importance else 0

        # Prepare data for returning (with original answers)
        user_data_return = {desc.category_id: {'answer': desc.answer, 'importance': desc.importance_score}
                            for desc in user_descriptions}
        other_data_return = {}
        for desc in other_students_descriptions:
            if desc.student_id not in other_data_return:
                other_data_return[desc.student_id] = {}
            other_data_return[desc.student_id][desc.category_id] = {'answer': desc.answer, 'importance': desc.importance_score}

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
                'categories': [{'category': category_dict[cat_id], 'score': score, 'answer': other_data_return[student.id][cat_id]['answer']}
                               for cat_id, score in scores[student.id].items() if cat_id != 'total_score']
            })

        return student_scores_with_details

    def get_student_score_with_specific_student(self, user_id, specific_student_id):
        # Retrieve the user's details and descriptions
        user = StudentModel.query.filter_by(id=user_id).first()
        user_descriptions = CategoryStudentSelfDescriptionModel.query.filter_by(student_id=user_id).all()

        # Retrieve the specific student's details and descriptions
        specific_student = StudentModel.query.filter_by(id=specific_student_id).first()
        specific_student_descriptions = CategoryStudentSelfDescriptionModel.query.filter_by(
            student_id=specific_student_id).all()

        if not specific_student or not specific_student_descriptions:
            return None

        # Retrieve all category names
        categories = CategoryModel.query.order_by(CategoryModel.id).all()
        category_dict = {category.id: category.title for category in categories}

        # Prepare data for comparison (for score computation)
        user_data_computation = {desc.category_id: {'answer': f"{category_dict[desc.category_id]}: {desc.answer}" if self._needs_context(desc.answer, category_dict[desc.category_id]) else desc.answer, 'importance': desc.importance_score}
                     for desc in user_descriptions}
        specific_student_data_computation = {desc.category_id: {'answer': f"{category_dict[desc.category_id]}: {desc.answer}" if self._needs_context(desc.answer, category_dict[desc.category_id]) else desc.answer, 'importance': desc.importance_score}
                                 for desc in specific_student_descriptions}

        # Compute compatibility score
        total_similarity = 0
        total_importance = 0
        category_scores = []
        for category_id, other_info in specific_student_data_computation.items():
            if category_id in user_data_computation:
                # Compute the similarity using Sentence Transformers
                user_answer = user_data_computation[category_id]['answer']
                other_answer = other_info['answer']
                user_embedding = self.model.encode(user_answer, convert_to_tensor=True)
                other_embedding = self.model.encode(other_answer, convert_to_tensor=True)
                similarity = util.pytorch_cos_sim(user_embedding, other_embedding).item()
                # Compute the score
                importance_diff = user_data_computation[category_id]['importance'] - other_info['importance']
                adjusted_similarity = similarity * (
                            (10 - 0.3 * (abs(importance_diff + 1 if importance_diff == 0 else importance_diff))) / 10)
                category_scores.append({'category_id': category_id, 'adjusted_similarity': adjusted_similarity,
                                        'answer': other_info['answer']})
                # Accumulate total similarity and importance for weighted mean calculation
                total_similarity += adjusted_similarity * user_data_computation[category_id]['importance']
                total_importance += user_data_computation[category_id]['importance']

        total_score = total_similarity / total_importance if total_importance else 0

        # Prepare data for returning (with original answers)
        user_data_return = {desc.category_id: {'answer': desc.answer, 'importance': desc.importance_score}
                            for desc in user_descriptions}
        specific_student_data_return = {desc.category_id: {'answer': desc.answer, 'importance': desc.importance_score}
                                 for desc in specific_student_descriptions}

        return {
            'total_score': total_score,
            'categories': [{'category': category_dict[cat['category_id']], 'score': cat['adjusted_similarity'],
                            'answer': specific_student_data_return[cat['category_id']]['answer']} for cat in category_scores]
        }

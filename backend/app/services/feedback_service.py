"""
Service for generating automated feedback based on pronunciation assessment
"""

from typing import Dict, List, Optional


class FeedbackService:
    """Generate automated feedback from pronunciation scores"""

    @staticmethod
    def generate_feedback(assessment_result: Dict, word_text: str) -> Dict:
        """
        Generate automated feedback based on pronunciation assessment

        Args:
            assessment_result: Result from pronunciation assessment
            word_text: The word that was pronounced

        Returns:
            Dictionary with feedback text and grade
        """
        if not assessment_result or 'pronunciation_score' not in assessment_result:
            return {
                "feedback_text": "Unable to assess pronunciation. Please try recording again.",
                "grade": "N/A",
                "is_automated": True
            }

        pronunciation_score = assessment_result.get('pronunciation_score', 0)
        accuracy_score = assessment_result.get('accuracy_score', 0)
        fluency_score = assessment_result.get('fluency_score', 0)
        completeness_score = assessment_result.get('completeness_score', 0)

        # Determine grade based on pronunciation score
        grade = FeedbackService._calculate_grade(pronunciation_score)

        # Generate detailed feedback
        feedback_parts = []

        # Overall performance
        if pronunciation_score >= 90:
            feedback_parts.append(f"Excellent pronunciation of '{word_text}'! 🌟")
        elif pronunciation_score >= 80:
            feedback_parts.append(f"Great job on '{word_text}'! You're doing very well.")
        elif pronunciation_score >= 70:
            feedback_parts.append(f"Good effort on '{word_text}'. You're making progress!")
        elif pronunciation_score >= 60:
            feedback_parts.append(f"Nice try with '{word_text}'. Keep practicing!")
        else:
            feedback_parts.append(f"Keep working on '{word_text}'. Practice makes perfect!")

        # Specific areas to improve
        areas_to_improve = []
        strengths = []

        if accuracy_score < 70:
            areas_to_improve.append("pronunciation accuracy")
        elif accuracy_score >= 85:
            strengths.append("accurate pronunciation")

        if fluency_score < 70:
            areas_to_improve.append("fluency and rhythm")
        elif fluency_score >= 85:
            strengths.append("smooth fluency")

        if completeness_score < 80:
            areas_to_improve.append("completing the full word clearly")
        elif completeness_score >= 90:
            strengths.append("clear articulation")

        # Add strengths
        if strengths:
            feedback_parts.append(f"Strengths: {', '.join(strengths)}.")

        # Add areas to improve
        if areas_to_improve:
            feedback_parts.append(f"Focus on: {', '.join(areas_to_improve)}.")

        # Phoneme-level feedback
        phoneme_feedback = FeedbackService._analyze_phonemes(assessment_result)
        if phoneme_feedback:
            feedback_parts.append(phoneme_feedback)

        # Encouragement and next steps
        if pronunciation_score < 70:
            feedback_parts.append("💡 Tip: Listen to the model pronunciation and try to match the sounds carefully.")
        elif pronunciation_score < 85:
            feedback_parts.append("💡 Tip: You're close! Pay attention to the stress and rhythm of the word.")
        else:
            feedback_parts.append("Keep up the excellent work!")

        feedback_text = " ".join(feedback_parts)

        return {
            "feedback_text": feedback_text,
            "grade": grade,
            "is_automated": True
        }

    @staticmethod
    def _calculate_grade(score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= 95:
            return "A+"
        elif score >= 90:
            return "A"
        elif score >= 85:
            return "A-"
        elif score >= 80:
            return "B+"
        elif score >= 75:
            return "B"
        elif score >= 70:
            return "B-"
        elif score >= 65:
            return "C+"
        elif score >= 60:
            return "C"
        elif score >= 55:
            return "C-"
        elif score >= 50:
            return "D"
        else:
            return "F"

    @staticmethod
    def _analyze_phonemes(assessment_result: Dict) -> Optional[str]:
        """Analyze phoneme-level results and provide specific feedback"""
        if 'words' not in assessment_result or not assessment_result['words']:
            return None

        words = assessment_result['words']
        problem_phonemes = []

        for word in words:
            if 'phonemes' not in word:
                continue

            for phoneme in word['phonemes']:
                phoneme_score = phoneme.get('accuracy_score', 100)
                if phoneme_score < 60:
                    phoneme_text = phoneme.get('phoneme', '').strip()
                    if phoneme_text and phoneme_text not in problem_phonemes:
                        problem_phonemes.append(phoneme_text)

        if problem_phonemes:
            # Limit to first 3 problem phonemes to keep feedback concise
            problem_phonemes = problem_phonemes[:3]
            phoneme_list = ', '.join([f"/{p}/" for p in problem_phonemes])
            return f"Pay special attention to these sounds: {phoneme_list}."

        return None

    @staticmethod
    def enhance_feedback_with_teacher_notes(
        automated_feedback: str,
        teacher_notes: str
    ) -> str:
        """
        Combine automated feedback with teacher's additional notes

        Args:
            automated_feedback: Original automated feedback
            teacher_notes: Teacher's additional comments

        Returns:
            Combined feedback text
        """
        if not teacher_notes or teacher_notes.strip() == "":
            return automated_feedback

        return f"{automated_feedback}\n\n👨‍🏫 Teacher's Note: {teacher_notes}"


# Singleton instance
feedback_service = FeedbackService()

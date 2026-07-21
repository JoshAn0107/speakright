"""
Service for generating automated feedback based on pronunciation assessment
"""

from typing import Dict, List, Optional


class FeedbackService:
    """Generate automated feedback from pronunciation scores"""

    # Performance level thresholds (for feedback messages)
    EXCELLENT_THRESHOLD = 90
    GREAT_THRESHOLD = 80
    GOOD_THRESHOLD = 70
    OKAY_THRESHOLD = 60

    # Grade calculation boundaries
    GRADE_A_PLUS_THRESHOLD = 95
    GRADE_A_THRESHOLD = 90
    GRADE_A_MINUS_THRESHOLD = 85
    GRADE_B_PLUS_THRESHOLD = 80
    GRADE_B_THRESHOLD = 75
    GRADE_B_MINUS_THRESHOLD = 70
    GRADE_C_PLUS_THRESHOLD = 65
    GRADE_C_THRESHOLD = 60
    GRADE_C_MINUS_THRESHOLD = 55
    GRADE_D_THRESHOLD = 50

    # Component score thresholds
    ACCURACY_LOW_THRESHOLD = 70
    ACCURACY_HIGH_THRESHOLD = 85
    FLUENCY_LOW_THRESHOLD = 70
    FLUENCY_HIGH_THRESHOLD = 85
    COMPLETENESS_LOW_THRESHOLD = 80
    COMPLETENESS_HIGH_THRESHOLD = 90

    # Phoneme analysis thresholds
    PHONEME_PROBLEM_THRESHOLD = 60
    MAX_PHONEME_FEEDBACK_COUNT = 3

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
                "feedback_text": "无法评估发音，请重新录音。",
                "grade": "N/A",
                "is_automated": True
            }

        if assessment_result.get('error'):
            return {
                "feedback_text": "自动评分暂时失败，本次录音已保留，老师会人工评分；你也可以重新录一次。",
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
        if assessment_result.get('fallback'):
            feedback_parts.append("（备用评分：主评分服务繁忙，本次由本地模型评分，仅供参考）")

        # Prosody: point out stress/intonation problems explicitly
        prosody_score = assessment_result.get('prosody_score')

        if assessment_result.get('scorer') == 'xfyun':
            omitted = [w['word'] for w in assessment_result.get('words', []) if w.get('error_type') == 'Omission']
            if assessment_result.get('rejected'):
                feedback_parts.append(f"⚠️ 没听清你读的是不是“{word_text}”，请靠近麦克风重读。")
            elif omitted:
                feedback_parts.append(f"⚠️ 漏读了：{'、'.join(omitted[:8])}。")
            grade = FeedbackService._calculate_grade(pronunciation_score)
            if pronunciation_score >= 85:
                feedback_parts.append(f"“{word_text}”发音很棒！🌟")
            elif pronunciation_score >= 70:
                feedback_parts.append(f"“{word_text}”不错，继续保持！")
            elif pronunciation_score >= 60:
                feedback_parts.append(f"“{word_text}”还可以，多听示范再练几遍。")
            else:
                feedback_parts.append(f"“{word_text}”需要加强，跟着示范一个音一个音地读。")
            return {"feedback_text": " ".join(feedback_parts), "grade": grade, "is_automated": True}

        # Recognized text mismatch: the strongest signal that the wrong word was read
        if assessment_result.get('text_match') is False:
            recognized = (assessment_result.get('heard_text') or assessment_result.get('recognized_text') or '').strip().rstrip('.')
            if recognized:
                feedback_parts.append(
                    f"⚠️ 系统听到的更像“{recognized}”，而不是“{word_text}”。请听示范发音后重读。"
                )
            else:
                feedback_parts.append(f"⚠️ 系统没有听清你读的是不是“{word_text}”，请重读。")
        elif (assessment_result.get('gop_similarity') is not None
              and assessment_result['gop_similarity'] < 0.55
              and (assessment_result.get('phoneme_mean') or 100) <= 82
              and assessment_result.get('text_match') is not False):
            heard = (assessment_result.get('gop_heard') or '').strip()
            feedback_parts.append(
                f"⚠️ 发音和标准读音有明显差距{f'（系统听到的更接近“{heard}”）' if heard else ''}。放慢速度，听示范音逐个音节模仿。"
            )
        elif (assessment_result.get('stress_check') or {}).get('match') is False:
            sc = assessment_result['stress_check']
            syllables = sc.get('syllables') or []
            exp_i, got_i = sc.get('expected_syllable'), sc.get('predicted_syllable')
            exp_name = f"“{syllables[exp_i-1]}”" if syllables and exp_i and exp_i <= len(syllables) else ""
            feedback_parts.append(
                f"⚠️ 重音位置不对：“{word_text}”应该重读第{exp_i}个音节{exp_name}，你重读的是第{got_i}个。听示范发音再试一次。"
            )
        elif prosody_score is not None and prosody_score < 70:
            feedback_parts.append(
                f"⚠️ 重音或语调不太对（韵律 {prosody_score:.0f} 分）。听一遍示范发音，注意重音落在哪个音节上。"
            )

        # Overall performance
        if pronunciation_score >= FeedbackService.EXCELLENT_THRESHOLD:
            feedback_parts.append(f"“{word_text}”发音非常棒！🌟")
        elif pronunciation_score >= FeedbackService.GREAT_THRESHOLD:
            feedback_parts.append(f"“{word_text}”做得很好！你表现很出色。")
        elif pronunciation_score >= FeedbackService.GOOD_THRESHOLD:
            feedback_parts.append(f"“{word_text}”努力不错，你在进步！")
        elif pronunciation_score >= FeedbackService.OKAY_THRESHOLD:
            feedback_parts.append(f"“{word_text}”不错的尝试，继续练习！")
        else:
            feedback_parts.append(f"继续练习“{word_text}”，熟能生巧！")

        # Specific areas to improve
        areas_to_improve = []
        strengths = []

        if accuracy_score < FeedbackService.ACCURACY_LOW_THRESHOLD:
            areas_to_improve.append("发音准确度")
        elif accuracy_score >= FeedbackService.ACCURACY_HIGH_THRESHOLD:
            strengths.append("发音准确")

        if fluency_score < FeedbackService.FLUENCY_LOW_THRESHOLD:
            areas_to_improve.append("流利度与节奏")
        elif fluency_score >= FeedbackService.FLUENCY_HIGH_THRESHOLD:
            strengths.append("流畅度")

        if completeness_score < FeedbackService.COMPLETENESS_LOW_THRESHOLD:
            areas_to_improve.append("清晰完整地读出单词")
        elif completeness_score >= FeedbackService.COMPLETENESS_HIGH_THRESHOLD:
            strengths.append("清晰发音")

        # Add strengths
        if strengths:
            feedback_parts.append(f"优势：{', '.join(strengths)}。")

        # Add areas to improve
        if areas_to_improve:
            feedback_parts.append(f"需要重点提升：{', '.join(areas_to_improve)}。")

        # Phoneme-level feedback
        phoneme_feedback = FeedbackService._analyze_phonemes(assessment_result)
        if phoneme_feedback:
            feedback_parts.append(phoneme_feedback)

        # Encouragement and next steps
        if pronunciation_score < FeedbackService.GOOD_THRESHOLD:
            feedback_parts.append("💡 提示：听示范发音，尽量准确模仿每个音。")
        elif pronunciation_score < FeedbackService.ACCURACY_HIGH_THRESHOLD:
            feedback_parts.append("💡 提示：你很接近了！注意单词的重音和节奏。")
        else:
            feedback_parts.append("继续保持优秀表现！")

        feedback_text = " ".join(feedback_parts)

        return {
            "feedback_text": feedback_text,
            "grade": grade,
            "is_automated": True
        }

    @staticmethod
    def _calculate_grade(score: float) -> str:
        """Convert numerical score to letter grade"""
        if score >= FeedbackService.GRADE_A_PLUS_THRESHOLD:
            return "A+"
        elif score >= FeedbackService.GRADE_A_THRESHOLD:
            return "A"
        elif score >= FeedbackService.GRADE_A_MINUS_THRESHOLD:
            return "A-"
        elif score >= FeedbackService.GRADE_B_PLUS_THRESHOLD:
            return "B+"
        elif score >= FeedbackService.GRADE_B_THRESHOLD:
            return "B"
        elif score >= FeedbackService.GRADE_B_MINUS_THRESHOLD:
            return "B-"
        elif score >= FeedbackService.GRADE_C_PLUS_THRESHOLD:
            return "C+"
        elif score >= FeedbackService.GRADE_C_THRESHOLD:
            return "C"
        elif score >= FeedbackService.GRADE_C_MINUS_THRESHOLD:
            return "C-"
        elif score >= FeedbackService.GRADE_D_THRESHOLD:
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
                if phoneme_score < FeedbackService.PHONEME_PROBLEM_THRESHOLD:
                    phoneme_text = phoneme.get('phoneme', '').strip()
                    if phoneme_text and phoneme_text not in problem_phonemes:
                        problem_phonemes.append(phoneme_text)

        if problem_phonemes:
            # Limit to keep feedback concise
            problem_phonemes = problem_phonemes[:FeedbackService.MAX_PHONEME_FEEDBACK_COUNT]
            phoneme_list = ', '.join([f"/{p}/" for p in problem_phonemes])
            return f"请特别注意这些音素：{phoneme_list}。"

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

        return f"{automated_feedback}\n\n👨‍🏫 老师备注：{teacher_notes}"


# Singleton instance
feedback_service = FeedbackService()

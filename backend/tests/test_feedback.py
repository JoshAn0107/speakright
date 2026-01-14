"""
Simple test script to verify automated feedback generation
Run this to see example feedback without needing the full API
"""

from app.services.feedback_service import feedback_service

# Test case 1: Excellent pronunciation
print("=" * 60)
print("TEST 1: Excellent Pronunciation (Score: 95)")
print("=" * 60)

excellent_result = {
    "pronunciation_score": 95,
    "accuracy_score": 94,
    "fluency_score": 96,
    "completeness_score": 95,
    "words": [
        {
            "word": "beautiful",
            "phonemes": [
                {"phoneme": "b", "accuracy_score": 95},
                {"phoneme": "juː", "accuracy_score": 93},
                {"phoneme": "t", "accuracy_score": 94},
                {"phoneme": "ɪ", "accuracy_score": 96},
                {"phoneme": "f", "accuracy_score": 92},
                {"phoneme": "əl", "accuracy_score": 95}
            ]
        }
    ]
}

feedback1 = feedback_service.generate_feedback(excellent_result, "beautiful")
print(f"\nGrade: {feedback1['grade']}")
print(f"Feedback:\n{feedback1['feedback_text']}")
print(f"Automated: {feedback1['is_automated']}")

# Test case 2: Good pronunciation (needs improvement)
print("\n" + "=" * 60)
print("TEST 2: Good Pronunciation with Areas to Improve (Score: 75)")
print("=" * 60)

good_result = {
    "pronunciation_score": 75,
    "accuracy_score": 70,
    "fluency_score": 78,
    "completeness_score": 77,
    "words": [
        {
            "word": "comfortable",
            "phonemes": [
                {"phoneme": "k", "accuracy_score": 85},
                {"phoneme": "ʌ", "accuracy_score": 55},  # Problem phoneme
                {"phoneme": "m", "accuracy_score": 75},
                {"phoneme": "f", "accuracy_score": 58},  # Problem phoneme
                {"phoneme": "ə", "accuracy_score": 70},
                {"phoneme": "t", "accuracy_score": 80},
                {"phoneme": "ə", "accuracy_score": 72},
                {"phoneme": "b", "accuracy_score": 78},
                {"phoneme": "l", "accuracy_score": 50}   # Problem phoneme
            ]
        }
    ]
}

feedback2 = feedback_service.generate_feedback(good_result, "comfortable")
print(f"\nGrade: {feedback2['grade']}")
print(f"Feedback:\n{feedback2['feedback_text']}")
print(f"Automated: {feedback2['is_automated']}")

# Test case 3: Needs practice
print("\n" + "=" * 60)
print("TEST 3: Needs Practice (Score: 60)")
print("=" * 60)

needs_practice_result = {
    "pronunciation_score": 60,
    "accuracy_score": 55,
    "fluency_score": 62,
    "completeness_score": 65,
    "words": [
        {
            "word": "thorough",
            "phonemes": [
                {"phoneme": "θ", "accuracy_score": 45},  # Problem
                {"phoneme": "ɜː", "accuracy_score": 50}, # Problem
                {"phoneme": "r", "accuracy_score": 60},
                {"phoneme": "əʊ", "accuracy_score": 48}  # Problem
            ]
        }
    ]
}

feedback3 = feedback_service.generate_feedback(needs_practice_result, "thorough")
print(f"\nGrade: {feedback3['grade']}")
print(f"Feedback:\n{feedback3['feedback_text']}")
print(f"Automated: {feedback3['is_automated']}")

# Test case 4: Failing
print("\n" + "=" * 60)
print("TEST 4: Needs Significant Work (Score: 45)")
print("=" * 60)

failing_result = {
    "pronunciation_score": 45,
    "accuracy_score": 40,
    "fluency_score": 48,
    "completeness_score": 47,
    "words": [
        {
            "word": "pronunciation",
            "phonemes": [
                {"phoneme": "p", "accuracy_score": 50},
                {"phoneme": "r", "accuracy_score": 35},  # Problem
                {"phoneme": "ə", "accuracy_score": 42},
                {"phoneme": "n", "accuracy_score": 45}
            ]
        }
    ]
}

feedback4 = feedback_service.generate_feedback(failing_result, "pronunciation")
print(f"\nGrade: {feedback4['grade']}")
print(f"Feedback:\n{feedback4['feedback_text']}")
print(f"Automated: {feedback4['is_automated']}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
